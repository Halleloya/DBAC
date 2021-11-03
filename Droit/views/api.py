import json
import copy
from logging import Logger
import requests
import uuid
import re
import jwt
from flask import Blueprint, config, request, url_for, redirect, Response, make_response, jsonify, session, render_template
from flask import current_app as app
from flask_login import current_user as user
from py_abac import PDP, AccessRequest, Policy
from urllib.parse import urljoin, urlencode
from ..models import ThingDescription, DirectoryNameToURL, TypeToChildrenNames, TargetToChildName, LevelBoundingBox
from ..utils import get_target_url, is_json_request, clean_thing_description, add_policy_to_storage,\
    delete_policy_from_storage, is_policy_request, is_request_allowed, get_auth_attributes, set_auth_user_attr,\
    generate_jwt
from pymongo import MongoClient
from py_abac.storage.mongo import MongoStorage
from ..auth.models import auth_db, Policy
from datetime import datetime
from Droit.views import GeographyHelper

ERROR_JSON = {"error": "Invalid request."}
ERROR_POLICY = {"error": "Invalid policy."}
ERROR_NO_USER = {"error": "Please login."}
OPERATION_COUNT = ""

api = Blueprint('api', __name__)
level_details_cache = {}

def delete_local_thing_description(thing_id: str) -> bool:
    """Delete the thing description with the specific 'thing_id' in local directory and return whether the deletion is complete.

    This is the function that perform the real thing description deletion oepration. It will do it locally by deleting the 
    thing description specified by `thing_id` field. If the to-be-delete thing description has publicity larger than 1, it 
    will send addition request to its parent directory to totally remove the record. This is a recursive request and only
    until its finished, this function should return.

    Args:
        thing_id (str): ID for thing description to be deleted

    Return:
        bool: True if the deletion is complete, if any error happens in the whole prcesss, then return False
    """
    delete_thing = ThingDescription.objects(thing_id=thing_id).first()
    if delete_thing is None:
        return True

    delete_thing.delete()

    # 1. if the publicity is larger than 0, it needs to recursively delete the thing in parent's directory
    if delete_thing.publicity > 0:
        delete_up_things(delete_thing.thing_id)
    # 2. if current directory has no other thing_description of this type,
    # should update parent's aggregation information to delete this one
    dir_remaining_count = ThingDescription.objects(
        thing_type=delete_thing.thing_type).count()
    if dir_remaining_count == 0:
        delete_parent_aggregation(
            delete_thing.thing_type, app.config['HOST_NAME'])
    return True


def push_up_things(thing_description: dict, publicity: int) -> bool:
    """Send register request to parent directory, only if the publicity is larger than 0 and current directory has parent

    Args:
        thing_description (dict): the thing description may need to be pushed up
        publicity (int): how many levels the thing needs to be pushed up

    Return:
        bool: boolean value indicating the push up result. If succeed, return True, otherwise False
    """
    parent_directory = DirectoryNameToURL.objects(
        relationship='parent').first()
    # 1. only do push-up when the publicity is larger than 0, and it has parent
    if publicity == 0 or parent_directory is None:
        return True

    # 2. send push up request to the parent url
    parent_url = urljoin(app.config[parent_directory.directory_name] + parent_directory.url if parent_directory.directory_name in app.config else parent_directory.url, url_for('api.register'))
    request_data = {
        "td": thing_description,
        "location": parent_directory.directory_name,
        "publicity": publicity - 1
    }

    response = requests.post(parent_url, data=json.dumps(request_data), headers={
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8'
    })

    return response.status_code == 200


def delete_up_things(thing_id: str) -> bool:
    """Send delete request to parent's directory's /delete API, asking to delete the thing description.
    
    Args:
        thing_id (str): Unique identifer of thing description that specify the thing description to be deleted. 
    Return:
        bool: True if the deletion is complete, otherwise False.
    """
    parent_dir = DirectoryNameToURL.objects(relationship='parent').first()
    response = None
    if parent_dir is not None:
        query_parameters = urlencode(
            {"location": parent_dir.directory_name, "thing_id": thing_id})
        par_url = app.config[parent_dir.directory_name] + parent_dir.url if parent_dir.directory_name in app.config else parent_dir.url
        request_url = f"{urljoin(par_url, url_for('api.delete'))}?{query_parameters}"
        try:
            response = requests.delete(request_url)
        except:
            return False
    return response is None or response.status_code == 200


def add_parent_aggregation(thing_type: str, location: str) -> bool:
    """Send a post request to parent's directory to update the aggregation data.

    Args:
        thing_type(str): Specify the type of the aggregation.
        location(str): the directory name that the aggregation should be using to update.

    Returns:
        bool: True if the update is complete, otherwise False.
    :return: boolean value indicating the update result. return True if update successfully
    """

    parent_dir = DirectoryNameToURL.objects(relationship='parent').first()
    if parent_dir is None:
        return True

    request_body = {"location": location, "thing_type": thing_type}
    par_url = app.config[parent_dir.directory_name] + parent_dir.url if parent_dir.directory_name in app.config else parent_dir.url
    request_url = urljoin(par_url, url_for(
        'api.update_type_aggregation'))
    
    response = requests.post(request_url, data=json.dumps(request_body), headers={
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8'
    })

    return response.status_code == 200


def delete_parent_aggregation(thing_type: str, location: str) -> bool:
    """Send delete request to parent's [update_type_aggregation] API to update aggregation
    
    Args:
        thing_type (str): The thing type needs to be updated.
        location (str): Which directory name should be removed in the aggregation.

    Returns:
        bool: True when the delete aggregation operation is successful. Otherwise False.
    """
    # 1. if it has no parent directory, terminate the call
    parent_dir = DirectoryNameToURL.objects(relationship='parent').first()
    if parent_dir is None:
        return True
    query_parameters = urlencode(
        {"location": location, "thing_type": thing_type})
    par_url = app.config[parent_dir.directory_name] + parent_dir.url if parent_dir.directory_name in app.config else parent_dir.url
    request_url = f"{urljoin(par_url, url_for('api.update_type_aggregation'))}?{query_parameters}"
    try:
        response = requests.delete(request_url)
    except:
        return False

    return response == 200


def get_children_result(thing_type: str, api: str, query_string: str) -> list:
    """Get thing descriptions from all children directories and return the result

    This operation is done recursively using a DFS serach algorithm. The request is sent to the endpoint of
    children directory specified by `api` argument along with `query_string` as the query parameters. 
    If `thing_type` is specified, then only thing descriptions matching the `thing_type` argument is collected.
    
    Args:
        thing_type(str): Type of thing descriptions to return. Is this is missing, then no filtering will be doing.
        api(str): The API endpoint of the children directories.
        query_string(str): Query string of the of the requests sent to children directories.
    
    Returns:
        list: the list of thing descriptions that meet the filter condition. Each thing description is a dict object.
    """
    children_directories = DirectoryNameToURL.objects(
        relationship='child').all()
    # Get children names that contains only the 'thing_type' accroding to the aggregation stats
    descendant_names_with_type = TypeToChildrenNames.objects(thing_type=thing_type).first() \
        if thing_type is not None else TypeToChildrenNames.objects.first()
    descendant_to_child_mappings = TargetToChildName.objects().all()
    # Send request to each child node that has thing desciriptions with this [thing_type] and get result as a list
    result_list = []
    if children_directories is not None and descendant_names_with_type is not None:
        child_name_to_url_map = {
            child_directory.directory_name: child_directory.url for child_directory in children_directories
        }
        if descendant_to_child_mappings is not None:
            for mapping in descendant_to_child_mappings:
                child_name_to_url_map[mapping.target_name] = child_name_to_url_map[mapping.child_name]

        for descendant_directory_name in descendant_names_with_type.children_names:
            child_url = child_name_to_url_map[descendant_directory_name]
            para_dict = dict(k.split('=') for k in query_string.split('&'))
            if 'location' in para_dict.keys():
                # tmpstr = query_string.split('&', 1)[1]
                # new_query_string = f"location={descendant_directory_name}&{tmpstr}"
                para_dict['location'] = descendant_directory_name
                new_query_string = urlencode(para_dict)
                request_url = f"{urljoin(child_url, api)}?{new_query_string}"
            else:
                request_url = f"{urljoin(child_url, api)}?{query_string}"
            response = requests.get(request_url)
            if response.status_code != 200:
                continue
            child_result = response.json()
            if type(child_result) == list:
                result_list.extend(child_result)
            else:
                result_list.append(child_result)
    return result_list


@api.route('/register', methods=['POST'])
def register():
    """Register thing description at the target location. 

    If the current directory is the target location specified by `location` argument, the operation is processed locally
    Otherwise it will delegate the operation to the next possible directory (if there is ), and return whatever the result it receives
    
    In addition, an extra 'push-up' operation may be called if the publicity is larger than zero. It will send a new register request
    using the same thing description information to its parent directory with publicity decreased by one.
    
    Args:
        All of the following arguments are required and passed in the request URL.
        td (JSON str): the information of the thing description to be registered in JSON format
        location (str): the location where the thing description should be registered
        publicity (number): specify the number of levels that the thing description should be duplicate to upper level directory.
            By default this is zero, means it does not need to be pushed up.

    Returns:
        HTTP Response: if the register is completed, a simple success string with HTTP status code 200 is returned
            Otherwise a reason is returned in the response and HTTP status code is set to 400
    """

    # 1-2. check and parse input
    if not is_json_request(request, ["td", "location", "publicity"]):
        return jsonify(ERROR_JSON), 400
    body = request.get_json()
    location = body['location']
    thing_description = body['td']
    publicity = int(body['publicity']) if 'publicity' in body else 0
    headers = {
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8'
    }
    # 3. check if the location is current directory
    local_server_name = app.config['HOST_NAME'] if 'HOST_NAME' in app.config else "Unknown"
    if local_server_name == location:
        thing_description = clean_thing_description(thing_description)
        push_up_result = True
        aggregation_result = True
        registration_result = True
        # 3a. register locally
        # when this API is called by 'relocate', publicity is in the thing_description object
        # remove it to avoid duplicate key error when creating new object
        if "publicity" in thing_description:
            del thing_description["publicity"]
        
        new_td = ThingDescription(publicity=publicity, **thing_description)
        try:
            new_td.save()
        except Exception as e:
            registration_result = False

        # 3b. push up thing description and update parent directory's aggregation data
        push_up_result = push_up_things(thing_description, publicity)
        aggregation_result = add_parent_aggregation(
            thing_description["thing_type"], local_server_name)

        # 3c. return result
        if push_up_result and registration_result and aggregation_result:
            return make_response("Created", 200)
        else:
            return make_response("Register failed - Internal database error", 400)

    # otherwise, the request should be redirected to other directory
    register_api = url_for("api.register")

    target_url = get_target_url(location, register_api)

    # check if any of above condition is satisified
    if target_url is not None:
        master_response = requests.post(
            target_url, data=json.dumps(body), headers=headers)
        return make_response(master_response.reason, master_response.status_code)

    # Otherwise the input location is invalid, return
    return jsonify(ERROR_JSON), 400

@api.route('/policy', methods=['POST'])
def policy():
    """Register a new policy using the py_abac format. 
    
    Args:
        All of the following arguments are required and passed in the request URL.
        td (JSON str): the information of the policy to be registered in JSON format
        location (str): the location where the thing description should be registered

    Returns:
        HTTP Response: if the register is completed, a simple success string with HTTP status code 200 is returned
            Otherwise a reason is returned in the response and HTTP status code is set to 400
    """

    # 1-2. check and parse input
    if not is_json_request(request, ["td","location"]):
        return jsonify(ERROR_JSON), 400

    json = request.get_json()
    policy_json = json['td']
    location = json['location']
    # Does not allow customized uid, it should be auto generated by uuid
    if 'uid' in policy_json:
        return jsonify({'error': 'Cannot customize uid'})
    uid = str(uuid.uuid4())
    if not is_policy_request(policy_json, ["description", "effect", "rules", "targets", "priority"]):
        return jsonify(ERROR_POLICY), 400
    
    if not user.get_id():
        return jsonify(ERROR_NO_USER), 400
    policy_json['uid'] = uid
    if add_policy_to_storage(policy_json, location):
        new_policy = Policy(uid=uid,
                            location=location,
                            policy_json=str(policy_json),
                            user_id=int(user.get_user_id()))  # local policy register
        auth_db.session.add(new_policy)
        auth_db.session.commit()
        return make_response("Created Policy", 200)
    
    return jsonify(ERROR_JSON), 400


@api.route('/policy_attribute_auth', methods=['POST'])
def policy_attr_auth():
    if not is_json_request(request, ["thing_id", "thing_type", "action"]):
        return jsonify(ERROR_JSON), 400

    access_frequency = request.cookies.get('accessFrequency')
    request_json = request.get_json()
    thing_id = request_json['thing_id']
    policy_location = request_json['location']

    client = MongoClient()
    storage = MongoStorage(client, db_name=policy_location)
    add_user_scope = []
    add_server_scope = []
    add_user_scope_str = ""
    add_server_scope_str = ""
    for p in storage.get_for_target("", str(thing_id), ""):
        subject_rules = get_attr_list(p.rules.subject)
        context_rules = get_attr_list(p.rules.context)
        print("[API] (policy_attr_auth)")
        auth_attributes = get_auth_attributes()
        auth_user_attributes = auth_attributes[0]
        auth_server_attributes = auth_attributes[1]
        # initialize user attributes from profile info, if already exists
        if not auth_user_attributes["address"]:
            set_auth_user_attr("address", user.get_address())
        if not auth_user_attributes["phone_number"]:
            set_auth_user_attr("phone_number", user.get_phone())
        add_user_scope_str = get_auth_scopes(add_user_scope, subject_rules, auth_user_attributes)
        add_server_scope_str = get_auth_scopes(add_server_scope, context_rules, auth_server_attributes)
    print("add_user_scope_str: ", add_user_scope_str)
    print("add_server_scope_str: ", add_server_scope_str)

    # authorize and access the required attributes
    if len(add_user_scope_str) > 0 or len(add_server_scope_str) > 0:
        # initialize 'info_authorize' to zero to indicate authorization not yet started
        session['info_authorize'] = 0
        # pass scopes by session
        session['add_user_scope'] = add_user_scope_str
        session['add_server_scope'] = add_server_scope_str
        return url_for("auth.info_authorize"), 300

    return make_response("Request Succeed", 200)


def get_attr_list(policy_rules):
    if isinstance(policy_rules, list):
        rule_dict = {}
        for rule in policy_rules:
            rule_dict.update(rule)
        return rule_dict.keys()
    return policy_rules.keys()


@api.route('/policy_decision', methods=['POST'])
def policy_decision():
    """Determines whether a request is allowed or not

    Args:
        The function uses HTTP request directly. These argument must be contained in the request:
        thing_id (str): identification of the thing
        thing_type (str): type of the thing
        action (str): get,delete, or create

    Returns:
        success: HTTP response with a short string indicating of successfulness and status code 
        failure: user id and status code

    """
    if not is_json_request(request, ["thing_id", "thing_type", "action"]):
        return jsonify(ERROR_JSON), 400
    code = is_request_allowed(request)
    if code == 1:
        resp = make_response("Request Succeed", 200)
    elif code == 0:
        resp = jsonify({"id": user.get_id()}), 400
    
    #resp.set_cookie('accessFrequency', '1')
    return resp


def get_auth_scopes(auth_scope, attr_list, auth_attributes):
    for s in attr_list:
        attr_name = re.search("[a-zA-Z_]+", s).group().lower()
        if (attr_name not in auth_scope) and (attr_name in auth_attributes):
            if not auth_attributes.get(attr_name, None):
                auth_scope.append(attr_name)
    return " ".join(auth_scope)


@api.route('/delete_policy', methods=['POST'])
def delete_policy():
    """Delete a policy from storage and the database

    Args:
        The function uses HTTP request directly. These argument must be contained in the request:
        uid (str): uid of the policy
        location (str): location the policy is stored

    Returns:
        HTTP response with a short string indicating of successfulness and status code 

    """
    if delete_policy_from_storage(request):
        request_json = request.get_json()
        uid = request_json['uid']
        Policy.query.filter(Policy.uid==uid).delete()
        auth_db.session.commit()
        return make_response("Policy Deleted", 200)
    else:
        return make_response("Error Occured", 400)


@api.route('/update_aggregate', methods=['POST', 'DELETE'])
def update_type_aggregation():
    """Update local aggregation data when a thing is registered/deleted at any children directory

    If the current directory is the target location specified by `location` argument, the operation is processed locally
    Otherwise it will delegate the operation to the next possible directory (if there is ), and return whatever the result it receives

    Args:
        thing_type (str): the type of the thing description may need to be updated.
        location (str): specify where the update operation should be done.

    Returns:
        HTTP Response: a brief string explaining the result and corresponding HTTP status code.
            When the update finished, HTTP status code 200 will be return, otherwise 400.
    """
    if request.method == 'POST':
        if not is_json_request(request, ["location", "thing_type"]):
            return jsonify(ERROR_JSON), 400
        body = request.get_json()
        thing_type = body['thing_type']
        location = body['location']

        # 3. update database
        children_locations = TypeToChildrenNames.objects(
            thing_type=thing_type).first()
        # don't need to do any update
        if children_locations is not None and location in children_locations.children_names:
            return "No need to update", 200

        if children_locations is None:
            children_locations = TypeToChildrenNames(
                thing_type=thing_type, children_names=[location])
        elif location not in children_locations.children_names:
            children_locations.children_names.append(location)

        children_locations.save()
        # 4. recursively update the aggregation data at parent's directory
        add_parent_aggregation(thing_type, location)

    elif request.method == 'DELETE':
        location = request.args.get('location')
        thing_type = request.args.get('thing_type')
        if location is None or thing_type is None:
            return "Bad Request(arguments missing).", 400
        # delete location from the thing_type's aggregation list
        children_locations = TypeToChildrenNames.objects(
            thing_type=thing_type).first()
        if children_locations is not None:
            children_locations.children_names.remove(location)
            children_locations.save()
            # recursivly delete parent's aggregation data for the same record
            delete_parent_aggregation(thing_type, location)

    return make_response("Update aggregation data succesfully.", 200)


@api.route('/adjacent_directory')
def adjacent_directory():
    """Retured the neighbor(one-level apart) and master directory names and URIs of the current directory.

    Returns:
        HTTP Response: a list of directory information in JSON format with HTTP status 200
    """
    return jsonify(DirectoryNameToURL.objects().to_json()), 200


@api.route('/search', methods=['GET'])
def search():
    """Search the thing descriptions according to the conditions from the target directory and return all satisfying thing descriptions
    
    If the current directory is the target location specified by `location` argument, the operation is processed locally
    Otherwise it will delegate the operation to the next possible directory (if there is ), and return whatever the result it receives

    Args:
        location (str): specify the directory where the search operation should be performed. If this is missing, then the current location 
            and all of its descendant locations containing the thing descriptions will be searched.
        type (str): the type of the thing description. Only thing descriptions of this type will be returned. If this is missing, then there
            is no constraint on the type.
        id (str) : the unique thing id of the thing description. Only the thing description having this id will be returned. If this is missing,
            then there is no constraint on the id.

    Returns:
        HTTP Response: If the search operation is complete without error, a list of thing descriptions in JSON format is returned with HTTP code
            setting to 200. Otherwise a string description will be in the response body along with HTTP status code 400 is returned.
    """
    location = request.args.get('location')
    local_server_name = app.config['HOST_NAME'] if 'HOST_NAME' in app.config else "Unknown"
    request_query_string = urlencode(request.args)
    if not location or not location.strip():
        location = local_server_name
    else:
        location = location.strip()

    # 1. starting from current directory
    if location == local_server_name:
        thing_type = request.args.get('thing_type')
        thing_id = request.args.get('thing_id')
        
        # clean empty input string
        thing_type = None if not thing_type or not thing_type.strip() else thing_type.strip()
        thing_id = None if not thing_id or not thing_id.strip() else thing_id.strip()

        thing_list = []
        # 1. add result in current directory
        local_things = json.loads(ThingDescription.objects(thing_type=thing_type).to_json()) if thing_type is not None else \
            json.loads(ThingDescription.objects.to_json())

        if local_things is not None:
            thing_list.extend(local_things)

        # 2. get results from children's directory
        children_things = get_children_result(
            thing_type, url_for("api.search"), request_query_string)
        thing_list.extend(children_things)
        # 3. deduplicate by thing_id
        thing_id_set = set()
        result_list = []
        for thing in thing_list:
            if thing["thing_id"] not in thing_id_set and (thing_id is None or thing["thing_id"] == thing_id):
                thing_id_set.add(thing["thing_id"])
                result_list.append(thing)
        return jsonify(result_list), 200

    # 2. redirect to the target location
    target_url = get_target_url(location, url_for('api.search'))
    if target_url is None:
        return "Search failed", 400
    iterative = request.args.get('iterative')
    # if the request is 'iterative', it simply returns the redirect URL path
    # otherwise, it will send request on behalf of the caller to the URL
    if iterative:
        return target_url, 302
    else:
        request_url = f"{target_url}?{request_query_string}"
        print(request_url)
        try:
            response = requests.get(request_url)
        except:
            return "Search failed", 400

        if response.status_code == 200:
            return jsonify(response.json()), 200

    return "Search failed", 400


@api.route('/jwt', methods=['GET'])
def get_jwt():

    """Generate jwt of the requested thing with minimal inforamtion in the payload`

    Args:
        This method receive arguments from HTTP request body, which must be JSON format containing following properties
        thing_id (str): uniquely identify the thing description to be deleted
        Also, user must be logged in for username attribute.
    Returns:
        HTTP Response: The response is a jwt in JSON format with corresponding HTTP status code indicating the result
        if the deletion is performed succesfully, or there is no such thing description in the target directory,
        the deletion is complete with HTTP status code 200 being returned. Otherwise HTTP status code 400 is returned.
    """

    thing_id = request.args.get('thing_id')
    username = user.get_username()
    timestamp = datetime.now().timestamp()
    payload = {"thing_id": thing_id, "username": username, "timestamp": timestamp}
    if not thing_id:
        return "Invalid input", 400
    if not username:
        return "Please login", 400

    encoded_jwt, priv_key, pub_key = generate_jwt(payload)
    # TODO: save priv_key and pub_key in server

    jwt_json = payload.copy()
    jwt_json['encoding'] = str(encoded_jwt)
    return jsonify(jwt_json), 200
        

@api.route('/delete', methods=['DELETE'])
def delete():
    """Delete the thing description specified by `thing_id` argument and from directory specified by the argument `location`

    If the current directory is the target location specified by `location` argument, the operation is processed locally
    Otherwise it will delegate the operation to the next possible directory (if there is ), and return whatever the result it receives
    
    Args:
        This method receive arguments from HTTP request body, which must be JSON format containing following properties
        thing_id (str): uniquely identify the thing description to be deleted
        location (str): specify the location where the thing description located is
    Returns:
        HTTP Response: The response is a pure string HTTP response with corresponding HTTP status code indicating the result
        if the deletion is performed succesfully, or there is no such thing description in the target directory,
        the deletion is complete with HTTP status code 200 being returned. Otherwise HTTP status code 400 is returned.
    """

    location = request.args.get('location')
    thing_id = request.args.get('thing_id')
    if not location or not thing_id or not location.strip() or not location.strip():
        return ('', 200)

    location = location.strip()
    thing_id = thing_id.strip()
    local_server_name = app.config['HOST_NAME'] if 'HOST_NAME' in app.config else "Unknown"
    if location == local_server_name:
        delete_local_thing_description(thing_id)

        return "", 200

    # if not aiming at current directory, send a request to the correct target location
    target_url = get_target_url(location, url_for("api.delete"))
    if target_url is not None:
        request_url = f"{target_url}?{urlencode(request.args)}"
        try:
            response = requests.delete(request_url)
        except:
            return "", 400
        if response.status_code == 200:
            return "", 200

    return "", 400


@api.route('/relocate', methods=['POST'])
def relocate():
    """Relocate a thing specified by the `thing_id` from the location specified by `from` to the location specified by `to`

    If the current directory is the target location specified by `location` argument, the operation is processed locally
    Otherwise it will delegate the operation to the next possible directory (if there is ), and return whatever the result it receives

    This method performs search operation using the `thing_id` from the `from` directory
    Then the thing description is removed locally, followed by an insertion operation using the same thing description content in `to` directory
    
    Caution: Currently this two steps are not performed as one transaction, which means even if the second operation (insertion) failed, 
    the first operation (deletion) is already finished an irrevocable.

    Args:
        This method receive arguments from HTTP request body, which must be JSON format containing following properties
        thing_id (str): uniquely identify the thing description to be relocated
        from (str): specify the location where the thing description located is
        to (str): specify the location that the thing description should be relocated to

    Returns:
        HTTP Response: The response is a pure string HTTP response with corresponding HTTP status code indicating the result
        if the relocation operation is completed, 200 is returned. Otherwise 400 is returned.
    """
    if not is_json_request(request, ["thing_id", "from", "to"]):
        return jsonify(ERROR_JSON), 400
    body = request.get_json()
    thing_id = body['thing_id']
    from_location = body['from']
    to_location = body['to']

    headers = {
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8'
    }

    local_server_name = app.config['HOST_NAME'] if 'HOST_NAME' in app.config else "Unknown"
    if local_server_name == from_location:
        relocate_thing = ThingDescription.objects(thing_id=thing_id).first()
        target_url = get_target_url(to_location, url_for("api.register"))
        if relocate_thing is None or target_url is None:
            return jsonify(ERROR_JSON), 400
        # 1. insert this thing description at 'to_location'
        request_data = {
            "td": json.loads(relocate_thing.to_json()),
            "location": to_location,
            "publicity": relocate_thing.publicity
        }
        try:
            response = requests.post(
                target_url, data=json.dumps(request_data), headers=headers)
            pass
        except:
            return "Relocate failed", 400
        # 2. delete this thing description at 'from_location'
        delete_local_thing_description(thing_id)

        return "", 200

    # delegate the request to other directory
    request_url = get_target_url(from_location, url_for("api.relocate"))
    if request_url is None:
        return "Request failed", 400
    try:
        response = requests.post(
            request_url, data=json.dumps(body), headers=headers)
    except:
        return "Request failed", 400

    return "", response.status_code


def deduplicate_by_id(thing_list):
    """Deduplicate the thing description list according to its 'thing_id' field

    Args:
        thing_list (list): the list of thing description
    Returns:
        list: the deduplicated thing description list
    """
    thing_ids = set()
    unique_thing_list = []
    for thing in thing_list:
        if thing["thing_id"] not in thing_ids:
            thing_ids.add(thing["thing_id"])
            unique_thing_list.append(thing)
    return unique_thing_list

def get_data_field(thing_description, data_field_list):
    """Get the field specified by 'data_field_list' from each thing description

    Args:
        data_field_list(list): list of str that specified the hierarchical field names
            For example, if the parameter value is ['foo', 'bar', 'foobar'], then this
            function will try to get thing_description['foo']['bar']['foobar'] and return the value
            If any of the field does not exist, an error will occur
    Returns:
        object: the content specified by the data field
    """
    for data_field in data_field_list:
        thing_description = thing_description[data_field]
    return thing_description

def get_compressed_list(thing_list, operation, data_field):
    """Get a compressed version of thing list input, keeping only thing_id and 'data_field'

    Args:
        thing_list(list): the list of thing description
        operation(str): one of the five aggregation operations
        data_field(str): property names. If it contains hierarchical property, then seperate each part using dot '.'

    Returns:
        list: compressed version of the input thing list
    """
    if operation == "COUNT":
        return list(map(lambda item: {"thing_id" : item["thing_id"]}, thing_list))


    data_field_list = data_field.split(".")
    def compress_function(thing_description):
        return_thing_desc = {"thing_id" : thing_description["thing_id"]}
        try:
            return_thing_desc["_query_data"] = thing_description["_query_data"] if "_query_data" in thing_description else get_data_field(thing_description, data_field_list)
        except:
            return None

        return return_thing_desc

    return list(filter(lambda item: item is not None, map(compress_function, thing_list)))

def get_final_aggregation(thing_list, operation):
    """Generate the HTTP response content according to the operation and the result thing list

    Args:
        thing_list(list): the list of thing description
        operation(str): one of the five aggregation operations

    Returns:
        dict: formatted result containing the aggregation data
    """
    if operation != "COUNT" and len(thing_list) == 0:
        return {"operation": operation, "result": "unknown"}

    result = {"operation": operation}
    if operation == "COUNT":
        result["result"] = len(thing_list)
    elif operation == "MIN":
        result["result"] = min([thing_description["_query_data"] for thing_description in thing_list])
    elif operation == "MAX":
        result["result"] = max([thing_description["_query_data"] for thing_description in thing_list])
    elif operation == "AVG":
        result["result"] = sum([thing_description["_query_data"] for thing_description in thing_list]) / len(thing_list)
    elif operation == "SUM":
        result["result"] = sum([thing_description["_query_data"] for thing_description in thing_list])
    return result

@api.route('/custom_query', methods=['GET'])
def custom_query():
    """Return all thing descriptions from the target directory and its descandant directories that satisfy the filter conditions

    Args:
        operation (str):
        type (str):
        data (str):
        location (str): optional, specify the root directory to be searched. 
        filter (JSON str): 
    Returns:
        HTTP Response:
    """
    script = request.args.get('data')
    stop_recurse = request.args.get('stop_recurse') == 'True'
    try:
        script_json = json.loads(script)
    except:
        return jsonify({"error": "Invalid input format"}), 400
    
    SCRIPT_OPERATION = ["SUM", "AVG", "MIN", "MAX", "COUNT"]  # Allowed operation of the customized script query

    # check input combination: type and operation are required
    if "operation" not in script_json or "type" not in script_json or type(script_json["operation"]) != str:
        return jsonify(ERROR_JSON), 400
    
    script_json["operation"] = script_json["operation"].upper()
    
    if script_json["operation"] not in SCRIPT_OPERATION or (script_json["operation"] != "COUNT" and "data" not in script_json):
        return jsonify(ERROR_JSON), 400

    # 2. Clean parameters
    local_server_name = app.config['HOST_NAME'] if 'HOST_NAME' in app.config else "Unknown"
    location = local_server_name if "location" not in script_json else script_json["location"].strip()
    # the filters itself is a dictionary, in order to manipulate(delete/udpate) items in the filter
    # here must be a deepcopy rather than a merely reference to the filed in script_json
    filters = copy.deepcopy(script_json["filter"]) if "filter" in script_json else {}
    data_field = script_json["data"] if "data" in script_json else None

    # 3. filter result.
    if location == local_server_name:
        operation = script_json["operation"].strip()
        thing_type = script_json["type"].strip()
        
        filter_map = {}
        # add geographical filter condition
        if "polygon" in filters and type(filters["polygon"]) == list and len(filters["polygon"]) >= 3:
            # properties__geo__coordinates represents field properties.geo.coordinates
            # geo_within_polygon: query string for geospatial query
            filter_map["properties__geo__coordinates__geo_within_polygon"] = filters.pop("polygon")
            # An example of mongodb query is: db.td.find({ "properties.geo.coordinates": { $geoWithin: {$polygon: [[-75,40],[-75,41],[-70,41],[-70,40]]}}})
        
        for filter_name in filters:
            filter_map[filter_name.replace(".", "__")] = filters[filter_name]

        try:
            thing_list = json.loads(ThingDescription.objects(thing_type=thing_type, **filter_map).to_json())
        except:
            return jsonify({"reason": "filter condition error."}), 400

        if stop_recurse:
            compressed_thing_list = get_compressed_list(thing_list, operation, data_field)
            return jsonify(compressed_thing_list), 200

        # 3a). Instead of a recursive search which queries all directories
        # We can search only relevant directories. Each directory
        # has a bounding box defined. We query only those directories which
        # intersects with the input parameter polygon.
        query_polygon = filter_map["properties__geo__coordinates__geo_within_polygon"]
        if  len(query_polygon) > 0:
            #query has a polygon search criteria
            is_sub_dir = "_sub_dir" in script_json
            script_json["_sub_dir"] = True  # Give hint to children directory
            # delete the "location" field in the query string, then each children will treat themselves as the target dir
            if "location" in script_json:
                del script_json["location"]
            children_result_list = get_children_in_bbox_result(thing_type, url_for(
                "api.custom_query"), f"data={json.dumps(script_json)}", query_polygon)
            if children_result_list != None:
                thing_list.extend(children_result_list)
            thing_list = deduplicate_by_id(thing_list)
            #
            # [{id, properties, ..., ..}, {id, propertis..}, {}, {}]
            # COUNT: [{id1}, {id2}, {id3}, ...]
            # MIN,MAX,SUM,AVG: [{id, data: a}, {id, data: b}]
            compressed_thing_list = get_compressed_list(thing_list, operation, data_field)

            # 4. return data
            # return the aggregation result if current directory is the root
            # otherwise return the compressed list
            if not is_sub_dir:
                return jsonify(get_final_aggregation(compressed_thing_list, operation)), 200
            else:
                return jsonify(compressed_thing_list), 200
        else:
            # 3b. get children result.
            # "_sub_dir" field checks whether current directory is a recursive node
            # if this field is true, which means the request must return a compressed thing list results
            # otherwise, return the final aggregation result
            is_sub_dir = "_sub_dir" in script_json
            script_json["_sub_dir"] = True  # Give hint to children directory
            # delete the "location" field in the query string, then each children will treat themselves as the target dir
            if "location" in script_json:
                del script_json["location"]
            children_result_list = get_children_result(thing_type, url_for(
                "api.custom_query"), f"data={json.dumps(script_json)}")
            thing_list.extend(children_result_list)
            thing_list = deduplicate_by_id(thing_list)
            #
            # [{id, properties, ..., ..}, {id, propertis..}, {}, {}]
            # COUNT: [{id1}, {id2}, {id3}, ...]
            # MIN,MAX,SUM,AVG: [{id, data: a}, {id, data: b}]
            compressed_thing_list = get_compressed_list(thing_list, operation, data_field)

            # 4. return data
            # return the aggregation result if current directory is the root
            # otherwise return the compressed list
            if not is_sub_dir:
                return jsonify(get_final_aggregation(compressed_thing_list, operation)), 200
            else:
                return jsonify(compressed_thing_list), 200

    # when location is not here, delegate to other directories
    request_url = get_target_url(
        script_json["location"], url_for("api.custom_query"))
    if request_url is None:
        return jsonify("Request failed(location does not exist.)"), 400
    try:
        response = requests.get(f"{request_url}?data={script}")
    except:
        return jsonify("Request failed(target location is not running.)"), 400

    if response.status_code == 200:
        return jsonify(response.json()), 200

    return jsonify("Request failed(from other location)"), 400

      
@api.route('/dfs_level_details', methods=['GET'])
def dfs_level_details():
    """This function traverses all levels in a DFS style. It gets the child directories and
    recursively calls the same function on child directories to extract its level details

    Returns:
        Dictionary: Key is the level name, value is a list with first element as url
        and the second element as the bounding box of that url
    """
    level_details = {}
    local_server_name = app.config['HOST_NAME'] if 'HOST_NAME' in app.config else "Unknown"
    try:
        bounding_box_level = GeographyHelper.GetCoordinatesForLevel(local_server_name)
    except:
        print("An error has occured while retrieveing bounding box")
        bounding_box_level = None
    level_details[local_server_name] = [request.url_root, bounding_box_level]
    locations_to_urls = DirectoryNameToURL.objects(relationship='child').all()
    if locations_to_urls == None:
        return None
    for location_to_url in locations_to_urls:
        loc_url = app.config[location_to_url.directory_name] + location_to_url.url if location_to_url.directory_name in app.config else location_to_url.url
        request_url = urljoin(loc_url, url_for('api.dfs_level_details'))
        try:
            response = requests.get(request_url)
            if response.status_code != 200:
                return jsonify(response.json()), response.status_code
            results = response.json()
            if results == None or len(results) == 0:
                continue
            for result in results:
                level_details[result] = results[result]
        except:
            return jsonify(ERROR_JSON), 400
    return jsonify(level_details), 200


def get_all_level_details():
    """This function traverses all the levels in DFS style.
    We start from the master node and traverse till the root node

    Returns:
        Dictionary: Key is the level name, value is a list with first element as url
        and the second element as the bounding box of that url
    """
    global level_details_cache
    if len(level_details_cache) > 0:
        return level_details_cache
    location_to_url = DirectoryNameToURL.objects(relationship='master').first()
    if "level" in app.config:
        location_to_url = app.config[location_to_url.directory_name]
    request_url = urljoin(location_to_url, url_for('api.dfs_level_details'))
    try:
        response = requests.get(request_url)
        if response.status_code != 200:
            return
        result = response.json()
        level_details_cache = copy.deepcopy(result)
        return result
    except:
        return None

      
def get_children_in_bbox_result(thing_type: str, api: str, query_string: str, query_polygon: list) -> list:
    """Get thing descriptions from directories that has its location intersecting with the bounding box and return the result

    First we get all the child directories that intersects with the input query location. The request is sent to the endpoint of
    children directory specified by `api` argument along with `query_string` as the query parameters. 
    If `thing_type` is specified, then only thing descriptions matching the `thing_type` argument is collected.

    Args:
        thing_type(str): Type of thing descriptions to return. Is this is missing, then no filtering will be done.
        api(str): The API endpoint of the children directories.
        query_string(str): Query string of the requests sent to children directories.
        query_polygon(list): Polygon list

    Returns:
        list: the list of thing descriptions that meet the filter condition. Each thing description is a dict object.
    """
    result_list = []
    all_level_details = get_all_level_details()
    if all_level_details == None:
        return None

    #Filter only those levels which intersect with the query polygon
    for descendant_directory_name in all_level_details:
        #all_level_details is a dictionary with level name as the key
        #value is a list with first element as the url
        #and second element is the bounding box
        intersection = GeographyHelper.GetIntersectionForBoundingBoxCoordinates(descendant_directory_name, \
        all_level_details[descendant_directory_name][1], query_polygon)
        if intersection == None:
            continue

        child_url = all_level_details[descendant_directory_name][0]
        para_dict = dict(k.split('=') for k in query_string.split('&'))
        if 'location' in para_dict.keys():
            tmpstr = query_string.split('&', 1)[1]
            new_query_string = f"location={descendant_directory_name}&{tmpstr}"
            para_dict['location'] = descendant_directory_name
            new_query_string = urlencode(para_dict)
            request_url = f"{urljoin(child_url, api)}?{new_query_string}"
        else:
            para_dict['stop_recurse'] = True
            try:
                filter_json = para_dict['data']
                filter_dict = json.loads(filter_json)
                #Optimization : Search for things only in the intersection region
                intersection_coords = GeographyHelper.GeoCoordinatesFromPolygon(intersection)
                filter_dict['filter']['polygon'] = intersection_coords
                para_dict['data'] = json.dumps(filter_dict)
            except KeyError:
                print('Key not found')
            new_query_string = urlencode(para_dict)
            request_url = f"{urljoin(child_url, api)}?{new_query_string}"
        response = requests.get(request_url)
        if response.status_code != 200:
            continue
        child_result = response.json()
        if type(child_result) == list:
            result_list.extend(child_result)
        else:
            result_list.append(child_result)
    return result_list
