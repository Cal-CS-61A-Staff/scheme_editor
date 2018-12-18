import {charWidth, charHeight} from "./measure";

export { display_env };

function display_env(environments, container, i) {
    container.clear();

    let curr_y = 10;

    for (let frame of environments) {
        let out = "Frame " + frame.name + ": " + frame.label + " [parent = " + frame.parent + "]\n";
        let maxlen = out.length;
        let k;
        for (k = 0; k !== frame["bindings"].length; ++k) {
            if (frame["bindings"][k][0] > i) {
                break;
            }
            let line = "   " + frame["bindings"][k][1][0] + ": " + frame["bindings"][k][1][1] + "\n";
            maxlen = Math.max(maxlen, line.length);
            out += line;
        }
        if (k === 0) {
            continue;
        }
        let text = container.text(out).font("family", "Monaco, monospace").font("size", 14).dx(25).dy(curr_y);
        let rect = container.rect(maxlen * charWidth + 10, charHeight * (k + 1) + 10)
            .dx(15).dy(curr_y)
            .stroke({color: "#000000", width: 2})
            .fill({color: "#FFFFFF"})
            .radius(10).back();

        curr_y += charHeight * (k + 1) + 20;
    }
}