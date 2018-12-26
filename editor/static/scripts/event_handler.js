import {notify_close, notify_open, open_prop} from "./layout";
import {saveState, states} from "./state_handler";

export {request_update, make, begin_slow, end_slow, init_complete}

function request_update() {
    $("*").trigger("update");
}

function make(container, type, id) {
    container.on("open", function () {
        notify_open(type, container, id);
        if (!initializing) {
            saveState();
        }
    });

    container.on("destroy", function () {
        notify_close(type, container, id);
        states[id][open_prop.get(type)] = false;
        saveState();
    });
}

let timer;

function begin_slow() {
    console.log("SHOWING");
    timer = setTimeout(function() {
        $("#loadingModal").modal("show");
        timer = -1;
    }, 1000);
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