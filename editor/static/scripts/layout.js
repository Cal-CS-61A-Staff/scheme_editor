import * as substitution_tree from "./substitution_tree";
import * as env_diagram from "./env_diagram";
import * as editor from "./editor";
import * as test_results from "./test_results";
import * as output from "./output";

import {states, saveState} from "./state_handler";

let myLayout;

function open(type, index) {
    let config = {
        type: "component",
        componentName: type,
        componentState: {id: index}
    };

    let open_prop = new Map([
        ["editor", "editor_open"],
        ["output", "out_open"],
        ["substitution_tree", "sub_open"],
        ["turtle_graphics", "turtle_open"],
        ["env_diagram", "env_open"],
        ["test_results", "tests_open"]
    ]);

    if (states[index][open_prop.get(type)]) {
        return;
    }

    states[index][open_prop.get(type)] = true;

    myLayout.root.contentItems[0].addChild(config);
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
            type: 'row',
            content: [{
                type: 'component',
                componentName: 'editor',
                componentState: {id: 0},
                isClosable: false,
            }]
        }]
    };
    let savedLayout = localStorage.getItem('savedLayout');
    if (savedLayout !== null) {
        myLayout = new GoldenLayout(JSON.parse(savedLayout), $("#body"));
    } else {
        myLayout = new GoldenLayout(config, $("#body"));
    }

    myLayout.on('stateChanged', function () {
        localStorage.setItem('savedLayout', JSON.stringify(myLayout.toConfig()));
        saveState()
    });

    $(window).resize(function () {
        myLayout.updateSize($("#body").width(), $("#body").height());
    });

    myLayout.on("initialised", function () {
        $("*").trigger("update");
    });

    substitution_tree.register(myLayout);
    env_diagram.register(myLayout);
    editor.register(myLayout);
    test_results.register(myLayout);
    output.register(myLayout);

    myLayout.init();

    return myLayout;
}

export {init, open};
