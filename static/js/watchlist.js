"use strict";

function processUpdate(result) {
    console.log(result)
    alert(result.message);
    if (result.new) {
        let newPrice = +result.new_price
        $('#wanted_price').html(newPrice.toFixed(2));
    }
    if (result.empty) {
        $('#new_threshold').val('');
    }
}

function getUpdateInfo(evt) {
    evt.preventDefault();

    var formInputs = {
        "new_threshold": $("#new_threshold").val(),
        "product_id": $("#product_id_update").val(),
    };

    $.post("/update", 
           formInputs,
           processUpdate);
}

function processRemoval(result) {
    alert(result.message)
    $('#'+result.product_id).hide()
}


function deleteItem(evt) {
    evt.preventDefault();

    var id = evt.currentTarget.id.replace("remove_item", "")

    var formInputs = {
        "product_id": id,
    };

    $.post("/remove", 
           formInputs,
           processRemoval);

}

// functions to handle add item on the same page without redirecting
// function processAddItem(result) {
//     // jquery create dom element li, with id result.id
//     // jquery to get ul (list of products) append to this list

//     // OR

//     // jquery to clear the whole list, add product_list template


//     // var html = "<li id='" + result.id + '">' + result.productname + "</li>"

//     $('ul').append("<li>TEST</li>")
// }

// function addItem(e) {
//     e.preventDefault()

//     processAddItem()
//     // $.post("/add_item", 
//     //        formInputs,
//     //        processAddItem);


// }
// $('#add_item').on("click", addItem);


$("#update_form").on("submit", getUpdateInfo);

$('input[id^=remove_item]').on("click", deleteItem);

