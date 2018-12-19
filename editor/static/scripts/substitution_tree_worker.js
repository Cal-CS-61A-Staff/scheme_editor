import * as state_handler from "./state_handler";
import * as measure from "./measure";
import {states} from "./state_handler";
import {charWidth} from "./measure";
import {charHeight} from "./measure";

export { display_tree };

function get_i(all_data, curr, i) {
    let labels = [
        ["transitions", "transition_type"],
        ["strs", "str"],
        ["parent_strs", "parent_str"],
    ];
    let data = {};
    for (let label of labels) {
        for (let val of all_data[curr][label[0]]) {
            if (val[0] > i) {
                break;
            }
            data[label[1]] = val[1];
        }
    }

    let j;

    for (j = 0; j < all_data[curr]["children"].length - 1; ++j) {
        if (all_data[curr]["children"][j + 1][0] > i) {
            break;
        }
    }

    data["children"] = [];
    for (let child of all_data[curr]["children"][j][1]) {
        data["children"].push(get_i(all_data, child, i));
    }
    return data;
}

function display_tree(id, svg) {
    console.log(id);
    _display_tree(
        get_i(
            states[id].states[states[id].expr_i][2],
            states[id].roots[states[id].expr_i],
            states[id].index),
        svg, 10, 10, 0, [0]);
}

function _display_tree(data, container, x, y, level, starts) {
    let color;
    switch (data["transition_type"]) {
        case "UNEVALUATED":
            color = "#536dff";
            break;
        case "EVALUATING":
            color = "#ff0f00";
            break;
        case "EVALUATED":
            color = "#44ff51";
            break;
        case "APPLYING":
            color = "#ffa500";
            break;
    }

    let rect = container.rect(data["str"].length * charWidth + 10, charHeight + 10)
        .dx(x - 5).dy(y)
        .stroke({color: color, width: 2})
        .fill({color: "#FFFFFF"})
        .radius(10);

    let parent = container.text(data["str"]).font("family", "Monaco, monospace").font("size", 14).dx(x).dy(y);
    let xDelta = charWidth;

    // if (parent.length() !== 0) {
    //     charWidth = parent.length() / data["str"].length;
    // }

    starts[level] = x + charWidth * (data["str"].length + 1);
    for (let child of data["children"]) {
        if (starts.length === level + 1) {
            starts.push([10]);
        }
        let parent_len = child["parent_str"].length * charWidth;
        container.line(x + xDelta + parent_len / 2, y + charHeight + 5,
            Math.max(x + xDelta - 100000, starts[level + 1]) + child["str"].length * charWidth / 2 + 5,
            y + 110)
            .stroke({width: 3, color: "#c8c8c8"}).back();
        _display_tree(child, container, Math.max(x + xDelta - 100000, starts[level + 1]), y + 100, level + 1, starts);
        xDelta += parent_len + charWidth;
    }
}