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

    for (let frame of environments) {
        let maxlen = 0;
        let k;
        for (k = 0; k !== frame["bindings"].length; ++k) {
            if (frame["bindings"][k][0] > i) {
                break;
            }
            let line = "   " + frame["bindings"][k][2][0] + ": \n";
            maxlen = Math.max(maxlen, line.length);
            container.text(line).font("family", "Monaco, monospace").font("size", 14).dx(35).dy(curr_y + charHeight * (k + 1));
            display_elem(100, curr_y + charHeight * (k + 1), frame["bindings"][k][2], heap, container, true)
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

function calc_length(elem) {
    if (elem[0]) {
        return charWidth * 1.5;
    } else {
        return charWidth * elem[1].length + 5;
    }
}

function display_elem(x, y, id, all_data, container, at_end) {
    console.log(id);
    console.log(all_data);
    if (id[0]) {
        console.log(all_data[id[1]]);
        // non atomic
        let len = 5;
        if (at_end) {
            container.line(x, y + charHeight / 2 + 5 / 2, x + 20, y + charHeight / 2 + 5 / 2)
                .stroke({width: 3, color: "#c8c8c8"}).back();
            x += 20;
        } else {
            console.log("atom")
        }
        let i = 0;
        for (let elem of all_data[id[1]]) {
            i += 1;
            display_elem(x + len, y, elem, all_data, container, i === all_data[id[1]].length);
            len += calc_length(elem);
        }
        container.rect(len, charHeight + 5)
            .dx(x).dy(y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();
    } else {
        // atomic
        container.text(id[1]).font("family", "Monaco, monospace").font("size", 14).dx(x).dy(y);
    }
}