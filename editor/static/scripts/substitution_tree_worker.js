import {
	states
} from "./state_handler";
import {
	charWidth
} from "./measure";
import {
	charHeight
} from "./measure";

export {
	display_tree,
	get_i
};

function locate(data) {
	_locate(data, data["parent_str"], 0, 0, 0);
	console.log(data);
	data["root"] = true;
}

function _locate(elem, base_str, i, row, col) {
    console.log(elem["str"] + " " + i + " " + row + " " + col);
	let pos = 0;
	let start_row = -1;
	let start_col = -1;
	let start_i = -1;

	let max_col = -1;

	elem["root"] = (elem["parent_str"] !== elem["str"]);

	while (base_str[i] === " " || base_str[i] === "\n" || base_str[i] === elem["parent_str"][pos]) {
		if (base_str[i] === elem["parent_str"][pos] && start_row === -1) {
			start_row = row;
			start_col = col;
			max_col = col;
			start_i = i;
		}
		if (base_str[i] === elem["parent_str"][pos]) {
			++pos;
		}
		if (pos === elem["parent_str"].length) {
			break;
		}
		if (base_str[i] === "\n") {
			++row;
			col = 0;
		} else {
			++col;
			max_col = Math.max(max_col, col);
		}
		++i;
	}

	elem["start_row"] = start_row;
	elem["start_col"] = start_col;
	elem["start_i"] = start_i;
	elem["end_row"] = row;
	elem["end_col"] = max_col;
	elem["end_i"] = i;

	let child_i = start_i + 1;
	let child_row = start_row;
	let child_col = start_col + 1;
	for (let child of elem["children"]) {
		_locate(child, base_str, child_i, child_row, child_col);
		child_i = child["end_i"] + 1;
		child_row = child["end_row"];
		child_col = child["end_col"] + 1;
	}
}

function get_i(all_data, curr, i, callback) {
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

	data["id"] = curr;

	data["children"] = [];
	for (let child of all_data[curr]["children"][j][1]) {
		data["children"].push(get_i(all_data, child, i));
	}
	if (callback !== undefined) {
		$.post("./reformat", {
			code: [data["parent_str"]],
		}).done(function (response) {
			response = $.parseJSON(response);
			data["parent_str"] = response["formatted"];
			$.post("./reformat", {
				code: [data["str"]],
			}).done(function (response) {
				response = $.parseJSON(response);
				data["str"] = response["formatted"];
				locate(data);
				callback(data);
			});
		});
	}
	return data;
}

function display_tree(id, svg, callback) {
	get_i(
		states[id].states[states[id].expr_i][2],
		states[id].roots[states[id].expr_i],
		states[id].index,
		(data) => {
			_display_tree(data, svg);
			callback();
		}
	);
}

function _display_tree(data, container) {
	let color;
	switch (data["transition_type"]) {
		case "UNEVALUATED":
			color = "#536dff";
            color = "transparent";
			break;
		case "EVALUATING":
			color = "#ff0f00";
            // color = "transparent";
			break;
		case "EVALUATED":
			color = "#44ff51";
			break;
		case "APPLYING":
			color = "#ffa500";
			break;
	}

	let width = charWidth * (data["end_col"] - data["start_col"] + 1);
	let height = charHeight * (data["end_row"] - data["start_row"] + 1);

	let x = data["start_col"] * charWidth;
	let y = data["start_row"] * charHeight;

	let rect = container.rect(width, height).dx(x).dy(y + 3)
		.stroke({
			color: color,
			width: 2
		})
		.radius(5)
		.fill("transparent");

	if (data["root"]) {
		rect.fill({
			color: "#FFFFFF"
		});
		let lines = data["str"].split("\n");
		for (let line = 0; line !== lines.length; ++line) {
			container.text(lines[line]).font("family", "Monaco, monospace").font("size", 14).dx(x).dy(y + charHeight * line)
				.attr('xml:space', 'preserve', 'http://www.w3.org/XML/1998/namespace');
		}
	}

	let xDelta = charWidth;

	for (let child of data["children"]) {
		let parent_len = child["parent_str"].length * charWidth;
		_display_tree(child, container,
			child["start_col"] * charWidth,
			child["start_row"] * charHeight);
		xDelta += parent_len + charWidth;
	}
}