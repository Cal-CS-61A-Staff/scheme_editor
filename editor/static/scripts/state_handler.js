import {begin_slow, end_slow} from "./event_handler";
import {getLayout, open, setLayout} from "./layout";
import {getAllSettings, setAllSettings} from "./settings";

export {states, temp_file, loadState, saveState, make_new_state};

let base_state = {
    states: {},
    environments: [],
    moves: [],
    out: "",
    heap: {},
    frameUpdates: [],

    index: 0,
    expr_i: 0,

    start: 0,
    end: 0,
    roots: ["demo"],

    globalFrameID: -1,

    editor_open: false,
    sub_open: false,
    env_open: false,
    using_box_pointer: false,
    turtle_open: false,
    out_open: false,
    tests_open: false,

    test_results: undefined,

    file_name: "",
};

let states = [make_new_state()];
states[0].file_name = $.parseJSON(start_data)["file"];

let temp_file = "__";

function make_new_state() {
    return jQuery.extend({}, base_state);
}

function loadState(callback) {
    begin_slow();
    $.post("./load_state", {})
        .done(function (data) {
            end_slow();
            if (data !== "fail") {
                data = $.parseJSON(data);
                states = data.states;
                setLayout(data.layout);
                setAllSettings(data.settings);
            }
            callback();
        });
}

let curr_saving = false;
function saveState(callback, layout=undefined) {
    if (curr_saving) {
        return;
    }
    console.log("saving");
    begin_slow();
    curr_saving = true;
    if (layout === undefined) {
        layout = getLayout();
    }
    console.log(layout);
    $.post("./save_state", {
        state: JSON.stringify({states: states, layout: layout, settings: getAllSettings()}),
    }).done(function () {
        end_slow();
        curr_saving = false;
        if (callback !== undefined) {
            callback();
        }
    });
}