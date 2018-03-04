function addRec(result) {
    alert(result.message);
    $('#recommendation'+result.rec_id).hide();
}


function getRecInfo(evt) {
    evt.preventDefault();

    var id = evt.currentTarget.id.replace("add_rec", "");

    var formInputs = {
        "recommendation_id": id,
        "threshold": $("#rec_wanted"+id).val()
    };

    $.post("/add_rec", 
           formInputs,
           addRec);

}

$('ul').on("submit", "form[id^=add_rec]", getRecInfo);