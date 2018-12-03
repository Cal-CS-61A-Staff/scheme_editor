let states = [
    {
        states: [],
        environments: [],
        moves: [],
        out: "",
        minIndex: 0,
        index: 0,
        globalFrameID: -1,

        sub_open: false,
        env_open: false,
        turtle_open: false,
        out_open: false,

        root: "demo"
    }
];

function getDims(parentElement) {
    parentElement = parentElement || document.body;
    let div = document.createElement('div');
    div.style.width = "1000em";
    $(div).css("white-space", "pre-line");
    $(div).css("font-family", "Monaco, monospace");
    $(div).css("font-size", "16px");

    div.innerHTML = "x\n".repeat(1000);
    parentElement.appendChild(div);
    let w = div.offsetWidth / 1000;
    let h = div.offsetHeight / 1000;
    parentElement.removeChild(div);
    return [w, h];
}

function countLines(elem) {
   let divHeight = elem.offsetHeight;
   let lineHeight = parseInt(elem.style.lineHeight);
   return divHeight / lineHeight;
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
            }).done(function (data) {
                console.log(data);
                data = $.parseJSON(data);
                states[componentState.id].states = data.states;
                states[componentState.id].environments = data.environments;
                states[componentState.id].moves = data.graphics;
                states[componentState.id].out = data.out[0];
                states[componentState.id].start = data.start;
                states[componentState.id].end = data.end;
                states[componentState.id].root = data.root;
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

                states[componentState.id].index = data.start;
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
        container.getElement().find(".output").html(states[componentState.id].out);
        container.getElement().find(".preview").html(preview);
        editor.focus();
        container.getElement().find(".output-wrapper").scrollTop(
            container.getElement().find(".output-wrapper")[0].scrollHeight);
        let lines = states[componentState.id].out.split("\n").length;
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
        editor.session.gutterRenderer =  {
            getWidth: function(session, lastLineNumber, config) {
                return 3 * config.characterWidth;
            },
            getText: function(session, row) {
                return "scm> ";
            }
        };

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
                }).done(function (data) {
                    // editor.setValue(val.slice(firstTerminator + 1));
                    data = $.parseJSON(data);
                    i = 0;
                    if (data.out[0].trim() !== "") {
                        states[componentState.id].out += "\n" + data.out[0];
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
            </div>
            <div class="tree" id="cat">
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
        display_tree(get_i(states[componentState.id].states, states[componentState.id].root, states[componentState.id].index), svg, 10, 10, 0, [0]);
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
        states[componentState.id].index = Math.max(states[componentState.id].index - 1, states[componentState.id].start);
        $("*").trigger("update");
    });

    container.getElement().find(".next").click(function () {
        states[componentState.id].index =
            Math.min(states[componentState.id].index + 1, states[componentState.id].end - 1);
        $("*").trigger("update");
    });
});

myLayout.registerComponent('env_diagram', function (container, componentState) {
    container.getElement().html(`
    <div class="envs" id="cat">
        <svg></svg>
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

    if (parent.length() !== 0) {
        charWidth = parent.length() / data["str"].length;
    }

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

myLayout.init();

$(window).resize(function () {
    myLayout.updateSize($("#body").width(), $("#body").height());
});

savedState = localStorage.getItem("savedState");
if (savedState !== null) {
    states = JSON.parse(savedState);
    $("*").trigger("update");
}
