import * as substitution_tree from "./substitution_tree";
import * as env_diagram from "./env_diagram";
import * as editor from "./editor";
import * as test_results from "./test_results";
import * as output from "./output";
import {states, saveState} from "./state_handler";

export {init, open, notify_open, notify_close};

let layout;

let containers = {
    "substitution_tree": [],
    "env_diagram": [],
    "output": [],
    "editor": [],
    "test_results": [],
};

function notify_open(type, component) {
    console.log(type);
    containers[type].push(component);
}

function notify_close(type, component) {
    containers[type].splice(containers[type].indexOf(component), 1);
}

function open(type, index) {
    console.log("Opening " + type);
    let config = {
        type: "component",
        componentName: type,
        componentState: {id: index},
        height: 40,
        width: 40,
    };

    let open_prop = new Map([
        ["editor", "editor_open"],
        ["output", "out_open"],
        ["substitution_tree", "sub_open"],
        ["turtle_graphics", "turtle_open"],
        ["env_diagram", "env_open"],
        ["test_results", "tests_open"]
    ]);
    console.log(states);

    if (states[index][open_prop.get(type)]) {
        $("*").trigger("update");
        return;
    }

    states[index][open_prop.get(type)] = true;

    let pos;
    let friends;

    if (type === "editor") {
        pos = "column";
        friends = ["editor"]
    } else if (type === "test_results") {
        pos = "row";
        friends = [];
    } else {
        // output, visualizations
        pos = "column";
        friends = [type, "substitution_tree", "env_diagram", "output"];
    }

    let ok = false;
    for (let friend of friends) {
        console.log(friends);
        if (containers[friend].length === 0) {
            continue;
        }
        console.log(containers[friend].slice(-1)[0]);
        containers[friend].slice(-1)[0].parent.parent.addChild(config);
        ok = true;
        break;
    }

    if (!ok) {
        if (layout.root.contentItems[0].config.type !== pos) {
            let curr_config = layout.toConfig();
            console.log(curr_config);
            curr_config.content[0] = {
                content: [curr_config.content[0], config],
                isClosable: true,
                reorderEnabled: true,
                title: "",
                type: pos,
            };
            localStorage.setItem('savedLayout', JSON.stringify(curr_config));
            saveState(window.location.reload.bind(window.location));
        } else {
            layout.root.contentItems[0].addChild(config);
        }
    }

    $("*").trigger("update");
}

function init() {
    let config = {
        settings: {
            showPopoutIcon: false,
            showMaximiseIcon: false,
            showCloseIcon: true,
        },
        content: [{
            type: 'component',
            componentName: 'editor',
            componentState: {id: 0},
            isClosable: false,
        }]
    };
    let savedLayout = localStorage.getItem('savedLayout');
    if (savedLayout !== null) {
        layout = new GoldenLayout(JSON.parse(savedLayout), $("#body"));
    } else {
        layout = new GoldenLayout(config, $("#body"));
    }

    layout.on('stateChanged', function () {
        localStorage.setItem('savedLayout', JSON.stringify(layout.toConfig()));
        // saveState();
    });

    $(window).resize(function () {
        layout.updateSize($("#body").width(), $("#body").height());
    });

    substitution_tree.register(layout);
    env_diagram.register(layout);
    editor.register(layout);
    test_results.register(layout);
    output.register(layout);

    layout.init();

    return layout;
}
