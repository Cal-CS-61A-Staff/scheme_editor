define(["substitution_tree", "env_diagram", "editor", "test_results", "output", "state_handler"],
    function (substitution_tree, env_diagram, editor, test_results, output, state_handler) {
        let states = state_handler.states;

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

            states[index][open_prop.get(type)] = true;

            myLayout.root.contentItems[0].addChild(config);
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
                state_handler.saveState()
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
            open: open,
        }
    });