let i = 0;
let data = [];
let starts = [0];

let editors = [];
let container = initializeSVG();


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
        $.post("./process2", {code: out}).done(function (_data) {
            i = 0;
            data = _data["states"];
            if (data.length > 0) {
                display(i);
            }
            addRow(false);
            for (let j = 0; j !== editors.length; ++j) {
                $(`#output-${j}`).html(_data["out"][j]);
            }
        });
        // disableEditor(editors[i]);
    } else {
        while (editors.length !== k + 1) {
            $(`#row-${editors.length - 1}`).remove();
            editors.pop();
        }
        enableEditor(editors[k]);
        container.clear();
        $(`#row-${k} .button`)
            .text("Execute")
            .removeClass("btn-outline-danger")
            .addClass("btn-outline-success");
    }
});

$("#prev").click(function () {
    i = Math.max(i - 1, 0);
    display(i);
});

$("#next").click(function () {
    i = Math.min(i + 1, data.length - 1);
    display(i);
});

addRow(true);
window.scrollTo(0, 0);

function display(i) {
    container.clear();
    starts = [0];

    let svg = $("#drawarea > svg").get(0);
    let zoom = svgPanZoom(svg).getZoom();
    let pan = svgPanZoom(svg).getPan();

    svgPanZoom(svg).destroy();
    _display(data[i], container, 10, 10, 0);
    svgPanZoom(svg, {fit: false, zoomEnabled: true, center: false});

    svgPanZoom(svg).zoom(zoom);
    svgPanZoom(svg).pan(pan);
}

function _display(data, container, x, y, level) {
    let charHeight = 32;
    let charWidth = 14.4;

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

    let parent = container.text(data["str"]).font("family", "Monaco").font("size", 24).dx(x).dy(y);
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
        _display(child, container, Math.max(x + xDelta - 100000, starts[level + 1]), y + 100, level + 1, i);
        xDelta += parent_len + charWidth;
    }
}

function initializeSVG() {
    out = SVG("drawarea").size($(".starter-template").width(), 500);
    svgPanZoom($("#drawarea > svg").get(0), {fit: false, zoomEnabled: true, center: false});
    return out;
}

function disableEditor(editor) {
    editor.setOptions({
        readOnly: true,
        highlightActiveLine: false,
        highlightGutterLine: false
    });
    editor.renderer.$cursorLayer.element.style.opacity = 0;
    // editor.container.style.pointerEvents="none";
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
    editor.setOption("fontSize", 24);
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
