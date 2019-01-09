import * as env_diagram_worker from "./env_diagram_worker";
import {states} from "./state_handler";
import {make, request_update} from "./event_handler";

export { register };

function register(myLayout) {
    myLayout.registerComponent('env_diagram', function (container, componentState) {
        let random_id = Math.random().toString(36).replace(/[^a-z]+/g, '');
        container.getElement().html(`
        <div class="content">
            <div class="header diagram-header">
                <div class="btn-group">
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary prev-update">Prev</button>          
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary next-update">Next</button>
                </div>            
                <div class="btn-group">
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary prev-expr">Restart Frame</button>          
                    <button type="button" data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary next-expr">Complete Frame</button>
                </div>
                <div class="btn-group float-right">
                    <div class="custom-control custom-checkbox header-checkbox">
                      <input type="checkbox" class="custom-control-input" id="${random_id}">
                      <label class="custom-control-label" for="${random_id}">Show box and pointer diagrams</label>
                    </div>
                </div>
            </div>
            <div class="envs">
                <svg></svg>
            </div>
        </div>
        `);

        make(container, "env_diagram", componentState.id);

        let rawSVG = container.getElement().find(".envs > svg").get(0);
        // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        let svg = SVG.adopt(rawSVG).size(container.width, container.height);

        container.getElement().find(".envs").on("update", function () {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            svg.clear();
            // env_diagram_worker.display_env(states[componentState.id].environments, svg, states[componentState.id].index);
            env_diagram_worker.display_env_pointers(
                states[componentState.id].environments,
                states[componentState.id].heap,
                svg,
                states[componentState.id].index,
                $(`#${random_id}`).is(":checked"));
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });

        container.getElement().find(".envs").on("reset", function () {
            svgPanZoom(rawSVG).reset();
        });

        container.getElement().find(`#${random_id}`).on("click", function () {
            request_update();
        });

        container.on("resize", function () {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            svg.size(container.width, container.height);
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });

        container.on("shown", function () {
            request_update();
        })
    });
}