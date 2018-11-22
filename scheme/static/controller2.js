let states = [
    {
        states: [],
        environments: [],
        moves: [],
        out: "",
        index: 0,

        sub_open: true,
        env_open: false,
        turtle_open: false,
        out_open: true
    }
];

let charHeight = 32 * 2 / 3;
let charWidth = 14.4 * 2 / 3;

let config = {
    content: [{
        type: 'row',
        content: [{
            type: 'component',
            componentName: 'editor',
            componentState: {id: 0}
        }, {
            type: 'column',
            content: [{
                type: 'component',
                componentName: 'output',
                componentState: {id: 0}
            }, {
                type: 'component',
                componentName: 'substitution_tree',
                componentState: {id: 0}
            }]
        }]
    }]
};

let myLayout = new GoldenLayout(config);

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
        editor.container.style.background = "white";
        editor.focus();

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
                skip_tree: "false",
                skip_envs: "false",
                hide_return_frames: "false"
            }).done(function (data) {
                data = $.parseJSON(data);
                i = 0;
                states[componentState.id].states = data.states;
                states[componentState.id].environments = data.environments;
                states[componentState.id].moves = data.graphics;
                states[componentState.id].out = data.out[0];

                if (!states[componentState.id].out_open) {
                    let config = {
                        type: "component",
                        componentName: "output",
                        componentState: {id: componentState.id}
                    };
                    states[componentState.id].out_open = true;
                    myLayout.root.contentItems[0].addChild(config)
                }

                states[componentState.id].index = 0;
                $("*").trigger("reset");

                $("*").trigger("update");
            });
        });

        container.getElement().find(".save-btn").on("click", function (e) {
            container.getElement().find(".save-btn > .text").text("Saving...");
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
            states[componentState.id].sub_open = true;
            myLayout.root.contentItems[0].addChild(config)
        }

        $("*").trigger("update");
        })
    });

});

myLayout.registerComponent('output', function (container, componentState) {
    container.getElement().html('<div class="output"> [click Run to start!] </div>');
    container.getElement().find(".output").on("update", function (e) {
        container.getElement().find(".output").html(states[componentState.id].out);
    });
    container.on("destroy", function () {
        states[componentState.id].out_open = false;
    })
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
        display_tree(states[componentState.id].states[states[componentState.id].index], svg, 10, 10, 0, [0]);
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
        states[componentState.id].index = Math.max(states[componentState.id].index - 1, 0);
        $("*").trigger("update");
    });

    container.getElement().find(".next").click(function () {
        states[componentState.id].index =
            Math.min(states[componentState.id].index + 1, states[componentState.id].states.length - 1);
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

function get_curr_env(i, environments) {
    let j;
    for (j = 0; j !== environments.length; ++j) {
        if (environments[j][0] >= i) {
            break;
        }
    }
    --j;
    return j;
}

function display_env(environments, container, i) {
    let j;
    if (true) {  // TODO: displaying states or something?
        j = get_curr_env(i, environments);
    } else {
        j = i;
    }
    container.clear();

    let curr_y = 10;

    for (let frame of environments[j][1].slice(1)) {
        for (let i = 0; i !== 2; ++i) {
            if (typeof frame[0][i] !== "string") {
                console.log(frame[0][0]);
                frame[0][i] = 'f' + frame[0][i];
            }
        }
        let out = "Frame " + frame[0][0] + ": " + frame[0][2] + " [parent = " + frame[0][1] + "]\n";
        let maxlen = out.length;
        for (let k = 0; k !== frame[1].length; ++k) {
            let line = "   " + frame[1][k][0] + ": " + frame[1][k][1] + "\n";
            maxlen = Math.max(maxlen, line.length);
            out += line;
        }
        let text = container.text(out).font("family", "Monaco, monospace").font("size", 16).dx(25).dy(curr_y);
        let rect = container.rect(maxlen * charWidth + 10, charHeight * (frame[1].length + 1) + 10)
            .dx(15).dy(curr_y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();

        curr_y += charHeight * (frame[1].length + 1) + 20;
    }
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

    charWidth = parent.length() / data["str"].length;

    starts[level] = x + parent.length() + charWidth;

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
