define(["./state_handler", "./layout"], function (state_handler, layout) {
    let states = state_handler.states;

    function init() {
        $("#open-btn").click(function () {
            $.post("./list_files").done(function (data) {
                let files = new Set();
                for (let state of states) {
                    if (state.editor_open) {
                        files.add(state.file_name);
                    }
                }
                data = $.parseJSON(data);
                $("#fileChooserModal").modal();
                $("#file-list").html("");
                for (let file of data) {
                    if (files.has(file)) {
                        $("#file-list").append(`
                    <tr><td class="align-middle">${file}</td> <td class="text-right"><button type="button" disabled class="btn btn-primary disabled">Already Open</button></td></tr>
                `);
                        continue;
                    }
                    $("#file-list").append(`
                        <tr>
                        <td class="align-middle">${file}</td> 
                        <td class="text-right">
                            <button type="button" class="btn btn-primary">Open</button>
                        </td>
                        </tr>
                    `);
                    $("#file-list").children().last().find(".btn").click(function () {
                        let index = states.length;
                        let new_state = jQuery.extend({}, state_handler.base_state);
                        new_state.file_name = file;
                        states.push(new_state);
                        layout.open("editor", index);
                        $("#fileChooserModal").modal("hide");
                    });
                }
            })
        });
    }
    return {
        init: init
    }
});