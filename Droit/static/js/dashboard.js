var REGISTER_URL = '/api/register';
var POLICY_URL = '/api/policy';
var POLICY_DECISION_URL = '/api/policy_decision';
var ATTRIBUTE_AUTH_URL = '/api/policy_attribute_auth'
var POLICY_DELETION_URL = '/api/delete_policy';
var JWT_API = '/api/jwt';
var SEARCH_API = '/api/search';
var DELETE_API = '/api/delete';
var RELOCATE_API = '/api/relocate';
var SCRIPT_API = '/api/custom_query';

// to avoid redundant prompt messages
let deleted_msg = false;
let added_msg = false;

const lock_btn = function ($button) {
    $button.prop("disabled", true);
}

const unlock_btn = function ($button) {
    $button.prop("disabled", false);
}

const show_prompt = function (text, title = 'Result') {
    $("#modal").modal('show').find(".modal-body").text(text).end()
    .find(".modal-title").text(title);
}

/**
 * Encapsulated object for rendering JSON with format and color
 * it maintains the JSON container object and a json Editor object used to render JSON
 * 
 * users can use getJSONString to get access to the valid JSON string, or null if this value is never set
 * setJSONString method is used to update the JSON content, and refresh the rendering part
 */
class JSONFormatter {
    constructor(containerID, editable = true) {
        this.$container = $(`#${containerID}`)
        this.$jsonEditor = new JsonEditor(`#${containerID}`)

        // only store valid JSON string
        this.jsonString = null
        this.jsonHTML = null
        if (!editable) {
            // Make the JSON formatter readonly
            this.$container.on("input", e => this.$container.html(this.jsonHTML));
        } else {
            // Format the container when the focus changes
            this.$container.on("blur", e => this.setJSONString(this.$container.text()));
        }
    }

    getJSONString() {
        return this.jsonString
    }

    setJSONString(text) {
        let jsonObj = null;
        try {
            jsonObj = JSON.parse(text)
        } catch {
            return false
        }
        this.$jsonEditor.load(jsonObj)
        this.jsonString = text
        this.jsonHTML = this.$container.html()
        return true;
    }
}