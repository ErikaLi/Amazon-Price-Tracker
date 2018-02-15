"use strict";

function processUpdate(result) {
    alert(result.message);
    if (result.new) {
        $('#wanted_price').html(result.new_price);
    }
}

function getUpdateInfo(evt) {
    evt.preventDefault();

    var formInputs = {
        "new_threshold": $("#new_threshold").val(),
        "product_id": $("#product_id").val(),
    };

    $.post("/update", 
           formInputs,
           processUpdate);
}

$("#update_form").on("submit", getUpdateInfo);