export { states, base_state, temp_file, saveState };

let base_state = {
    states: [],
    environments: [],
    moves: [],
    out: "",

    index: 0,
    expr_i: 0,

    start: 0,
    end: 0,
    roots: ["demo"],

    globalFrameID: -1,

    editor_open: false,
    sub_open: false,
    env_open: false,
    turtle_open: false,
    out_open: false,
    tests_open: false,

    test_results: undefined,

    file_name: "",
};

let states = [jQuery.extend({}, base_state)];

let temp_file = "<temporary>";

let savedState = localStorage.getItem("savedState");
if (savedState !== null) {
    states = JSON.parse(savedState);
}

function saveState() {
    localStorage.setItem('savedState', JSON.stringify(states));
}