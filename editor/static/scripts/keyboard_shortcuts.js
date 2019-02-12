export {init};


function init() {
    $(document).keydown(function (event) {
        if (event.ctrlKey && event.keyCode === 83) {
            event.preventDefault();
            //action here
            save();
        }
    });
}