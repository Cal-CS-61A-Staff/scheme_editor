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
    if (starts.length === level) {
        starts.push([10]);
    }
    x = Math.max(x, starts[level]);
    let parent = container.text(data["str"]).font("family", "Monaco").font("size", 24).dx(x).dy(y);

    let charWidth = parent.length() / data["str"].length;
    let charHeight = parent.leading();
    let xDelta = charWidth;

    starts[level] = x + parent.length() + charWidth;

    for (let child of data["children"]) {
        console.log("Drawing object with p_string=" + child["parent_str"] + " and str=" + child["str"])
        let parent_len = child["parent_str"].length * charWidth;
        let rect = container.rect(parent_len, 50).dx(x + xDelta).dy(y).opacity(0.5);
        if (child["transition_type"] !== "UNEVALUATED") {
            _display(child, container, x + xDelta, y + 100, level + 1);
        }
        xDelta += parent_len + charWidth;
    }
}

function initializeSVG() {
    return SVG('drawarea').size($(".starter-template").width(), 1000);
}