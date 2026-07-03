<script lang="ts">
    import Map from "$lib/components/Map.svelte";

    let { data } = $props();
</script>

<article class="prose prose-sm sm:prose-base lg:prose-lg xl:prose-xl dark:prose-invert mx-auto">
    <h1>Nutzungsanalyse Veloleo</h1>
    <p>In dieser Karte ist die potentielle Nutzung der Fahrräder des Braunschweiger Fahrradausleihsystems "Veloleo" interaktiv visualisiert.</p>

    <Map {data} />
</article>
