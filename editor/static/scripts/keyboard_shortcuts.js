export {init};


function init() {
    $(document).keydown(function (event) {
        if ((event.ctrlKey || event.metaKey) && event.keyCode === 83) {
            event.preventDefault();
            $("*").trigger("save");
        }
    });
}