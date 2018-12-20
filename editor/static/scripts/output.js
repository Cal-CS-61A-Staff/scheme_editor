import {saveState, states} from "./state_handler";
import {notify_close, notify_open} from "./layout";
import {make, request_update} from "./event_handler";

export {register};

function register(myLayout) {
    myLayout.registerComponent('output', function (container, componentState) {
        container.getElement().html(`
        <div class="output-wrapper">
            <div class="output-holder">
                <div class="output">[click Run to start!]</div>
            </div>
            <div class="console-wrapper">
                <div class="console-input"></div>
            </div>
            <div class="preview"></div>
        </div>
        `);

        make(container, "output", componentState.id);

        let preview = "";
        let editorDiv;
        let editor;

        container.getElement().find(".output").on("update", function () {
            container.getElement().find(".output").html(states[componentState.id].out.trim());
            container.getElement().find(".preview").html(preview);
            container.getElement().find(".output-wrapper").scrollTop(
            container.getElement().find(".output-wrapper")[0].scrollHeight);
        });
        container.getElement().on("click", function () {
            editor.focus();
        });

        container.on("open", function () {
            editorDiv = container.getElement().find(".console-input").get(0);
            editor = ace.edit(editorDiv);
            ace.config.set("packaged", true);
            editor.session.setMode("ace/mode/scheme");
            editor.setOption("fontSize", 14);
            editor.setOption("enableBasicAutocompletion", true);
            editor.setOption("minLines", 1);
            editor.setOption("maxLines", 100);
            editor.setOption("highlightActiveLine", false);
            editor.container.style.background = "white";
            editor.session.gutterRenderer = {
                getWidth: function (session, lastLineNumber, config) {
                    return 3 * config.characterWidth;
                },
                getText: function () {
                    return "scm> ";
                }
            };
            editor.focus();

            container.on("resize", function () {
                editor.resize();
            });

            editor.getSession().on("change", function () {
                let val = editor.getValue();
                val = val.replace(/\r/g, "");
                if (val.slice(-1) === "\n") {
                    val = val.trim();
                    editor.setReadOnly(true);
                    editor.setReadOnly(false);
                    editor.setValue("", 0);
                    editor.focus();
                    setTimeout(function () {
                        editor.setValue("", 0);
                    }, 10);
                    val = val.replace(/\n/g, "");
                    states[componentState.id].out += "\nscm> " + val;
                    request_update();
                    $.post("./process2", {
                        code: [val],
                        globalFrameID: states[componentState.id].globalFrameID,
                        curr_i: states[componentState.id].states.slice(-1)[0][1],
                        curr_f: states[componentState.id].environments.length
                    }).done(function (data) {
                        // editor.setValue(val.slice(firstTerminator + 1));
                        data = $.parseJSON(data);
                        if (data.out[0].trim() !== "") {
                            states[componentState.id].out += "\n" + data.out[0].trim();
                        }
                        if (data.success) {
                            for (let key of data.active_frames) {
                                states[componentState.id].environments.push(data.frame_lookup[key]);
                            }
                            states[componentState.id].environments[0] =
                                data.frame_lookup[states[componentState.id].globalFrameID];
                            states[componentState.id].states.push(...data.states);
                            states[componentState.id].roots.push(...data.roots);
                        }
                        request_update();
                    });
                } else {
                    $.post("./instant", {
                        code: [editor.getValue()],
                        globalFrameID: states[componentState.id].globalFrameID,
                    }).done(function (data) {
                        data = $.parseJSON(data);
                        if (data.success) {
                            preview = "<i>" + data.content + "</i>";
                        } else {
                            preview = "";
                        }
                        request_update();
                    })
                }
            });
        });
    });
}