define(["./substitution_tree", "./env_diagram", "./editor", "./test_results", "./output", "./state_handler"], function (substitution_tree, env_diagram, editor, test_results, output, state_handler) {
    let states = state_handler.states;

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
        let myLayout;
        let savedLayout = localStorage.getItem('savedLayout');
        if (savedLayout !== null) {
            myLayout = new GoldenLayout(JSON.parse(savedLayout), $("#body"));
        } else {
            myLayout = new GoldenLayout(config, $("#body"));
        }

        myLayout.on('stateChanged', function () {
            localStorage.setItem('savedLayout', JSON.stringify(myLayout.toConfig()));
            localStorage.setItem('savedState', JSON.stringify(states));
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
    return {
        init: init,
    }
});