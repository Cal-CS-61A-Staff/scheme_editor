import * as substitution_tree_worker from "./substitution_tree_worker"
import {
    make
} from "./event_handler";

export {
    register
};

function register(myLayout) {
    myLayout.registerComponent('substitution_tree', function (container, componentState) {
        container.getElement().html(`
            <div class="content">
                <div class="header">
                <div class="btn-toolbar bg-light">
                    <button type="button" data-toggle="tooltip"
                            title="Step backward." data-id="${componentState.id}" 
                            class="btn btn-sm btn-light prev">
                            <i class="fas fa-arrow-left"></i>
                    </button>          
                    <button type="button" data-toggle="tooltip"
                            title="Step forward." data-id="${componentState.id}" 
                            class="btn btn-sm btn-light next">
                        <i class="fas fa-arrow-right"></i>
                    </button>
                    <button type="button" data-toggle="tooltip"
                            title="Go to the start of the evaluation of the current expression." 
                            data-id="${componentState.id}" 
                            class="btn btn-sm btn-light restart-eval">
                        <i class="fas fa-angle-double-left"></i>
                    </button>          
                    <button type="button" data-toggle="tooltip"
                            title="Finish evaluating the current expression." 
                            data-id="${componentState.id}" 
                            class="btn btn-sm btn-light finish-eval">
                        <i class="fas fa-angle-double-right"></i>
                    </button>          
                    <button type="button" data-toggle="tooltip"
                            title="Go to the start of the program.." 
                            data-id="${componentState.id}" 
                            class="btn btn-sm btn-light go-to-start">
                        <i class="fas fa-arrow-alt-circle-left"></i>
                    </button>          
                    <button type="button" data-toggle="tooltip"
                            title="Finish executing the program." 
                            data-id="${componentState.id}" 
                            class="btn btn-sm btn-light go-to-end">
                        <i class="fas fa-arrow-alt-circle-right"></i>
                    </button>
                </div>
                </div>
                <div class="tree">
                    <svg></svg>
                </div>
                <div class="flag"></div>
            </div>
        `);

        make(container, "substitution_tree", componentState.id);

        let rawSVG = container.getElement().find(".tree > svg").get(0);
        let svg = SVG.adopt(rawSVG).size(container.width, container.height);
        console.log("adopted");
        let ready = false;

        container.getElement().find(".flag").on("update", async () => {
            let zoom = svgPanZoom(rawSVG).getZoom();
            let pan = svgPanZoom(rawSVG).getPan();
            svgPanZoom(rawSVG).destroy();
            if (ready) {
                svg.clear();
            } else {
                ready = true;
                console.log("SKIP");
            }
            console.log("starting");

            await substitution_tree_worker.display_tree(componentState.id, svg);

            svgPanZoom(rawSVG, {
                fit: false,
                zoomEnabled: true,
                center: false,
                controlIconsEnabled: true
            });

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
            svgPanZoom(rawSVG, {
                fit: false,
                zoomEnabled: true,
                center: false,
                controlIconsEnabled: true
            });
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });
    });
}