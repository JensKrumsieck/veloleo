import * as d3 from 'd3';

// place files you want to import through the `$lib` alias in this folder.

export function inferno_color_scale(min: number, max: number): (count: number) => string {
    const logScale = d3.scaleLog().domain([Math.max(1, min), Math.max(max, 2)]) // avoid log(0)
        .range([0, 1])
        .clamp(true);
    return (count: number) => d3.interpolateInferno(logScale(Math.max(count, 1)));

}