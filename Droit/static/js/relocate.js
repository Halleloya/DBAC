$("#relocate-btn").click(function () {
    let from_location = $("#from_location").val().trim();
    let to_location = $("#to_location").val().trim();
    let thing_id = $("#thing_id").val().trim();
    if (from_location.length == 0 || to_location.length == 0 || thing_id.length == 0) {
        show_prompt("Please Filled All Input Fields", title = 'Alert');
        return;
    }

    /** Send asynchronous request to delete the thing description */
    lock_btn($(this));

    fetch(RELOCATE_API, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            thing_id: thing_id,
            from: from_location,
            to: to_location
        })
    }).then(response => {
        show_prompt('Relocation Succeed!');
        unlock_btn($(this));
    }).catch(response => {
        show_prompt('Relocation Failed...');
        unlock_btn($(this));
    });
});
