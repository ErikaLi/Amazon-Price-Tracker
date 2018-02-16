"use strict";

function processChange(result) {
    alert(result.message);
    if (result.redirect) {
        window.location.href = result.redirect_url;
    }

    if (result.empty_password) {
        $('#new_password').val('');
        $('#new_password1').val('');
        $('#old_password').val('');
    }
}

function getPasswordInfo(evt) {
    evt.preventDefault();

    var formInputs = {
        "old_password": $("#old_password").val(),
        "new_password": $("#new_password").val(),
        "new_password1": $("#new_password1").val(),
    };

    $.post("/change_password", 
           formInputs,
           processChange);
}

$("#changeForm").on("submit", getPasswordInfo);