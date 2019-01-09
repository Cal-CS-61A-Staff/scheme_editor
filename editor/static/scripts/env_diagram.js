import * as env_diagram_worker from "./env_diagram_worker";
import {states} from "./state_handler";
import {make, request_update} from "./event_handler";

export { register };

function register(myLayout) {
    myLayout.registerComponent('env_diagram', function (container, componentState) {
        let random_id = Math.random().toString(36).replace(/[^a-z]+/g, '');
        container.getElement().html(`
        <div class="content">
        <div class="header">
            <div class="btn-toolbar bg-light">
                <button type="button" data-toggle="tooltip"
                        title="Step backward." data-id="${componentState.id}" 
                        class="btn btn-sm btn-light prev-update">
                        <i class="fas fa-arrow-left"></i>
                </button>          
                <button type="button" data-toggle="tooltip"
                        title="Step forward." data-id="${componentState.id}" 
                        class="btn btn-sm btn-light next-update">
                    <i class="fas fa-arrow-right"></i>
                </button>
                <button type="button" data-toggle="tooltip"
                        title="Go back to the opening of the frame." 
                        data-id="${componentState.id}" 
                        class="btn btn-sm btn-light prev-expr">
                    <i class="fas fa-angle-double-left"></i>
                </button>          
                <button type="button" data-toggle="tooltip"
                        title="Skip to the exit of the frame." 
                        data-id="${componentState.id}" 
                        class="btn btn-sm btn-light next-expr">
                    <i class="fas fa-angle-double-right"></i>
                </button>
                <span data-toggle="tooltip" data-target="${random_id}"
                      title="Toggle box and pointer visualization.">
                    <div class="btn-group-toggle" data-toggle="buttons">
                      <label class="btn btn-sm btn-light" id="${random_id}">
                        <input type="checkbox" autocomplete="off" class="box-pointer-checkbox">
                        <i class="fas fa-th-large "></i>
                      </label>
                    </div>
                </span>
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
                container.getElement().find(".box-pointer-checkbox").is(":checked"));
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
            setTimeout(request_update, 0);
            console.log("CLICKING");
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