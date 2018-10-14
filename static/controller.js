var editor = ace.edit("editor");
editor.setTheme("ace/theme/dark");
editor.session.setMode("ace/mode/scheme");
editor.setOption("minLines", 1);
editor.setOption("maxLines", 1);
editor.setOption("fontSize", 24);
editor.setOption("showLineNumbers", false);
editor.setOption("showGutter", false);

$("#editor").keydown(function (e) {
// Enter was pressed without shift key
    if (e.keyCode === 13) {
        e.preventDefault();
    }
});

$("#code-form").submit(function (e) {
    e.preventDefault();
    $.post( "./process2", { code: editor.getValue() } );
});