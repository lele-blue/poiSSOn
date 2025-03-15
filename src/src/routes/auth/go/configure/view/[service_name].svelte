<script>
		import DefaultFrame from "../../../../../components/DefaultFrame.svelte"
		import Loader from "../../../../../components/Loader.svelte"
		import LoadButton from "../../../../../components/LoadButton.svelte"
		import Input from "../../../../../components/Input.svelte"
		import Select from "../../../../../components/Select.svelte"
		import {csrftoken} from "../../../../../snippets/csrf.ts"
    import {goto} from "@roxi/routify";

		export let service_name;
</script>

<DefaultFrame>
	<h1>Configuration for {service_name}</h1>
	{#await fetch("/auth/api/configuration/view/" + service_name)}
		<Loader/>
	{:then resp}
		{#await resp.text()}
			<Loader/>
		{:then text}
			{@html text}
		{/await}
	{/await}
</DefaultFrame>
