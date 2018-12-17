let windows = {
    editors: [],
    outputs: [],
    env_diagrams: [],
    substitution_trees: [],
};

$("#open-btn").click(function () {
    $.post("./list_files", {
    }).done(function (data) {
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
                <tr><td class="align-middle">${file}</td> <td class="text-right"><button type="button" class="btn btn-primary">Open</button></td></tr>
            `);
            $("#file-list").children().last().find(".btn").click(function () {
                let index = states.length;
                let new_state = jQuery.extend({}, base_state);
                new_state.file_name = file;
                states.push(new_state);
                let config = {
                    type: "component",
                    componentName: "editor",
                    componentState: {id: index}
                };
                states[index].editor_open = true;
                myLayout.root.contentItems[0].addChild(config);
                $("#fileChooserModal").modal("hide");
            });
        }
    })
});

function next_expr(i) {
    states[i].expr_i = Math.min(states[i].expr_i + 1, states[i].states.length - 1);
    states[i].start = states[i].states[states[i].expr_i][0];
    states[i].end = states[i].states[states[i].expr_i][1];
    states[i].index = states[i].start;
    $("*").trigger("update");
}

function prev_expr(i) {
    states[i].expr_i = Math.max(states[i].expr_i - 1, 0);
    states[i].start = states[i].states[states[i].expr_i][0];
    states[i].end = states[i].states[states[i].expr_i][1];
    states[i].index = states[i].start;
    $("*").trigger("update");
}

function next_i(i) {
    states[i].index += 1;
    if (states[i].index === states[i].end && states[i].expr_i !== states[i].states.length - 1) {
        next_expr(i);
    } else {
        states[i].index = Math.min(states[i].index, states[i].end - 1);
    }
    $("*").trigger("update");
}

function prev_i(i) {
    states[i].index -= 1;
    if (states[i].index === states[i].start - 1 && states[i].expr_i !== 0) {
        prev_expr(i);
        states[i].index = states[i].end - 1;
    } else {
        states[i].index = Math.max(states[i].index, states[i].start);
    }
    $("*").trigger("update");
}
