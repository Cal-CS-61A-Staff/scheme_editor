import {notify_close, notify_open, open_prop} from "./layout";
import {saveState, states} from "./state_handler";

export {request_update, make}

function request_update() {
    $("*").trigger("update");
}

function make(container, type, id) {
    container.on("open", function () {
        notify_open(type, container, id);
        saveState();
    });

    container.on("destroy", function () {
        notify_close(type, container, id);
        states[id][open_prop.get(type)] = false;
        saveState();
    });
}
