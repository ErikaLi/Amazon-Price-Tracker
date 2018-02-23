"use strict";

function processUpdate(result) {
    alert(result.message);
    if (result.valid_threshold) {
        let newPrice = result.new_price;
        $('#wanted_price'+result.product_id).html(newPrice.toFixed(2));
    }
    if (result.empty) {
        $('#new_threshold'+result.product_id).val('');
    }
}


function getUpdateInfo(evt) {
    evt.preventDefault();
    var id = evt.currentTarget.id.replace("update_form", "");
    var formInputs = {
        "new_threshold": $("#new_threshold"+id).val(),
        "product_id": id,
    };

    $.post("/update", 
           formInputs,
           processUpdate);
}


function processRemoval(result) {
    alert(result.message);
    $('#'+result.product_id).hide();
}


function deleteItem(evt) {
    evt.preventDefault();

    var id = evt.currentTarget.id.replace("remove_item", "");

    var formInputs = {
        "product_id": id,
    };

    $.post("/remove", 
           formInputs,
           processRemoval);

}


function addItem(evt) {
    evt.preventDefault();

    var formInputs = {
        "url": $("#url_add").val(),
        "threshold": $("#threshold_add").val(),
    };

    $.post("/wishlist_add", formInputs, processAdd);
}


function processAdd(result) {
    alert(result.message);

    if (result.redirect) {
        window.location.href = result.redirect_url;
    }

    if (result.empty) {
        $('#threshold_add').val('');
    }

    if (result.added) {

        $("#new_item").prepend(result.html_content);

    }

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


$('ul').on("submit", "form[id^=update_form]", getUpdateInfo);

// parent, descendant contained in the parent
$('ul').on("click", "input[id^=remove_item]", deleteItem);


$("#add_item_form").on("submit", addItem);


