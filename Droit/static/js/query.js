const request_jsonFormatter = new JSONFormatter("json-thingdescription", false)
const $tdModal = $("#thing_description_modal");
const jwt_jsonFormatter = new JSONFormatter("json-jwt", false)
const $jwtModal = $("#jwt_modal");
var searched_location
var things = {}

// Show thing details
$(".result table tbody").on("click", ".request", function () {
    let thingDescription = things[$(this).closest('tr').find("td.thing_id").text().trim()];
    request_jsonFormatter.setJSONString(thingDescription);
    console.log(thingDescription)
    let requestBtn = $(this)

    action = 'get' //currently considering only get requests

    thing_json = JSON.parse(thingDescription)
    thing_json['action'] = action
    thing_json['location'] = searched_location

    lock_btn(requestBtn);
    $.ajax({
        url: POLICY_DECISION_URL,
        type: "POST",
        data: JSON.stringify(thing_json),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn(requestBtn);
            if(jqXHR.status == 300){
                window.location.href=jqXHR.responseText;
            }else{
                show_prompt("Access denied")
            }
                
        },
        success: function (data, textStatus, jqXHR) {
            unlock_btn(requestBtn);
            $tdModal.modal('show');
        }
    });
    unlock_btn(requestBtn);
});

// Authorize attributes for a thing
$(".result table tbody").on("click", ".authorize", function () {
    let thingDescription = things[$(this).closest('tr').find("td.thing_id").text().trim()];
    let requestBtn = $(this)
    action = 'get' //currently considering only get requests
    thing_json = JSON.parse(thingDescription)
    thing_json['action'] = action
    thing_json['location'] = searched_location

    lock_btn(requestBtn);
    $.ajax({
        url: ATTRIBUTE_AUTH_URL,
        type: "POST",
        data: JSON.stringify(thing_json),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn(requestBtn);
            if (jqXHR.status == 300) {
                window.location.href=jqXHR.responseText;
            } else {
                show_prompt("Authorization failed")
            }
        },
        success: function (data, textStatus, jqXHR) {
            unlock_btn(requestBtn);
            show_prompt("No attribute authorization required")
        }
    });
    unlock_btn(requestBtn);
});


$(".result table tbody").on("click", ".jwt", function () {
    let thingDescription = things[$(this).closest('tr').find("td.thing_id").text().trim()];
    thing_json = JSON.parse(thingDescription)
    thing_json['location'] = searched_location
    action = 'get' //currently considering only get requests
    thing_json['action'] = action
    lock_btn($(this));

    // First check if user is authorized to access
    $.ajax({
        url: POLICY_DECISION_URL,
        type: "POST",
        data: JSON.stringify(thing_json),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn(requestBtn);
            if(jqXHR.status == 300){
                window.location.href=jqXHR.responseText;
            }else{
                show_prompt("Access denied")
            }
                
        },
        success: function (data, textStatus, jqXHR) {
            thing_id = thing_json['thing_id']
            request_url = `${JWT_API}?thing_id=${thing_id}`
            // return jwt is access granted
            fetch(request_url)
                .then(response => response.json())
                .then(data => {
                    // Show result list 
                    jwt_jsonFormatter.setJSONString(JSON.stringify(data));
                    $jwtModal.modal('show')
                    unlock_btn($(this));
                })
                .catch(response => {
                    show_prompt('Request failed' + response);
                    unlock_btn($(this));
                });
        }
    });
    unlock_btn($(this));
});

// Register click event for the 'search' button
$("#search").click(async function () {
    let form_data = $(".register-form").serialize();
    var form_data_array = {};
    $.each($('.register-form').serializeArray(), function(i, field) {
        form_data_array[field.name] = field.value;
    });
    searched_location = form_data_array['location'];
    let request_url = `${SEARCH_API}?${form_data}`;

    // Send asynchronous get request for the query
    let $resultContainer = $('.result');
    $resultContainer.hide();
    lock_btn($(this));

    await fetch(request_url)
        .then(response => response.json())
        .then(data => {
            // Show result list 
            $resultContainer.show();
            // render each thing description
            $tableBody = $(".result table tbody");
            $tableBody.html("");
            data.forEach(element => {
                $tableBody.append(`<tr>
                <td class="thing_id">${element.thing_id}</td>
                <td>${element.thing_type}</td>
                <td>${element.title}</td>
                <td>
                    <button class="btn btn-primary authorize">Authorize</button>
                </td>
                <td>
                    <button class="btn btn-primary request">Request</button>
                </td>
                <td>
                    <button class="btn btn-primary jwt">Generate</button>
                </td>
                </tr>`);
                things[element.thing_id] = JSON.stringify(element)
            });
            unlock_btn($(this));
        })
        .catch(response => {
            console.log(response);
            show_prompt('Search failed, please try again using valid input');
            unlock_btn($(this));
        });
});