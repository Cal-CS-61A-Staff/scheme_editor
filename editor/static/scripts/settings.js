import {saveState} from "./state_handler";

export {init, hide_return_frames, getAllSettings, setAllSettings};

function init() {
    $("#settings-btn").click(function () {
        $("#settingsModal").modal("show");
    });
    $('#settingsModal').on('hide.bs.modal', function (e) {
        saveState();
    });
    $("#stop-editor-btn").on("click", () => {
        $.post("/kill");
    });
}

function hide_return_frames() {
    return $("#hideReturnFramesCheckbox").prop('checked');
}

function getAllSettings() {
    return {
        "return_frames": hide_return_frames()
    }
}

function setAllSettings(data) {
    $("#hideReturnFramesCheckbox").prop('checked', data["return_frames"]);
}