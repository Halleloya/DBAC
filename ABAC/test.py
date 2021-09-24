from py_abac import PDP, Policy, AccessRequest
from py_abac.pdp import EvaluationAlgorithm
from py_abac.storage.mongo.storage import MongoStorage
from pymongo.mongo_client import MongoClient
client = MongoClient()
# Setup policy storage
storage = MongoStorage(client)
if storage.get('1'):
    print("removed 1")
    storage.delete('1')
if storage.get('2'):
    print("removed 2")
    storage.delete('2')
if storage.get('3'):
    print("removed 3")
    storage.delete('3')
if storage.get('4'):
    print("removed 4")
    storage.delete('4')

# Add policy to storage

# Policy definition in JSON
policy_json = {
    "uid": "1",
    "description": "Allow only ryan-liang@qq.com to access.",
    "effect": "allow",
    "rules": {
        "subject": [{"$.email": {"condition": "Equals", "value": "ryan-liang@qq.com"}}],
        "resource": {"id": {"condition": "RegexMatch", "value": ".*"}},
        "action": [{"$.method": {"condition": "Equals", "value": "create"}},
                   {"$.method": {"condition": "Equals", "value": "delete"}},
                   {"$.method": {"condition": "Equals", "value": "get"}}],
        "context": {}
    },
    "targets": {},
    "priority": 1
}

# Parse JSON and create policy object
policy = Policy.from_json(policy_json)

storage.add(policy)

# Add second policy
policy_json = {
    "uid": "2",
    "description": "Allow everyone to access.",
    "effect": "deny",
    "rules": {
        "subject": [{"id": {"condition": "RegexMatch", "value": ".*"}}],
        "resource": {"id": {"condition": "RegexMatch", "value": ".*"}},
        "action": [{"$.method": {"condition": "Equals", "value": "create"}},
                   {"$.method": {"condition": "Equals", "value": "delete"}},
                   {"$.method": {"condition": "Equals", "value": "get"}}],
        "context": {}
    },
    "targets": {},
    "priority": 0
}
policy = Policy.from_json(policy_json)
# Add policy to storage
storage.add(policy)



# Create policy decision point
pdp = PDP(storage,EvaluationAlgorithm.HIGHEST_PRIORITY)

# A sample access request JSON
user_id = 1
user_email = "ryan-liang@qq.com"
thing_id = "ziuboq12312"
request_json = {
        "subject": {
            "id": str(user_id), 
            "attributes": {"email": str(user_email)}
        },
        "resource": {
            "id": str(thing_id), 
            "attributes": {"thing_id": str(thing_id)}
        },
        "action": {
            "id": "", 
            "attributes": {"method": "get"}
        },
        "context": {
        }
    }
# Parse JSON and create access request object
request = AccessRequest.from_json(request_json)

# Check if access request is allowed. Evaluates to True since 
# Max is allowed to get any resource when client IP matches.
print(pdp.is_allowed(request))