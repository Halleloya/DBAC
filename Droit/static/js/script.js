// Set initial placeholder for the script
const exampleFilterScript =
`{
    "location": "level1",
    "operation": "COUNT",
    "type": "bus",
    "data": "temperature",
    "filter": {
        "polygon": [[-75, 40], [-75, 41],[-74, 41], [-74, 40] ],
        "properties.status.description": "running or not? not important"
    }
}`;
const jsonFormatter = new JSONFormatter("json-query-script", true);
jsonFormatter.setJSONString(exampleFilterScript);

const validOperation = ["SUM", "AVG", "COUNT", "MAX", "MIN"];

$("#search").click(async function () {

    // 1. Check JSON Format
    if (jsonFormatter.getJSONString() == null) {
        show_prompt("Please input valid script format (JSON).");
        return;
    }

    // 2. Check must-have property names
    let scriptJson = JSON.parse(jsonFormatter.getJSONString());
    if (!("location" in scriptJson) || !("operation" in scriptJson)
        || !("type" in scriptJson)) {
        show_prompt("Script must have [location], [operation], and [type] properties.");
        return;
    }
    if (typeof scriptJson.operation !== "string" || !(validOperation.includes(scriptJson.operation.toUpperCase()))) {
        show_prompt("[operation] value must be one of the following values:" + validOperation + ".");
        return;
    }
    scriptJson.operation = scriptJson.operation.toUpperCase();

    // 3. Check valid combination of operation
    if (scriptJson.operation !== "COUNT" && !("data" in scriptJson)) {
        show_prompt("Must specify the [data] field to aggregate.");
        return;
    }

    // 4. Send Asynchronous Query
    const $resultContainer = $('.result');
    $resultContainer.hide();
    lock_btn($(this));
    let inputScript = jsonFormatter.getJSONString();
    await fetch(`${SCRIPT_API}?data=${inputScript}`)
        .then(response => response.json())
        // 5. Render the result
        .then(data => {
            $resultContainer.show();
            $tableBody = $(".result table tbody");
            $tableBody.html("");
            $tableBody.append(`<tr><td>${scriptJson.operation}</td><td>${data["result"]}</td></tr>`)
            unlock_btn($(this));
        })
        .catch(response => {
            show_prompt('Search failed, please try again using valid input');
            console.log(response)
            unlock_btn($(this));
            return;     // Stop before creating notification
        })
});