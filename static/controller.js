var editor = ace.edit("editor");

ace.config.set("packaged", true);
ace.config.set("basePath", "/ace");

// editor.setTheme("ace/theme/clouds");
editor.session.setMode("ace/mode/scheme");
editor.setOption("minLines", 1);
editor.setOption("maxLines", 1);
editor.setOption("fontSize", 24);
editor.setOption("showLineNumbers", false);
editor.setOption("showGutter", false);

editor.container.style.background = "white";

editor.focus();

let container = initializeSVG();
let i = 0;
let data = [];
let starts = [0];

$("#editor").keydown(function (e) {
    if (e.keyCode === 13) {
        e.preventDefault();
    }
});

$("#code-form").submit(function (e) {
    e.preventDefault();
    $.post( "./process2", { code: editor.getValue() }).done(function (_data) {
        i = 0;
        data = _data;
        display(i);
    });
});

$("#prev").click(function () {
    i = Math.max(i - 1, 0);
    display(i);
});

$("#next").click(function () {
    i = Math.min(i + 1, data.length - 1);
    display(i);
});

function display(i) {
    container.clear();
    starts = [0];
    _display(data[i], container, 10, 10, 0);
}

function _display(data, container, x, y, level) {
    let charHeight = 32;
    let charWidth = 14.4;

    let color;
    switch (data["transition_type"]) {
        case "UNEVALUATED": color = "#536dff"; break;
        case "EVALUATING": color = "#ff0f00"; break;
        case "EVALUATED": color = "#44ff51"; break;
        case "APPLYING": color = "#ffa500"; break;
    }

    let rect = container.rect(data["str"].length*charWidth + 10, charHeight + 10)
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
        if (child["transition_type"] !== "UNEVALUATED") {
            container.line(x + xDelta + parent_len / 2, y + charHeight + 5,
                           Math.max(x + xDelta, starts[level + 1]) + child["str"].length * charWidth / 2 + 5,
                            y + 110)
                     .stroke({ width: 3, color: "#c8c8c8"}).back();
            _display(child, container, Math.max(x + xDelta, starts[level + 1]), y + 100, level + 1);
        }
        xDelta += parent_len + charWidth;
    }
}

function initializeSVG() {
    return SVG('drawarea').size($(".starter-template").width(), 1000);
}