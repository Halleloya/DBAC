$("#delete-btn").click(function () {
    let location = $("#location").val();
    let thing_id = $("#thing_id").val();

    // Check input not empty
    if (location.trim().length == 0 || thing_id.trim().length == 0) {
        show_prompt("Please Filled All Input Fields", title = 'Alert');
        return;
    }

    /** Send asynchronous request to delete the thing description */
    lock_btn($(this));
    deleted_msg = true; // hide redundant thing deleted notification
    fetch(`${DELETE_API}?${$(".delete-form").serialize()}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        show_prompt('Deleted!<br>');
        unlock_btn($(this));
    }).catch(response => {
        show_prompt('Delete Failed.');
        unlock_btn($(this));
    });


});


