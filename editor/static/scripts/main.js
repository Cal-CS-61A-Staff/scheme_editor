define(["layout", "navigation", "file_opening"], function (layout, navigation, file_opening) {
    layout.init();
    navigation.init_events();
    file_opening.init();
});