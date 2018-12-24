import {charWidth, charHeight} from "./measure";

export {display_env, display_env_pointers};

function display_env(environments, container, i) {
    container.clear();

    let curr_y = 10;

    for (let frame of environments) {
        let maxlen = 0;
        let k;
        for (k = 0; k !== frame["bindings"].length; ++k) {
            if (frame["bindings"][k][0] > i) {
                break;
            }
            let line = "   " + frame["bindings"][k][1][0] + ": " + frame["bindings"][k][1][1] + "\n";
            maxlen = Math.max(maxlen, line.length);
            container.text(line).font("family", "Monaco, monospace").font("size", 14).dx(35).dy(curr_y + charHeight * (k + 1));
        }
        if (k === 0) {
            continue;
        }
        let title = "Frame " + frame.name + ": " + frame.label + " [parent = " + frame.parent + "]\n";
        container.text(title).font("family", "Monaco, monospace").font("size", 14).dx(25).dy(curr_y);
        maxlen = Math.max(maxlen, title.length);
        let rect = container.rect(maxlen * charWidth + 10, charHeight * (k + 1) + 10)
            .dx(15).dy(curr_y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();

        curr_y += charHeight * (k + 1) + 20;
    }
}

function display_env_pointers(environments, heap, container, i) {
    container.clear();

    let curr_y = 10;

    let cache = new Map();

    let h = charHeight;
    for (let frame of environments) {
        let maxlen = 0;
        let k;
        for (k = 0; k !== frame["bindings"].length; ++k) {
            if (frame["bindings"][k][0] > i) {
                break;
            }
            let line = "   " + frame["bindings"][k][1][0] + ": \n";
            maxlen = Math.max(maxlen, line.length);
            container.text(line).font("family", "Monaco, monospace").font("size", 14).dx(35).dy(curr_y + charHeight * (k + 1));
            let depth = display_elem(
                200,
                h,
                frame["bindings"][k][2],
                heap,
                container,
                0,
                cache) + 1;
            h += depth * (minWidth + 15);
        }
        if (k === 0) {
            continue;
        }
        let title = "Frame " + frame.name + ": " + frame.label + " [parent = " + frame.parent + "]\n";
        // container.text(title).font("family", "Monaco, monospace").font("size", 14).dx(25).dy(curr_y);
        maxlen = Math.max(maxlen, title.length);
        let rect = container.rect(maxlen * charWidth + 10, charHeight * (k + 1) + 10)
            .dx(15).dy(curr_y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();

        curr_y += charHeight * (k + 1) + 20;
    }
}

let minWidth = charWidth * 4 + 5;

function calc_content_length(elem) {
    if (elem[0]) {
        return minWidth;
    } else {
        return Math.max(minWidth, charWidth * elem[1].length + 10);
    }
}

function straight_arrow(container, x1, y1, x2, y2) {
    container.circle(5).dx(x1 - 5 / 2).dy(y1 - 5 / 2);
    let arrow = container
        .polygon('0,0 -10,5 -10,-5')
        .dx(x2).dy(y2)
        .rotate(180 / Math.PI * Math.atan2(y2 - y1, x2 - x1), x2, y2);
    let length = Math.hypot(x2 - x1, y2 - y1);
    container
        .line(x1, y1, x2 + (x1 - x2) / length * 5, y2 + (y1 - y2) / length * 5)
        .stroke({width: 2, color: "#000000"});
}

function curved_arrow(container, x1, y1, x2, y2) {
    straight_arrow(container, x1, y1, x2, y2);
}

// function calc_positions(root, all_data) {
//     let occupied = [];
//     function is_occupied(x, row) {
//         while (occupied.length <= row) {
//             occupied.push([]);
//         }
//         for (let elem of occupied[row]) {
//             if (elem[0] > x) {
//                 break;
//             }
//             if (elem[1] > x) {
//                 return true;
//             }
//         }
//         return false;
//     }
//
//     function _calc_positions(id, row, x) {
//         if
//     }
//     return _calc_positions(root);
// }

function display_elem(x, y, id, all_data, container, depth, cache) {
    console.log(id);
    console.log(all_data);
    console.log(depth);
    if (id[0]) {
        // non atomic
        let x1 = x + minWidth / 2;
        let y1 = y + minWidth / 2;
        if (cache.has(id[1])) {
            curved_arrow(container, x1, y1, ...cache.get(id[1]));
            return 0;
        }
        let x2, y2;
        if (depth === 0) {
            cache.set(id[1], [x, y]);
            x2 = x + minWidth + 15;
            y2 = y + minWidth / 2;
            x = x2;
        } else {
            x2 = x + minWidth / 2;
            y2 = y + (minWidth + 15) * depth;
            y = y2;
        }
        if (all_data[id[1]].length > 1) {
            cache.set(id[1], [x2, y2]);
        } else {
            cache.set(id[1], [x, y + minWidth / 2]);
        }
        straight_arrow(container, x1, y1, ...cache.get(id[1]));
        let pos = 0;
        let lens = [];
        for (let elem of all_data[id[1]]) {
            lens.push(pos);
            pos += calc_content_length(elem);
        }
        let new_depth = 0;
        for (let i = all_data[id[1]].length - 1; i >= 0; --i) {
            if (i !== 0) {
                container.line(x + lens[i], y, x + lens[i], y + minWidth).stroke({color: "#000000", width: 2});
            }
            let elem = all_data[id[1]][i];
            if (i !== all_data[id[1]].length - 1 && elem[0] && !cache.has(elem[1])) {
                new_depth += 1;
            }
            new_depth += display_elem(x + lens[i], y, elem, all_data, container, new_depth, cache);
        }
        if (all_data[id[1]].length > 1) {
            container.rect(pos, minWidth)
                .dx(x).dy(y)
                .stroke({color: "#000000", width: 2})
                .fill({color: "#FFFFFF"}).back();
        }
        // container.text(new_depth.toString(10)).dx(x).dy(y);
        return new_depth;
    } else {
        // atomic
        let width = calc_content_length(id);
        container.text(id[1])
            .font("family", "Monaco, monospace").font("size", 14)
            .cx(x + width / 2)
            .cy(y + minWidth / 2);
        return 0;
    }
}