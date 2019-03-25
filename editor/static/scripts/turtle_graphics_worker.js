export {draw};

function draw(svg, moves) {
    for (let move of moves) {
        svg.path(move)
            .fill('none')
            .stroke({ color: '#f06', width: 4, linecap: 'round', linejoin: 'round' });
        console.log(move);
    }
}