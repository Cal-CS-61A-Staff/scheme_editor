import {saveState} from "./state_handler";

export {init, hide_return_frames, javastyle, getAllSettings, setAllSettings};

function init() {
    $("#settings-btn").click(function () {
        $("#settingsModal").modal("show");
    });
    $('#settingsModal').on('hide.bs.modal', function (e) {
        saveState();
    })
}

function hide_return_frames() {
    return $("#hideReturnFramesCheckbox").prop('checked');
}

function javastyle() {
    return $("#javastyleCheckbox").prop('checked');
}

function getAllSettings() {
    return {
        "return_frames": hide_return_frames(),
        "javastyle": javastyle(),
    }
}

function setAllSettings(data) {
    $("#hideReturnFramesCheckbox").prop('checked', data["return_frames"]);
    $("#javastyleCheckbox").prop('checked', data["javastyle"]);
}