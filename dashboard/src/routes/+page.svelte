<script lang="ts">
    import { inferno_color_scale } from "$lib";
    import Map from "$lib/components/Map.svelte";

    function getFeatureStyle(feature: any) {
        const count = feature?.properties.count || 0;
        return {
            color: colorScale(count),
            weight: 2,
            opacity: 0.85,
            lineCap: "round",
            lineJoin: "round",
        };
    }

    let { data } = $props();
    const colorScale = $derived(inferno_color_scale(1, data.maxCount));

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
    <h2>Durchschnittliche Strecke</h2>
    <p>
        Die durchschnittliche Strecke dauert etwa 7-8 Minuten und ist etwa 1,3 km lang. Die durchschnittliche Geschwindigkeit beträgt dabei etwa 10-11 km/h. Die nachfolgende Abbildung zeigt die Verteilungen der Streckenlängen, Fahrtdauer und
        Geschwindigkeit. Ungenauigkeiten ergeben sich durch die Annahme, dass der kürzeste Weg gefahren wird und durch den Umstand, dass die Daten nur in 5-Minuten-Intervallen erhoben wurden.
    </p>
    <img src="/images/trip_diagnostics.png" alt="Event Dichteverteilungen" />
</div>
<div class="prose prose-sm sm:prose-base lg:prose-lg xl:prose-xl dark:prose-invert mx-auto">
    <p class="text-sm">
        Code und Daten sind auf GitHub verfügbar. Die Daten wurden von der Nextbike GmbH über die öffentliche GBFS-Schnittstelle bereitgestellt. Die Daten sind anonymisiert und aggregiert, sodass keine Rückschlüsse auf einzelne Nutzer möglich sind.
        <a target="_blank" href="https://github.com/JensKrumsieck/veloleo">GitHub Repository</a>
    </p>
</div>