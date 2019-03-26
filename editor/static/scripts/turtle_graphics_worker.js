export {draw};

function draw(svg, rawSVG, data) {
    $(rawSVG).css("background-color", data["bgColor"]);
    for (let move of data["path"]) {
        svg.path(move["seq"])
            .fill(move["fill"])
            .stroke({ color: move["stroke"], width: 1, linecap: 'round', linejoin: 'round' });
    }
}