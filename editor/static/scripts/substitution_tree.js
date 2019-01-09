import * as state_handler from "./state_handler";
import * as substitution_tree_worker from "./substitution_tree_worker"
import {states} from "./state_handler";
import {notify_open} from "./layout";
import {make} from "./event_handler";

export { register };

function register(myLayout) {
    myLayout.registerComponent('substitution_tree', function (container, componentState) {
        container.getElement().html(`
            <div class="content">
                <div class="header">
                <div class="btn-group">
                    <button type="button" data-toggle="tooltip"
                            title="Step backward." data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary prev">
                            <i class="fas fa-arrow-left"></i>
                    </button>          
                    <button type="button" data-toggle="tooltip"
                            title="Step forward." data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary next">
                        <i class="fas fa-arrow-right"></i>
                    </button>
                </div>            
                <div class="btn-group">
                    <button type="button" data-toggle="tooltip"
                            title="Go to the start of the evaluation of the current expression." 
                            data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary prev-expr">
                        Restart Expr
                    </button>          
                    <button type="button" data-toggle="tooltip"
                            title="Finish evaluating the current expression." 
                             data-id="${componentState.id}" 
                            class="btn btn-sm btn-secondary next-expr">
                        Complete Expr
                    </button>
                </div>
                </div>
                <div class="tree">
                    <svg></svg>
                </div>
            </div>
        `);
        setTimeout(function () { $('[data-toggle="tooltip"]').tooltip(); }, 0);

        make(container, "substitution_tree", componentState.id);

        let rawSVG = container.getElement().find(".tree > svg").get(0);
        // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        let svg = SVG.adopt(rawSVG).size(container.width, container.height);
        console.log("adopted");
        let ready = false;

        container.getElement().find(".tree").on("update", function (e) {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            if (ready) {
                svg.clear();
            } else {
                ready = true;
                console.log("SKIP");
            }
            substitution_tree_worker.display_tree(componentState.id, svg);
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });

        container.getElement().find(".tree").on("reset", function () {
            svgPanZoom(rawSVG).reset();
            console.log("reset!");
        });

        container.on("resize", function () {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            svg.size(container.width, container.height);
            console.log("ready!");
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });
    });
}