<script lang="ts">
    import Map from "$lib/components/Map.svelte";

    function getHeatColor(count: number, maxCount: number) {
        const ratio = count / (maxCount || 1);
        if (ratio > 0.85) return "#fcffa4"; // Bright Yellow-White
        if (ratio > 0.65) return "#fac228"; // Hot Golden Yellow
        if (ratio > 0.45) return "#f17c1d"; // Vibrant Orange
        if (ratio > 0.30) return "#d14b4f"; // Hot Pink/Coral Red
        if (ratio > 0.15) return "#9c2e6f"; // Deep Magenta/Purple
        if (ratio > 0.05) return "#57106e"; // Dark Purple
        return "#1b0c41";                   // Ink Navy/Black (baseline)
    }

    function getLineWidth(count: number, maxCount: number) {
        return 1.5 + (count / (maxCount || 1)) * 8;
    }

    function getFeatureStyle(feature: any) {
        const count = feature?.properties.count || 0;
        return {
            color: getHeatColor(count, data.maxCount),
            weight: getLineWidth(count, data.maxCount),
            opacity: 0.85,
            lineCap: "round",
            lineJoin: "round",
        };
    }

    let { data } = $props();

    const mapLayer = $derived({
        geoJson: data.mapData,
        style: getFeatureStyle,
        onEachFeature: (feature: any, layer: any) => {
            layer.bindPopup(`<strong>Bikes Tracked:</strong> ${feature.properties.count}`);

            layer.on("mouseover", () => {
                layer.setStyle({ opacity: 1, weight: 12 });
            });

            layer.on("mouseout", () => {
                layer.setStyle(getFeatureStyle(feature));
            });
        },
    });
</script>

<div class="prose prose-sm sm:prose-base lg:prose-lg xl:prose-xl dark:prose-invert mx-auto">
    <h1>Nutzungsanalyse Veloleo</h1>
    <p>In dieser Karte ist die potentielle Nutzung der Fahrräder des Braunschweiger Fahrradausleihsystems "Veloleo" interaktiv visualisiert.</p>

    <Map data={mapLayer} />
</div>
