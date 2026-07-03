<script lang="ts">
	import { onMount } from "svelte";
	import { dev } from "$app/environment";
	import "./layout.css";
	import * as Swetrix from "swetrix";

	onMount(() => {
		Swetrix.init("j3QqUorqLLVY", {
			devMode: dev,
			disabled: dev,
			apiURL: "https://api.analytics.jenskrumsieck.de/log",
		});
		Swetrix.trackViews();
	});

	let { children } = $props();
</script>

<svelte:head>
	<title>Nutzungsanalyse Veloleo Braunschweig</title>
</svelte:head>

<div class="dark:bg-gray-800 min-h-screen px-2.5">
	<article class="pt-5">
		{@render children()}
	</article>
	<footer class="p-5 mt-12 text-center container container-md mx-auto dark:text-gray-400 text-gray-600 text-sm border-t dark:border-gray-600 border-gray-50">
		<div class="mt-5 text-green-200">
			Ein Projekt von <a class="underline font-medium" href="https://jenskrumsieck.de">Dr. Jens Krumsieck</a>.
		</div>
		<div class="mt-2 dark:text-gray-400 text-gray-600">
			<a class="underline" target="_blank" href="https://jenskrumsieck.de/privacy">Datenschutzerklärung</a> | <a class="underline" target="_blank" href="https://jenskrumsieck.de/impressum">Impressum</a>
		</div>
	</footer>
</div>
