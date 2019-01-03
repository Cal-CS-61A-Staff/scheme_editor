export { init };

function init() {
    $("#settings-btn").click(function () {
        $("#settingsModal").modal("show");
    });
}