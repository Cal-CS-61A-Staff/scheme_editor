import * as env_diagram_worker from "./env_diagram_worker";
import {states} from "./state_handler";

export { register };

function register(myLayout) {
    myLayout.registerComponent('env_diagram', function (container, componentState) {
        container.getElement().html(`
        <div class="content">
            <div class="header">
            <div class="btn-group">
                <button type="button" data-id="${componentState.id}" 
                        class="btn btn-sm btn-secondary prev">Prev</button>          
                <button type="button" data-id="${componentState.id}" 
                        class="btn btn-sm btn-secondary next">Next</button>
            </div>            
            <div class="btn-group">
                <button type="button" data-id="${componentState.id}" 
                        class="btn btn-sm btn-secondary prev-expr">Prev Expr</button>          
                <button type="button" data-id="${componentState.id}" 
                        class="btn btn-sm btn-secondary next-expr">Next Expr</button>
            </div>
            </div>
            <div class="envs">
                <svg></svg>
            </div>
        </div>
        `);

        let rawSVG = container.getElement().find(".envs > svg").get(0);
        // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        let svg = SVG.adopt(rawSVG).size(container.width, container.height);

        container.getElement().find(".envs").on("update", function () {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            svg.clear();
            env_diagram_worker.display_env(states[componentState.id].environments, svg, states[componentState.id].index);
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

        container.on("destroy", function () {
            states[componentState.id].env_open = false;
        });
    });
}