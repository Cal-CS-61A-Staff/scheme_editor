define(["./state_handler", "./substitution_tree_worker"], function (state_handler, substitution_tree_worker) {
    let states = state_handler.states;

    function register(myLayout) {
        myLayout.registerComponent('substitution_tree', function (container, componentState) {
            container.getElement().html(`
                <div class="content">
                    <div class="header">
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-secondary prev">Prev</button>          
                        <button type="button" class="btn btn-sm btn-secondary next">Next</button>
                    </div>            
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-secondary prev-expr">Prev Expr</button>          
                        <button type="button" class="btn btn-sm btn-secondary next-expr">Next Expr</button>
                    </div>
                    </div>
                    <div class="tree">
                        <svg></svg>
                    </div>
                </div>
        
            `);

            let rawSVG = container.getElement().find(".tree > svg").get(0);
            // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            let svg = SVG.adopt(rawSVG).size(container.width, container.height);

            container.getElement().find(".tree").on("update", function (e) {
                let zoom = svgPanZoom(rawSVG).getZoom();
                let pan = svgPanZoom(rawSVG).getPan();
                svgPanZoom(rawSVG).destroy();
                svg.clear();
                substitution_tree_worker.display_tree(componentState.id, svg);
                svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
                if (isNaN(zoom)) {
                    svgPanZoom(rawSVG).reset();
                } else {
                    svgPanZoom(rawSVG).zoom(zoom);
                    svgPanZoom(rawSVG).pan(pan);
                }
            });

            container.getElement().find(".tree").on("reset", function (e) {
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
                states[componentState.id].sub_open = false;
            });

            container.getElement().find(".prev").click(function () {
                prev_i(componentState.id);
            });

            container.getElement().find(".next").click(function () {
                next_i(componentState.id);
            });

            container.getElement().find(".prev-expr").click(function () {
                prev_expr(componentState.id);
            });

            container.getElement().find(".next-expr").click(function () {
                next_expr(componentState.id);
            });
        });
    }
    return {
        register: register,
    }
});