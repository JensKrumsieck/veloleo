<script lang="ts">
    import "leaflet/dist/leaflet.css";
    interface MapLayer {
        geoJson: any;
        style?: (feature: any) => any;
        onEachFeature?: (feature: any, layer: any) => void;
    }

    let { data } = $props<{ data: MapLayer }>();
    let mapEl = $state<HTMLDivElement>();
    let map: any = null;
    let width = $state(600);
    let maxWidth = 600;
    let height = 600;

    $effect(() => {
        console.log(data);
        if (!mapEl || !data.geoJson || map) return;
        const initMap = async () => {
            try {
                const LeafletModule = await import("leaflet");
                const L = LeafletModule.default || LeafletModule;
                const newMap = L.map(mapEl!, {
                    zoomSnap: 0.1,
                    maxBoundsViscosity: 1.0,
                    scrollWheelZoom: false,
                });
                newMap.on("focus", () => newMap.scrollWheelZoom.enable());
                newMap.on("blur", () => newMap.scrollWheelZoom.disable());

                L.tileLayer("https://api.jenskrumsieck.de/openstreetmap/{s}/{z}/{x}/{y}.png", {
                    attribution: "© OpenStreetMap contributors",
                }).addTo(newMap);
                newMap.on("tileerror", (e) => console.log("tile error", e));
                const currentLayer = L.geoJSON(data.geoJson, {
                    style: data.style,
                    onEachFeature: data.onEachFeature,
                }).addTo(newMap);

                const bounds = currentLayer.getBounds();
                if (bounds.isValid()) {
                    newMap.fitBounds(bounds);
                    newMap.setMaxBounds(bounds);
                    newMap.setMinZoom(newMap.getZoom());
                } else {
                    console.warn("GeoJSON bounds invalid:", data.geoJson);
                    newMap.setView([52.2689, 10.5268], 13);
                }

                map = newMap;
                requestAnimationFrame(() => map?.invalidateSize());
            } catch (err) {
                console.error("Leaflet map failed to initialize:", err);
            }
        };
        initMap();
        return () => {
            if (map) {
                map.remove();
                map = null;
            }
        };
    });
    $effect(() => {
        if (width && map) {
            map.invalidateSize();
        }
    });
</script>

<div class="flex w-full justify-center">
    <div bind:clientWidth={width} style="width: 100%; max-width: {maxWidth}px;">
        <div bind:this={mapEl} style="width: 100%; height: {height}px;"></div>
    </div>
</div>
