import * as substitution_tree from "./substitution_tree";
import * as env_diagram from "./env_diagram";
import * as editor from "./editor";
import * as test_results from "./test_results";
import * as output from "./output";
import {states, saveState, make_new_state} from "./state_handler";
import {init_complete, request_update} from "./event_handler";

export {init, open, notify_open, notify_close, open_prop, getLayout, setLayout};

let layout;

let containers = {
    "substitution_tree": new Map(),
    "env_diagram": new Map(),
    "output": new Map(),
    "editor": new Map(),
    "test_results": new Map(),
    "turtle_graphics": new Map()
};

const open_prop = new Map([
    ["editor", "editor_open"],
    ["output", "out_open"],
    ["substitution_tree", "sub_open"],
    ["turtle_graphics", "turtle_open"],
    ["env_diagram", "env_open"],
    ["test_results", "tests_open"]
]);

function notify_open(type, component, id) {
    containers[type].set(id, component);
}

function notify_close(type, component, id) {
    containers[type].delete(id);
    if (type === "editor") {
        for (let type of open_prop.keys()) {
            if (containers[type].has(id)) {
                containers[type].get(id).close();
            }
        }
        states[id] = make_new_state();
        setTimeout(saveState, 0);
    }
}

function open(type, index) {
    let config = {
        type: "component",
        componentName: type,
        componentState: {id: index},
        height: 40,
        width: 20,
    };

    if (states[index][open_prop.get(type)]) {
        let container = containers[type].get(index);
        container.parent.parent.setActiveContentItem(container.parent);
        request_update();
        return;
    }

    states[index][open_prop.get(type)] = true;

    let pos;
    let friends;

    if (type === "editor" || type === "substitution_tree") {
        pos = "column";
        friends = [type, "editor", "substitution_tree"]
    } else if (type === "test_results") {
        pos = "row";
        friends = [];
    } else {
        // output, visualizations
        pos = "column";
        friends = [type, "env_diagram", "output"];
    }

    let ok = false;
    for (let friend of friends) {
        if (containers[friend].size === 0) {
            continue;
        }
        let lastElem = Array.from(containers[friend].values()).pop();
        lastElem.parent.parent.addChild(config);
        ok = true;
        break;
    }

    if (!ok) {
        if (layout.root.contentItems[0].config.type !== pos) {
            let curr_config = layout.toConfig();
            curr_config.content[0] = {
                content: [curr_config.content[0], config],
                isClosable: true,
                reorderEnabled: true,
                title: "",
                type: pos,
            };
            saveState(true, JSON.stringify(curr_config)).then(
                window.location.reload.bind(window.location));
        } else {
            layout.root.contentItems[0].addChild(config);
        }
    }

    request_update();
}

function getLayout() {
    return JSON.stringify(layout.toConfig());
}

function setLayout(stored_layout) {
    layout = new GoldenLayout(JSON.parse(stored_layout), $("#body"));
}

function init() {
    let config = {
        settings: {
            showPopoutIcon: false,
            showMaximiseIcon: false,
            showCloseIcon: true,
        },
        content: [{
            type: 'stack',
            content: [],
        }]
    };
    let decoded = $.parseJSON(start_data);
    for (let i = 0; i !== decoded["files"].length; ++i) {
        config.content[0].content.push({
            type: 'component',
            componentName: 'editor',
            componentState: {id: i},
            isClosable: false,
        });
    }
    if (layout === undefined) {
        layout = new GoldenLayout(config, $("#body"));
    }

    $(window).resize(function () {
        layout.updateSize($("#body").width(), $("#body").height());
    });

    substitution_tree.register(layout);
    env_diagram.register(layout);
    editor.register(layout);
    test_results.register(layout);
    output.register(layout);

    layout.init();
    init_complete();

    return layout;
}
