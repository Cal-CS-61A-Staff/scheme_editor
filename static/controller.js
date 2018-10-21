let i = 0;
let states = [];
let environments = [];
let starts = [0];

let editors = [];
let tree_container = initializeTreeSvg();
let environment_container = initializeEnvironmentSvg();

let displayingStates = true;

let isFirst = true;

$("#editors").on("submit", ".code-form", function (e) {
    e.preventDefault();
    let k = parseInt($(this).closest('form').parent().attr('id').substr(4));
    if (k + 1 === editors.length) {
        if (editors[editors.length - 1].getValue().trim() === "") {
            return;
        }
        let out = [];
        for (let j = 0; j !== editors.length; ++j) {
            out.push(editors[j].getValue());
        }
        displayingStates = !$("#hide_subs").is(':checked');

        if (!displayingStates) {
            $("#substitution_tree").hide();
            $("#sub_br").hide();
            $("#sub_nav").hide();
            $("#environment_diagram").height(600);
            environment_container.height(600);
        } else {
            $("#substitution_tree").show();
            $("#sub_br").show();
            $("#sub_nav").show();
        }

        $.post("./process2", {code: out, skip_tree: $("#hide_subs").is(':checked')}).done(function (data) {
            i = 0;
            states = data["states"];
            environments = data["environments"];
            if (environments.length > 0) {
                isFirst = true;
                display(i);
            }
            addRow(false);
            for (let j = 0; j !== editors.length; ++j) {
                $(`#output-${j}`).html(data["out"][j]);
            }
        });
        // disableEditor(editors[i]);
    } else {
        while (editors.length !== k + 1) {
            $(`#row-${editors.length - 1}`).remove();
            editors.pop();
        }
        enableEditor(editors[k]);
        tree_container.clear();
        states = [];
        environment_container.clear();
        environments = [];
        $(`#row-${k} .button`)
            .text("Execute")
            .removeClass("btn-outline-danger")
            .addClass("btn-outline-success");
    }
});

$("#prev").click(function () {
    if (environments.length === 0) return;
    i = Math.max(i - 1, 0);
    display(i);
});

$("#next").click(function () {
    if (environments.length === 0) return;
    if (displayingStates) {
        i = Math.min(i + 1, states.length - 1);
    } else {
        i = Math.min(i + 1, environments.length - 1);
    }
    display(i);
});

$("#prev_fast").click(function () {
    if (environments.length === 0) return;
    if (displayingStates) {
        i = environments[Math.max(get_curr_env(i) - 1, 0)][0] + 1;
    } else {
        --i;
    }
    console.log(i);
    i = Math.max(i, 0);
    display(i)
});

$("#next_fast").click(function () {
    if (environments.length === 0) return;
    if (displayingStates) {
        i = environments[Math.min(get_curr_env(i) + 1, environments.length - 1)][0] + 1;
    } else {
        i = Math.min(i + 1, environments.length - 1);
    }
    i = Math.max(i, 0);
    display(i);
});

addRow(true);
window.scrollTo(0, 0);

function display(i) {
    tree_container.clear();
    starts = [0];

    if (displayingStates) {
        let svg = $("#substitution_tree > svg").get(0);
        let zoom = svgPanZoom(svg).getZoom();
        let pan = svgPanZoom(svg).getPan();

        svgPanZoom(svg).destroy();
        if (states !== []) {
            display_tree(states[i], tree_container, 10, 10, 0);
        }
        svgPanZoom(svg, {fit: false, zoomEnabled: true, center: false});

        if (isFirst) {
            svgPanZoom(svg).reset();
        } else {
            svgPanZoom(svg).zoom(zoom);
            svgPanZoom(svg).pan(pan);
        }
    }
    // Yeah I know copy + paste is bad but whatever

    let svg = $("#environment_diagram > svg").get(0);
    let zoom = svgPanZoom(svg).getZoom();
    let pan = svgPanZoom(svg).getPan();

    svgPanZoom(svg).destroy();
    display_env(environments, environment_container, i);
    svgPanZoom(svg, {fit: false, zoomEnabled: true, center: false});

    if (isFirst) {
        svgPanZoom(svg).reset();
    } else {
        svgPanZoom(svg).zoom(zoom);
        svgPanZoom(svg).pan(pan);
    }

    isFirst = false;
}

function get_curr_env(i) {
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
    let charHeight = 32 * 2 / 3;
    let charWidth = 14.4 * 2 / 3;

    let j;
    if (displayingStates) {
        j = get_curr_env(i);
    } else {
        j = i;
    }
    container.clear();

    let curr_y = 10;

    for (let frame of environments[j][1].slice(1)) {
        let out = "Frame f" + frame[0][0] + ": " + frame[0][2] + " [parent = f" + frame[0][1] + "]\n";
        let maxlen = out.length;
        for (let k = 0; k !== frame[1].length; ++k) {
            let line = "   " + frame[1][k][0] + ": " + frame[1][k][1] + "\n";
            maxlen = Math.max(maxlen, line.length);
            out += line;
        }
        let text = container.text(out).font("family", "Monaco").font("size", 16).dx(25).dy(curr_y);
        let rect = container.rect(maxlen * charWidth + 10, charHeight * (frame[1].length + 1) + 10)
            .dx(15).dy(curr_y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();

        curr_y += charHeight * (frame[1].length + 1) + 20;
    }
}

function display_tree(data, container, x, y, level) {
    let charHeight = 32 * 2 / 3;
    let charWidth = 14.4 * 2 / 3;

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

    let parent = container.text(data["str"]).font("family", "Monaco").font("size", 16).dx(x).dy(y);
    let xDelta = charWidth;

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
        display_tree(child, container, Math.max(x + xDelta - 100000, starts[level + 1]), y + 100, level + 1);
        xDelta += parent_len + charWidth;
    }
}

function initializeTreeSvg() {
    out = SVG("substitution_tree").size($(".starter-template").width() / 2, 300);
    svgPanZoom($("#substitution_tree > svg").get(0), {fit: false, zoomEnabled: true, center: false});
    return out;
}

function initializeEnvironmentSvg() {
    out = SVG("environment_diagram").size($(".starter-template").width() / 2, 300);
    svgPanZoom($("#environment_diagram > svg").get(0), {fit: false, zoomEnabled: true, center: false});
    return out;
}

function disableEditor(editor) {
    editor.setOptions({
        readOnly: true,
        highlightActiveLine: false,
        highlightGutterLine: false
    });
    editor.renderer.$cursorLayer.element.style.opacity = 0;
    // editor.tree_container.style.pointerEvents="none";
    editor.container.style.opacity = 0.5;
    editor.renderer.setStyle("disabled", true);
    editor.blur();
}

function enableEditor(editor) {
    editor.setOptions({
        readOnly: false,
        highlightActiveLine: true,
        highlightGutterLine: true
    });
    editor.renderer.$cursorLayer.element.style.opacity = 1;
    editor.container.style.pointerEvents = "all";
    editor.container.style.opacity = 1;
    editor.renderer.setStyle("disabled", false);
}

function initializeEditor(editor) {
    editor = ace.edit(editor);

    ace.config.set("packaged", true);
    ace.config.set("basePath", "/ace");

    // editor.setTheme("ace/theme/clouds");
    editor.session.setMode("ace/mode/scheme");
    editor.setOption("minLines", 1);
    editor.setOption("maxLines", 100);
    editor.setOption("fontSize", 16);
    editor.setOption("showLineNumbers", false);
    editor.setOption("showGutter", false);

    editor.container.style.background = "white";

    editor.focus();

    return editor;
}

function addRow(isFirst) {
    let i = editors.length;

    if (i !== 0) {
        // disable previous row
        $(`#row-${i - 1} .button`)
            .text("Revert")
            .addClass("btn-outline-danger")
            .removeClass("btn-outline-success");
        // disableEditor(editors[i - 1]);
    }


    let middle = `
    <div class="form-row"> <div class="col">
        <div id="output-${i - 1}" style="white-space: pre-line" class="editor-wrapper" style="width: 100%">
        </div>
    </div></div>
    <br>
    `;

    if (isFirst) {
        middle = "";
    }

    let data = `
    <div id="row-${i}" class="code-row">
    <form class="code-form" method="post">
        ` + middle +

        `<div class="form-row">
        <div class="col">
        <div class="editor-wrapper">
                <div class="editor"></div>
            </div>
        </div>
        <div class="col-auto">
            <button class="button form-control mb-2 btn btn-outline-success" type="submit">Execute</button>
        </div>
    </div>
    </form>
    <br>
    </div>
    `;
    $("#editors").append(data);
    editors.push(initializeEditor($(`#row-${i} .editor`).get(0)))
}
