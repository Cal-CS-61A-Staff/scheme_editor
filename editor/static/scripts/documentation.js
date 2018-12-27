import {end_slow} from "./event_handler";
import {states} from "./state_handler";

export {init}

function init() {
    $.post("./documentation_search", {}).done(
        function (data) {
            data = $.parseJSON(data);
            console.log(data);
            $("#documentation-search").select2({
                data: data,
                placeholder: "Search documentation",
                allowClear: true,
                width: '100%'
            });
        });
}