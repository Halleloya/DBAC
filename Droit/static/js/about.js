$(".policy_table").on("click", ".delete_policy", function () {
    uid = $(this).closest('tr').children('td.uid').text();
    loc = $(this).closest('tr').children('td.location').text();
    let delete_button = $(this);
    lock_btn(delete_button);
    $.ajax({
        url: POLICY_DELETION_URL,
        type: "POST",
        data: JSON.stringify({"uid" : uid.trim(),
                "location": loc.trim()}),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn(delete_button);
            show_prompt("Request Failed")
        },
        success: function (data, textStatus, jqXHR) {
            show_prompt("Policy Deleted")
            window.location.reload()
        }
    });
    unlock_btn(delete_button);
}); 