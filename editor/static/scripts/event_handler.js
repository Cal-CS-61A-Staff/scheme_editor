import {notify_close, notify_open, open_prop} from "./layout";
import {saveState, states, temp_file} from "./state_handler";

export {request_update, make, begin_slow, end_slow, init_complete}

const type_title = {
    "env_diagram": "Environments",
    "substitution_tree": "Debugger",
    "output": "Output",
    "test_results": "Test Results"
};

function request_update() {
    $("*").trigger("update");
}

function make(container, type, id) {
    let title;
    if (states[id].file_name.startsWith(temp_file)) {
        title = states[id].file_name.slice(temp_file.length);
    } else {
        title = states[id].file_name;
    }

    if (type !== "editor") {
        title = type_title[type] + " (" + title + ")";
    }

    container.setTitle(title);

    container.on("open", function () {
        notify_open(type, container, id);
        if (!initializing) {
            setTimeout(saveState, 0);
        }
    });

    container.on("destroy", function () {
        notify_close(type, container, id);
        states[id][open_prop.get(type)] = false;
        setTimeout(saveState, 0);
    });
}

let timer;

function begin_slow() {
    console.log("SHOWING");
    timer = setTimeout(function() {
        $("#loadingModal").modal("show");
        timer = -1;
    }, 300);
}

function end_slow() {
    console.log("HIDING");
    if (timer) {
        clearInterval(timer);
        timer = undefined;
    }
    $("#loadingModal").modal("hide");
}

let initializing = true;

function init_complete() {
    initializing = false;
}