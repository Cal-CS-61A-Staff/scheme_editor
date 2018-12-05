let states = [
    {
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

        sub_open: false,
        env_open: false,
        turtle_open: false,
        out_open: false,

    }
];

function getDims(parentElement) {
    parentElement = parentElement || document.body;
    let div = document.createElement('div');
    $(div).css("position", "absolute");
    $(div).css("white-space", "pre-line");
    $(div).css("font-family", "Monaco, monospace");
    $(div).css("font-size", "16px");

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
    content: [{
        type: 'row',
        content: [{
            type: 'component',
            componentName: 'editor',
            componentState: {id: 0}
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

myLayout.registerComponent('editor', function (container, componentState) {
    container.getElement().html(`
        <div class="content">
            <div class="header">        
                <button type="button" class="btn-default save-btn" aria-label="Save">
                    <span class="glyphicon glyphicon-floppy-disk" aria-hidden="true"></span>
                    <span class="text"> Save </span>
                </button>
                <button type="button" class="btn-success toolbar-btn run-btn">Run</button>

                <button type="button" class="btn-info toolbar-btn sub-btn">Subs</button>          
                <button type="button" class="btn-info toolbar-btn env-btn">Envs</button>          
                <button type="button" class="btn-info toolbar-btn reformat-btn">Reformat</button>          
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
        editor.setOption("fontSize", 16);
        editor.setOption("enableBasicAutocompletion", true);
        editor.setOption("enableLiveAutocompletion", true);
        editor.setAutoScrollEditorIntoView(true);
        editor.getSession().setUseSoftTabs(true);
        editor.container.style.background = "white";
        editor.focus();

        container.on("resize", function () {
            editor.resize();
        });

        let decoded = $.parseJSON(start_data);
        if (componentState.id !== 0 || $.isEmptyObject(decoded)) {
            return;
        }
        editor.setValue(decoded["code"][0]);

        container.getElement().find(".run-btn").on("click", function () {
            if (editor.getValue().trim() === "") {
                return;
            }
            let code = [editor.getValue()];
            $.post("./process2", {
                code: code,
                globalFrameID: -1,
                curr_i: i,
                curr_f: 0,
            }).done(function (data) {
                data = $.parseJSON(data);
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

        editor.getSession().on("change", function () {
            container.getElement().find(".save-btn > .text").text("Save");
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
        })
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

    container.getElement().find(".output").on("update", function (e) {
        container.getElement().find(".output").html(states[componentState.id].out.trim());
        container.getElement().find(".preview").html(preview);
        editor.focus();
        container.getElement().find(".output-wrapper").scrollTop(
            container.getElement().find(".output-wrapper")[0].scrollHeight);
    });
    container.getElement().on("click", function () {
        editor.focus();
    });

    container.on("destroy", function () {
        states[componentState.id].out_open = false;
    });
    let editorDiv;
    let editor;
    container.on("open", function () {
        editorDiv = container.getElement().find(".console-input").get(0);
        editor = ace.edit(editorDiv);
        ace.config.set("packaged", true);
        ace.config.set("basePath", "/ace");
        editor.session.setMode("ace/mode/scheme");
        editor.setOption("fontSize", 16);
        editor.setOption("enableBasicAutocompletion", true);
        editor.setOption("enableLiveAutocompletion", true);
        editor.setOption("minLines", 1);
        editor.setOption("maxLines", 1);
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

        container.on("resize", function () {
            editor.resize();
        });

        editor.getSession().on("change", function () {
            let val = editor.getValue();
            val = val.replace(/\r/g, "");
            let firstTerminator = val.indexOf("\n");
            if (firstTerminator !== -1) {
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
                    for (let key of data.active_frames) {
                        states[componentState.id].environments.push(data.frame_lookup[key]);
                    }
                    states[componentState.id].environments[0] =
                        data.frame_lookup[states[componentState.id].globalFrameID];
                    states[componentState.id].states.push(...data.states);
                    states[componentState.id].roots.push(...data.roots);
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
        let text = container.text(out).font("family", "Monaco, monospace").font("size", 16).dx(25).dy(curr_y);
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

    let parent = container.text(data["str"]).font("family", "Monaco, monospace").font("size", 16).dx(x).dy(y);
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