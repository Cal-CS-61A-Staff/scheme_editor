define(["state_handler"], function (state_handler) {
    let states = state_handler.states;

    function register(myLayout) {
        myLayout.registerComponent('test_results', function (container, componentState) {
            container.getElement().on("update", function () {
                let data = states[componentState.id].test_results;
                container.getElement().html(`<div id="accordion"> </div>`);
                let expanded = false;
                for (let entry of data) {
                    let random_id = Math.random().toString(36).replace(/[^a-z]+/g, '');
                    let card_style = entry.passed ? "bg-success" : "bg-danger";
                    let hideshow = (!expanded && !entry.passed) ? "show" : "hide";
                    expanded |= !entry.passed;
                    $("#accordion").append(`
                    <div class="card ">
                        <div class="card-header ${card_style} text-white" id="${random_id + "x"}" data-toggle="collapse" 
                        data-target="#${random_id}"> ${entry.problem} </div>
                        <div id="${random_id}" class="collapse ${hideshow}" aria-labelledby="${random_id + "x"}" data-parent="#accordion">
                        <div class="card-body" style="padding: 5px">
                            <table class="table table-sm table-hover">
                                <tbody>
                                </tbody>
                          </table>
                          </div>
                        </div>
                    </div>
                    `);

                    for (let i = 0; i !== entry.suites.length; ++i) {
                        for (let j = 0; j !== entry.suites[i].length; ++j) {
                            let test = entry.suites[i][j];
                            let pass_string = (test.passed ? "Passed!" : "Failed!");
                            let class_string = (test.passed ? "" : "font-bold");
                            $("#accordion").children().last().find("tbody").append(`
                            <tr class="${class_string}">
                                <td class="align-middle">Suite ${i + 1}, Case ${j + 1}</td> 
                                <td class="align-middle">${pass_string}</td> 
                                <td class="text-right"> <button class="btn btn-secondary"> View Case </button> </td>
                            </tr>`);
                            $(`#${random_id}`).find(".btn").last().click(function () {
                                let index = states.length;
                                let new_state = jQuery.extend({}, base_state);
                                new_state.file_name = temp_file;
                                new_state.file_content = test.code;
                                states.push(new_state);
                                let config = {
                                    type: "component",
                                    componentName: "editor",
                                    componentState: {id: index}
                                };
                                states[index].tests_open = true;
                                myLayout.root.contentItems[0].addChild(config);
                                $("#fileChooserModal").modal("hide");
                            });
                        }
                    }
                }
            });

            container.getElement().on("click", function () { });

            container.on("destroy", function () {
                states[componentState.id].tests_open = false;
            });

            container.on("open", function () {});
        });
    }
    return {
        register: register,
    }
});