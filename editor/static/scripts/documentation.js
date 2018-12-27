import {end_slow} from "./event_handler";
import {states} from "./state_handler";

export {init}

function init() {
    $("#documentation-search").on("input", function () {
        console.log("typing!");
        let text = $("#documentation-search").val();
        $("#documentation-search").val("");
        $("#documentation-search-modal").val(text);
        console.log(text);
        $("#documentationModal").modal("show");
        $("#documentation-search-modal").focus();
    });

    $("#documentation-search-modal").on("input", function () {
        render($("#documentation-search-modal").val());
    });
}

function render(query) {
    $.post("./documentation", {
        query: query,
    }).done(function (data) {
        data = $.parseJSON(data);
        console.log(data);
        $("#documentation-body").empty();
        for (let elem of data) {
            $("#documentation-body").append(elem);
        }
    });
}