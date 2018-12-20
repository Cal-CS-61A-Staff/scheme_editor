import {notify_close, notify_open, open_prop} from "./layout";
import {states} from "./state_handler";

export {request_update, make}

function request_update() {
    $("*").trigger("update");
}

function make(container, type, id) {
    container.on("open", function () {
        notify_open(type, container);
    });

    container.on("destroy", function () {
        notify_close(type, container);
        states[id][open_prop[type]] = false;
    });
}
