export {draw};

function draw(svg, moves) {
    for (let move of moves) {
        svg.path(move)
            .fill('none')
            .stroke({ color: '#f06', width: 1, linecap: 'round', linejoin: 'round' });
    }
}