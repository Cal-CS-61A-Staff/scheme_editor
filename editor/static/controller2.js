let base_state = {
        states: [],
        environments: [],
        moves: [],
        out: "",

        index: 0,
        expr_i: 0,

        start: 0,
        end: 0,
        roots: ["demo"],

        globalFrameID: -1,

        editor_open: false,
        sub_open: false,
        env_open: false,
        turtle_open: false,
        out_open: false,
        tests_open: false,

        test_results: undefined,

        file_name: "",
};

let states = [jQuery.extend({}, base_state)];

let temp_file = "<temporary>";

function getDims(parentElement) {
    parentElement = parentElement || document.body;
    let div = document.createElement('div');
    $(div).css("position", "absolute");
    $(div).css("white-space", "pre-line");
    $(div).css("font-family", "Monaco, monospace");
    $(div).css("font-size", "14px");

    div.innerHTML = "x".repeat(999) + "x\n".repeat(1000);
    parentElement.appendChild(div);
    let w = div.offsetWidth / 1000;
    let h = div.offsetHeight / 1000;
    parentElement.removeChild(div);
    return [w, h];
}

let charHeight = getDims()[1];
let charWidth = getDims()[0];

let config = {
    settings: {
        showPopoutIcon: false,
        showMaximiseIcon: false,
        showCloseIcon: true,
    },
    content: [{
        type: 'row',
        content: [{
            type: 'component',
            componentName: 'editor',
            componentState: {id: 0},
            isClosable: false,
        }]
    }]
};

let myLayout;
savedLayout = localStorage.getItem('savedLayout');
if (savedLayout !== null) {
    myLayout = new GoldenLayout(JSON.parse(savedLayout), $("#body"));
} else {
    myLayout = new GoldenLayout(config, $("#body"));
}

savedState = localStorage.getItem("savedState");
if (savedState !== null) {
    states = JSON.parse(savedState);
}

$(window).resize(function () {
    myLayout.updateSize($("#body").width(), $("#body").height());
});

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
                states[index].tests_open = true;
                myLayout.root.contentItems[0].addChild(config);
                $("#fileChooserModal").modal("hide");
            });
        }
    })
});

myLayout.registerComponent('editor', function (container, componentState) {
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

                if (!states[componentState.id].out_open) {
                    let config = {
                        type: "component",
                        componentName: "output",
                        componentState: {id: componentState.id}
                    };
                    states[componentState.id].out_open = true;
                    myLayout.root.contentItems[0].addChild(config)
                }

                $("*").trigger("reset");

                $("*").trigger("update");
            });
        });

    container.getElement().find(".save-btn").on("click", function (e) {
        container.getElement().find(".save-btn > .text").text("Saving...");

        localStorage.setItem('savedLayout', JSON.stringify(myLayout.toConfig()));

        localStorage.setItem('savedState', JSON.stringify(states));

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

    container.getElement().find(".reformat-btn").on("click", function (e) {
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
        if (states[componentState.id].sub_open) {

        } else {
            let config = {
                type: "component",
                componentName: "substitution_tree",
                componentState: {id: componentState.id}
            };
            states[componentState.id].sub_open = true;
            myLayout.root.contentItems[0].addChild(config)
        }

        $("*").trigger("update");
    });

    container.getElement().find(".env-btn").on("click", function () {
        if (states[componentState.id].env_open) {

        } else {
            let config = {
                type: "component",
                componentName: "env_diagram",
                componentState: {id: componentState.id}
            };
            states[componentState.id].env_open = true;
            myLayout.root.contentItems[0].addChild(config)
        }

        $("*").trigger("update");
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
            if (states[componentState.id].tests_open) {
            } else {
                let config = {
                    type: "component",
                    componentName: "test_results",
                    componentState: {id: componentState.id}
                };
                states[componentState.id].tests_open = true;
                myLayout.root.contentItems[0].addChild(config);
            }
            $("*").trigger("update");
        });
    });
});

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

    let preview = "";
    let editorDiv;
    let editor;

    container.getElement().find(".output").on("update", function (e) {
        container.getElement().find(".output").html(states[componentState.id].out.trim());
        container.getElement().find(".preview").html(preview);
        container.getElement().find(".output-wrapper").scrollTop(
            container.getElement().find(".output-wrapper")[0].scrollHeight);
    });
    container.getElement().on("click", function () {
        editor.focus();
    });

    container.on("destroy", function () {
        states[componentState.id].out_open = false;
    });
    container.on("open", function () {
        editorDiv = container.getElement().find(".console-input").get(0);
        editor = ace.edit(editorDiv);
        ace.config.set("packaged", true);
        ace.config.set("basePath", "/ace");
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
            getText: function (session, row) {
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
                $("*").trigger("update");
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
                    $("*").trigger("update");
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
                    $("*").trigger("update");
                })
            }
        });
    });
});

myLayout.registerComponent('substitution_tree', function (container, componentState) {
    container.getElement().html(`
        <div class="content">
            <div class="header">
            <div class="btn-group">
                <button type="button" class="btn btn-sm btn-secondary prev">Prev</button>          
                <button type="button" class="btn btn-sm btn-secondary next">Next</button>
            </div>            
            <div class="btn-group">
                <button type="button" class="btn btn-sm btn-secondary prev-expr">Prev Expr</button>          
                <button type="button" class="btn btn-sm btn-secondary next-expr">Next Expr</button>
            </div>
            </div>
            <div class="tree">
                <svg></svg>
            </div>
        </div>

    `);

    let rawSVG = container.getElement().find(".tree > svg").get(0);
    // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
    let svg = SVG.adopt(rawSVG).size(container.width, container.height);

    container.getElement().find(".tree").on("update", function (e) {
        let zoom = svgPanZoom(rawSVG).getZoom();
        let pan = svgPanZoom(rawSVG).getPan();
        svgPanZoom(rawSVG).destroy();
        svg.clear();
        display_tree(get_i(
            states[componentState.id].states[states[componentState.id].expr_i][2],
            states[componentState.id].roots[states[componentState.id].expr_i],
            states[componentState.id].index),
            svg, 10, 10, 0, [0]);
        svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        if (isNaN(zoom)) {
            svgPanZoom(rawSVG).reset();
        } else {
            svgPanZoom(rawSVG).zoom(zoom);
            svgPanZoom(rawSVG).pan(pan);
        }
    });

    container.getElement().find(".tree").on("reset", function (e) {
        svgPanZoom(rawSVG).reset();
    });

    container.on("resize", function () {
        let zoom = svgPanZoom(rawSVG).getZoom();
        let pan = svgPanZoom(rawSVG).getPan();
        svgPanZoom(rawSVG).destroy();
        svg.size(container.width, container.height);
        svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        if (isNaN(zoom)) {
            svgPanZoom(rawSVG).reset();
        } else {
            svgPanZoom(rawSVG).zoom(zoom);
            svgPanZoom(rawSVG).pan(pan);
        }
    });

    container.on("destroy", function () {
        states[componentState.id].sub_open = false;
    });

    container.getElement().find(".prev").click(function () {
        prev_i(componentState.id);
    });

    container.getElement().find(".next").click(function () {
        next_i(componentState.id);
    });

    container.getElement().find(".prev-expr").click(function () {
        prev_expr(componentState.id);
    });

    container.getElement().find(".next-expr").click(function () {
        next_expr(componentState.id);
    });
});

myLayout.registerComponent('env_diagram', function (container, componentState) {
    container.getElement().html(`
    <div class="content">
        <div class="header">
        <div class="btn-group">
            <button type="button" class="btn btn-sm btn-secondary prev">Prev</button>          
            <button type="button" class="btn btn-sm btn-secondary next">Next</button>
        </div>            
        <div class="btn-group">
            <button type="button" class="btn btn-sm btn-secondary prev-expr">Prev Expr</button>          
            <button type="button" class="btn btn-sm btn-secondary next-expr">Next Expr</button>
        </div>
        </div>
        <div class="envs">
            <svg></svg>
        </div>
    </div>
    `);

    let rawSVG = container.getElement().find(".envs > svg").get(0);
    // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
    let svg = SVG.adopt(rawSVG).size(container.width, container.height);

    container.getElement().find(".envs").on("update", function (e) {
        let zoom = svgPanZoom(rawSVG).getZoom();
        let pan = svgPanZoom(rawSVG).getPan();
        svgPanZoom(rawSVG).destroy();
        svg.clear();
        display_env(states[componentState.id].environments, svg, states[componentState.id].index);
        svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        if (isNaN(zoom)) {
            svgPanZoom(rawSVG).reset();
        } else {
            svgPanZoom(rawSVG).zoom(zoom);
            svgPanZoom(rawSVG).pan(pan);
        }
    });

    container.getElement().find(".envs").on("reset", function (e) {
        svgPanZoom(rawSVG).reset();
    });

    container.on("resize", function () {
        let zoom = svgPanZoom(rawSVG).getZoom();
        let pan = svgPanZoom(rawSVG).getPan();
        svgPanZoom(rawSVG).destroy();
        svg.size(container.width, container.height);
        svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        if (isNaN(zoom)) {
            svgPanZoom(rawSVG).reset();
        } else {
            svgPanZoom(rawSVG).zoom(zoom);
            svgPanZoom(rawSVG).pan(pan);
        }
    });

    container.on("destroy", function () {
        states[componentState.id].env_open = false;
    });
});

myLayout.registerComponent('test_results', function (container, componentState) {
    container.getElement().on("update", function () {
        let data = states[componentState.id].test_results;
        container.getElement().html(`<div id="accordion"> </div>`);
        let expanded = false;
        for (let entry of data) {
            let random_id = Math.random().toString(36).replace(/[^a-z]+/g, '');
            let card_style = entry.passed ? "bg-success" : "bg-danger";
            let hideshow = (!expanded && !entry.passed) ? "show" : "hide";
            expanded |= !entry.passed;
            $("#accordion").append(`
            <div class="card ">
                <div class="card-header ${card_style} text-white" id="${random_id + "x"}" data-toggle="collapse" 
                data-target="#${random_id}"> ${entry.problem} </div>
                <div id="${random_id}" class="collapse ${hideshow}" aria-labelledby="${random_id + "x"}" data-parent="#accordion">
                <div class="card-body" style="padding: 5px">
                    <table class="table table-sm table-hover">
                        <tbody>
                        </tbody>
                  </table>
                  </div>
                </div>
            </div>
            `);

            for (let i = 0; i !== entry.suites.length; ++i) {
                for (let j = 0; j !== entry.suites[i].length; ++j) {
                    let test = entry.suites[i][j];
                    let pass_string = (test.passed ? "Passed!" : "Failed!");
                    let class_string = (test.passed ? "" : "font-bold");
                    $("#accordion").children().last().find("tbody").append(`
                    <tr class="${class_string}">
                        <td class="align-middle">Suite ${i + 1}, Case ${j + 1}</td> 
                        <td class="align-middle">${pass_string}</td> 
                        <td class="text-right"> <button class="btn btn-secondary"> View Case </button> </td>
                    </tr>`);
                    $(`#${random_id}`).find(".btn").last().click(function () {
                        let index = states.length;
                        let new_state = jQuery.extend({}, base_state);
                        new_state.file_name = temp_file;
                        new_state.file_content = test.code;
                        states.push(new_state);
                        let config = {
                            type: "component",
                            componentName: "editor",
                            componentState: {id: index}
                        };
                        states[index].tests_open = true;
                        myLayout.root.contentItems[0].addChild(config);
                        $("#fileChooserModal").modal("hide");
                    });
                }
            }
        }
    });

    container.getElement().on("click", function () { });

    container.on("destroy", function () {
        states[componentState.id].tests_open = false;
    });

    container.on("open", function () {});
});

function display_env(environments, container, i) {
    container.clear();

    let curr_y = 10;

    for (let frame of environments) {
        let out = "Frame " + frame.name + ": " + frame.label + " [parent = " + frame.parent + "]\n";
        let maxlen = out.length;
        let k;
        for (k = 0; k !== frame["bindings"].length; ++k) {
            if (frame["bindings"][k][0] > i) {
                break;
            }
            let line = "   " + frame["bindings"][k][1][0] + ": " + frame["bindings"][k][1][1] + "\n";
            maxlen = Math.max(maxlen, line.length);
            out += line;
        }
        if (k === 0) {
            continue;
        }
        let text = container.text(out).font("family", "Monaco, monospace").font("size", 14).dx(25).dy(curr_y);
        let rect = container.rect(maxlen * charWidth + 10, charHeight * (k + 1) + 10)
            .dx(15).dy(curr_y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();

        curr_y += charHeight * (k + 1) + 20;
    }
}

function get_i(all_data, curr, i) {
    let labels = [
        ["transitions", "transition_type"],
        ["strs", "str"],
        ["parent_strs", "parent_str"],
    ];
    let data = {};
    for (let label of labels) {
        for (let val of all_data[curr][label[0]]) {
            if (val[0] > i) {
                break;
            }
            data[label[1]] = val[1];
        }
    }

    for (j = 0; j < all_data[curr]["children"].length - 1; ++j) {
        if (all_data[curr]["children"][j + 1][0] > i) {
            break;
        }
    }

    data["children"] = [];
    for (let child of all_data[curr]["children"][j][1]) {
        data["children"].push(get_i(all_data, child, i));
    }
    return data;
}

function display_tree(data, container, x, y, level, starts) {
    let color;
    switch (data["transition_type"]) {
        case "UNEVALUATED":
            color = "#536dff";
            break;
        case "EVALUATING":
            color = "#ff0f00";
            break;
        case "EVALUATED":
            color = "#44ff51";
            break;
        case "APPLYING":
            color = "#ffa500";
            break;
    }

    let rect = container.rect(data["str"].length * charWidth + 10, charHeight + 10)
        .dx(x - 5).dy(y)
        .stroke({color: color, width: 2})
        .fill({color: "#FFFFFF"})
        .radius(10);

    let parent = container.text(data["str"]).font("family", "Monaco, monospace").font("size", 14).dx(x).dy(y);
    let xDelta = charWidth;

    // if (parent.length() !== 0) {
    //     charWidth = parent.length() / data["str"].length;
    // }

    starts[level] = x + charWidth * (data["str"].length + 1);
    for (let child of data["children"]) {
        if (starts.length === level + 1) {
            starts.push([10]);
        }
        let parent_len = child["parent_str"].length * charWidth;
        container.line(x + xDelta + parent_len / 2, y + charHeight + 5,
            Math.max(x + xDelta - 100000, starts[level + 1]) + child["str"].length * charWidth / 2 + 5,
            y + 110)
            .stroke({width: 3, color: "#c8c8c8"}).back();
        display_tree(child, container, Math.max(x + xDelta - 100000, starts[level + 1]), y + 100, level + 1, starts);
        xDelta += parent_len + charWidth;
    }
}

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

myLayout.init();

$("*").trigger("update");