import {states, temp_file} from "./state_handler";

import {open} from "./layout";

export {register};

function register(layout) {
    layout.registerComponent('editor', function (container, componentState) {
        container.getElement().html(`
        <div class="content">
            <div class="header">        
                ${(states[componentState.id].file_name !== temp_file) ?
            `<button type="button" class="btn-default save-btn" aria-label="Save">
                    <span class="text"> Save </span>
                </button>` : ``}

                <button type="button" class="btn-success toolbar-btn run-btn">Run</button>
                ${(componentState.id === 0) ?
            `<button type="button" class="btn-danger toolbar-btn test-btn">Test</button>` : ``}

                <button type="button" class="btn-info toolbar-btn sub-btn">Subs</button>          
                <button type="button" class="btn-info toolbar-btn env-btn">Envs</button>          
                <button type="button" class="btn-primary toolbar-btn reformat-btn">Reformat</button>          
            </div>
            <div class="editor-wrapper">
                <div class="editor"></div>
            </div>
        </div>
    `);
        let editorDiv;
        let editor;

        container.setTitle(states[componentState.id].file_name);

        container.on("open", function () {
            editorDiv = container.getElement().find(".editor").get(0);
            editor = ace.edit(editorDiv);
            ace.config.set("packaged", true);
            ace.config.set("basePath", "/ace");
            editor.session.setMode("ace/mode/scheme");
            editor.setOption("fontSize", 14);
            editor.setOption("enableBasicAutocompletion", true);
            editor.setOption("enableLiveAutocompletion", true);
            editor.setAutoScrollEditorIntoView(true);
            editor.getSession().setUseSoftTabs(true);
            editor.container.style.background = "white";
            editor.focus();

            states[componentState.id].editor_open = true;
            // windows.editors.push(container);

            container.on("resize", function () {
                editor.resize();
            });

            let decoded = $.parseJSON(start_data);
            if (componentState.id === 0) {
                states[componentState.id].file_name = decoded["file"];
            }

            if (states[componentState.id].file_name === temp_file) {
                editor.setValue(states[componentState.id].file_content);
            } else {
                $.post("/read_file", {
                    filename: states[componentState.id].file_name,
                }).done(function (data) {
                    data = $.parseJSON(data);
                    editor.setValue(data);
                });
            }

            editor.getSession().on("change", function () {
                container.getElement().find(".save-btn > .text").text("Save");
            });
        });

        container.on("destroy", function () {
            states[componentState.id].editor_open = false;
            // windows.editors = windows.editors.filter(item => item !== container);
        });

        container.getElement().find(".run-btn").on("click", function () {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            $.post("./process2", {
                code: code,
                globalFrameID: -1,
                curr_i: 0,
                curr_f: 0,
            }).done(function (data) {
                data = $.parseJSON(data);
                console.log(data);
                if (data.success) {
                    states[componentState.id].states = data.states;
                    states[componentState.id].environments = [];
                    for (let key of data.active_frames) {
                        states[componentState.id].environments.push(data.frame_lookup[key]);
                    }
                    states[componentState.id].moves = data.graphics;
                    states[componentState.id].out = data.out[0];
                    states[componentState.id].start = data.states[0][0];
                    states[componentState.id].end = data.states[0][1];
                    states[componentState.id].index = data.states[0][0];
                    states[componentState.id].expr_i = 0;
                    states[componentState.id].roots = data.roots;
                    states[componentState.id].globalFrameID = data.globalFrameID;
                } else {
                    states[componentState.id].out = data.out[0];
                }

                open("output", componentState.id);

                $("*").trigger("reset");
                $("*").trigger("update");
            });
        });

        container.getElement().find(".save-btn").on("click", function () {
            container.getElement().find(".save-btn > .text").text("Saving...");

            let code = [editor.getValue()];
            $.post("./save", {
                code: code,
                filename: states[componentState.id].file_name,
            }).done(function (data) {
                if (data === "success") {
                    container.getElement().find(".save-btn > .text").text("Saved");
                } else {
                    alert("Save error - try copying code from editor to a file manually");
                }
            });
        });

        container.getElement().find(".reformat-btn").on("click", function () {
            let code = [editor.getValue()];
            $.post("./reformat", {
                code: code,
            }).done(function (data) {
                data = $.parseJSON(data);
                if (data["result"] === "success") {
                    editor.setValue(data["formatted"]);
                } else {
                    alert("An error occurred!");
                }
            });
        });

        container.getElement().find(".sub-btn").on("click", function () {
            open("substitution_tree", componentState.id);
        });

        container.getElement().find(".env-btn").on("click", function () {
            open("env_diagram", componentState.id);
        });

        container.getElement().find(".test-btn").on("click", function () {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            $.post("./test", {
                code: code,
                filename: states[componentState.id].file_name,
            }).done(function (data) {
                data = $.parseJSON(data);
                states[componentState.id].test_results = data;
                open("test_results", componentState.id);
            });
        });
    });
}