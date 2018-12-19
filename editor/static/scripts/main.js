import * as navigation from "./navigation";
import * as layout from "./layout";
import * as file_opening from "./file_opening";
import {loadState} from "./state_handler";

$(window).on("load", function () {
    loadState(function () {
        navigation.init_events();
        layout.init();
        file_opening.init();

        $("*").trigger("update");
    });
});