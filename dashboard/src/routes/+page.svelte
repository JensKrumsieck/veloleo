<script lang="ts">
    import Map from "$lib/components/Map.svelte";

    function getHeatColor(count: number, maxCount: number) {
        const ratio = count / (maxCount || 1);
        if (ratio > 0.85) return "#fcffa4"; // Bright Yellow-White
        if (ratio > 0.65) return "#fac228"; // Hot Golden Yellow
        if (ratio > 0.45) return "#f17c1d"; // Vibrant Orange
        if (ratio > 0.3) return "#d14b4f"; // Hot Pink/Coral Red
        if (ratio > 0.15) return "#9c2e6f"; // Deep Magenta/Purple
        if (ratio > 0.05) return "#57106e"; // Dark Purple
        return "#1b0c41"; // Ink Navy/Black (baseline)
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
    <h2>Interaktive Karte</h2>
    <p>
        In dieser Karte ist die potentielle Nutzung der Fahrräder des Braunschweiger Fahrradausleihsystems "Veloleo" interaktiv visualisiert. Die Karte zeigt <em>mögliche</em> gefahrene Strecken im Zeitraum der Datensammlung. <em>Mögliche</em> Strecken,
        weil Streckendaten nicht über die öffentlichen Schnittstellen abrufbar sind (siehe unten). Zu Erkennen ist eine erhebliche Nutzung im Bereich der Campusgegenden, sowie Fahrten in oder von Richtung Hauptbahnhof, vorwiegend über den östlichen Ring.
    </p>

    <Map data={mapLayer} />

    <p class="text-sm">
        Die Daten wurden von der öffentlichen GBFS-Schnittstelle der Nextbike GmbH über einen Zeitraum von mehreren Tagen im Abstand von 5 Minuten gesammelt. Da diese Schnittstelle allerdings lediglich freie Fahrräder listet, wurden verschwindende
        Fahräder als Ausleihstart und erscheinende Fahrräder als Ausleihende interpretiert. Aus diesen punktuellen Informationen wurden mittels Bipartite Graph Matching Algorithmus (<em>min_weight_full_bipartite_matching</em>) mögliche
        Start-Ziel-Paare ermittelt, aus denen die Strecken mittels OpenStreetMap Bike Map anhand des kürzesten Weges ermittelt wurden. Das heißt die Strecken stellen keine wirklichen Fahrten, sondern mögliche Benutzungskorridore dar.
    </p>

    <h2>Dichteverteilungen</h2>
    <p>
        In der nachfolgenden Abbildung wurden die Ausleih-(Departure) und Rückgabedichte (Arrival) um stadtweite Hotspots zu visualisieren. Dabei wurde die Kerndichteschätzer-Methode (Kernel Density Estimate; KDE) verwendet. Des weiteren wurde eine
        Übergangsdichte durch Subtraktion der Ausleih- und Rückgabedichte voneinander erhalten, die Gebiete aufdeckt, in denen mehr ausgeliehen oder zurückgegeben wird. Dabei zeigt sich, dass im Hochschulviertel und am Hauptbahnhof mehr Rückgaben als
        Ausleihvorgänge stattfinden, während in den Ringgebieten mehr Ausleihvorgänge vollzogen werden.
    </p>
    <img src="/images/event_heatmaps.png" alt="Event Dichteverteilungen" />
</div>
