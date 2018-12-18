import * as navigation from "./navigation";
import * as layout from "./layout";
import * as file_opening from "./file_opening";

$(window).on("load", function () {
    navigation.init_events();
    layout.init();
    file_opening.init();

    $("*").trigger("update");
});