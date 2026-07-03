import fs from 'fs';
import path from 'path';

/** @type {import('./$types').PageServerLoad} */
export async function load() {
    const geoJsonPath = path.resolve(process.cwd(), '../data/bike_heatmap.geojson');

    if (!fs.existsSync(geoJsonPath)) {
        return { error: 'Data file not found', mapData: null, maxCount: 0 };
    }

    const rawData = fs.readFileSync(geoJsonPath, 'utf-8');
    const geojson = JSON.parse(rawData);

    let maxCount = 0;

    const significantFeatures = geojson.features.filter((feature: any) => {
        const count = feature.properties?.count || 0;
        return count >= 3;
    });

    const cleanFeatures = significantFeatures.map((feature: any) => {
        const count = feature.properties.count || 0;
        if (count > maxCount) maxCount = count;

        return {
            type: 'Feature',
            geometry: feature.geometry,
            properties: {
                count: count // Keep only the count feature for rendering
            }
        };
    });

    return {
        maxCount,
        mapData: {
            type: 'FeatureCollection',
            features: cleanFeatures
        }
    };
}
