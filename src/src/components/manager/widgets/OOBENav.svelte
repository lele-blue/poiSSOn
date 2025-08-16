<script>
    import Input from "@components/Input.svelte"
    import Loader from "@components/Loader.svelte"
    import Button from "@components/Button.svelte"
    import LoadButton from "@components/LoadButton.svelte"
		import {goto} from "@roxi/routify"

    export let setting;
		export let next;
		export let pre_next;
		export let back = null;

    let loading = true;

    export let value = "";

		function goto_next() {
				$goto("/auth/go/manager/[section]/[...data]", {"section": "oobe", "data": [next]});
		}
</script>

<style>
		.oobe_nav {
				display: flex;
				align-items: center;
				gap: 5px;
				justify-content: space-between;
				width: 100%;
		}
</style>

<div class="oobe_nav">
		{#if back}
				<Button icon="chevron-left" on:click={() => $goto("/auth/go/manager/[section]/[...data]", {"section": "oobe", "data": [back]})}>Back</Button>
		{/if}
		<LoadButton icon="chevron-right" on:clicked={async event => {if(pre_next) {let prom = setting[pre_next](); event.detail.waitUntil(prom); if (await prom) goto_next()} else goto_next()}}  reverse={true}>Continue</LoadButton>
</div>


