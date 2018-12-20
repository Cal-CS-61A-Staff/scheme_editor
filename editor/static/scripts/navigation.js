import * as state_handler from "./state_handler";
import {states} from "./state_handler";
import {request_update} from "./event_handler";

export {init_events};

function next_expr(i) {
    states[i].expr_i = Math.min(states[i].expr_i + 1, states[i].states.length - 1);
    states[i].start = states[i].states[states[i].expr_i][0];
    states[i].end = states[i].states[states[i].expr_i][1];
    states[i].index = states[i].start;
    // state_handler.saveState();
    request_update();
}

function prev_expr(i) {
    states[i].expr_i = Math.max(states[i].expr_i - 1, 0);
    states[i].start = states[i].states[states[i].expr_i][0];
    states[i].end = states[i].states[states[i].expr_i][1];
    states[i].index = states[i].start;
    // state_handler.saveState();
    request_update();
}

function next_i(i) {
    states[i].index += 1;
    if (states[i].index === states[i].end && states[i].expr_i !== states[i].states.length - 1) {
        next_expr(i);
    } else {
        states[i].index = Math.min(states[i].index, states[i].end - 1);
    }
    // state_handler.saveState();
    request_update();
}

function prev_i(i) {
    states[i].index -= 1;
    if (states[i].index === states[i].start - 1 && states[i].expr_i !== 0) {
        prev_expr(i);
        states[i].index = states[i].end - 1;
    } else {
        states[i].index = Math.max(states[i].index, states[i].start);
    }
    // state_handler.saveState();
    request_update();
}

function init_events() {
    console.log("init events!");
    $("#body").on("click", ".prev", function (e) {
        prev_i($(e.target).data("id"));
    });

    $("#body").on("click", ".next", function (e) {
        console.log("Next!");
        next_i($(e.target).data("id"));
    });

    $("#body").on("click", ".prev-expr", function (e) {
        prev_expr($(e.target).data("id"));
    });

    $("#body").on("click", ".next-expr", function (e) {
        next_expr($(e.target).data("id"));
    });
}