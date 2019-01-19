import {saveState, states, temp_file} from "./state_handler";

import {notify_close, open, open_prop} from "./layout";
import {begin_slow, end_slow, make, request_update} from "./event_handler";

export {register};

function register(layout) {
    layout.registerComponent('editor', function (container, componentState) {
        console.log(componentState.id);
        console.log(states);
        container.getElement().html(`
        <div class="content">
            <div class="header">        
                ${(!states[componentState.id].file_name.startsWith(temp_file)) ?
            `<button type="button" class="btn-default save-btn" aria-label="Save">
                    <span class="text"> Save </span>
                </button>` : ``}

                <button type="button" data-toggle="tooltip"
                            title="Open a console and run the program locally."
                            class="btn-success toolbar-btn run-btn">Run</button>
                ${(componentState.id === 0) ?
                `<button type="button" data-toggle="tooltip"
                            title="Run all ok.py tests locally."
                            class="btn-danger toolbar-btn test-btn">Test</button>` : ``}
                <button type="button" data-toggle="tooltip"
                            title="Step through the program's execution."
                            class="btn-primary toolbar-btn sub-btn">Debug</button>          
                <button type="button" data-toggle="tooltip"
                            title="View environment diagram."
                            class="btn-info toolbar-btn env-btn">Environments</button>          
                <button type="button" data-toggle="tooltip"
                            title="Reformat code and fix (some) minor mistakes."
                            class="btn-secondary toolbar-btn reformat-btn">Reformat</button>          
            </div>
            <div class="editor-wrapper">
                <div class="editor"></div>
            </div>
        </div>
    `);

        make(container, "editor", componentState.id);

        let editorDiv;
        let editor;

        let changed = false;
        let saveTimer;

        container.on("open", function () {
            editorDiv = container.getElement().find(".editor").get(0);
            editor = ace.edit(editorDiv);
            ace.config.set("packaged", true);
            editor.session.setMode("ace/mode/scheme");
            editor.setOption("fontSize", 14);
            editor.setOption("enableBasicAutocompletion", true);
            editor.setOption("enableLiveAutocompletion", true);
            editor.setAutoScrollEditorIntoView(true);
            editor.getSession().setUseSoftTabs(true);
            editor.container.style.background = "white";
            editor.focus();

            saveTimer = setInterval(save, 5000);

            states[componentState.id].editor_open = true;
            // windows.editors.push(container);

            container.on("resize", function () {
                editor.resize();
            });

            let decoded = $.parseJSON(start_data);
            if (componentState.id === 0) {
                states[componentState.id].file_name = decoded["file"];
            }

            if (states[componentState.id].file_name.startsWith(temp_file)) {
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
                changed = true;
            });
        });

        container.on("destroy", function () {
            clearInterval(saveTimer);
        });

        container.getElement().find(".run-btn").on("click", function () {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            begin_slow();
            $.post("./process2", {
                code: code,
                globalFrameID: -1,
                curr_i: 0,
                curr_f: 0,
            }).done(async function (data) {
                end_slow();
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
                    states[componentState.id].heap = data.heap;
                    states[componentState.id].frameUpdates = data.frameUpdates;

                } else {
                    states[componentState.id].out = data.out[0];
                }

                await save();

                open("output", componentState.id);
                // noinspection JSIgnoredPromiseFromCall
                saveState();
                $("*").trigger("reset");
                request_update();
            });
        });

        container.getElement().find(".save-btn").on("click", function () {
            // noinspection JSIgnoredPromiseFromCall
            save();
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

        container.getElement().find(".sub-btn").on("click", async function () {
            await save();
            open("substitution_tree", componentState.id);
        });

        container.getElement().find(".env-btn").on("click", async function () {
            await save();
            open("env_diagram", componentState.id);
        });

        container.getElement().find(".test-btn").on("click", function () {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            begin_slow();
            $.post("./test", {
                code: code,
                filename: states[componentState.id].file_name,
            }).done(async function (data) {
                end_slow();
                data = $.parseJSON(data);
                states[componentState.id].test_results = data;
                await save();
                open("test_results", componentState.id);
            });
        });

        async function save() {
            if (!changed || states[componentState.id].file_name.startsWith(temp_file)) {
                return;
            }
            container.getElement().find(".save-btn > .text").text("Saving...");

            let code = [editor.getValue()];
            await $.post("./save", {
                code: code,
                filename: states[componentState.id].file_name,
            }).done(function (data) {
                if (data === "success") {
                    container.getElement().find(".save-btn > .text").text("Saved");
                    changed = false;
                } else {
                    alert("Save error - try copying code from editor to a file manually");
                }
            });
        }
    });
}