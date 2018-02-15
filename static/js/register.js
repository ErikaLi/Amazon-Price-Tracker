"use strict";

function processRegister(result) {
    alert(result.message);
    if (result.redirect) {
        window.location.href = result.redirect_url;
    }

    if (result.empty_password) {
        $('#password').val('');
        $('#password1').val('');
    }
}

function getRegisterInfo(evt) {
    evt.preventDefault();

    var formInputs = {
        "fname": $("#fname").val(),
        "lname": $("#lname").val(),
        "email": $("#email").val(),
        "phone": $("#phone").val(),
        "password": $("#password").val(),
        "password1": $("#password1").val(),
    };

    $.post("/register", 
           formInputs,
           processRegister);
}

$("#regForm").on("submit", getRegisterInfo);