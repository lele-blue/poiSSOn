<script>
		import DefaultFrame from "../../../../components/DefaultFrame.svelte"
		import Loader from "../../../../components/Loader.svelte"
		import LoadButton from "../../../../components/LoadButton.svelte"
		import Input from "../../../../components/Input.svelte"
		import Select from "../../../../components/Select.svelte"
		import {csrftoken} from "../../../../snippets/csrf.ts"
    import {goto} from "@roxi/routify";

		export let service;

		const configPr = (async () => {
				const config = await (await fetch(`/auth/api/service/${encodeURIComponent(service)}/configuration`)).json();
				for (const cfg of config) {
						values[cfg.query_id] = cfg.default;
						if (cfg.check_regex.startsWith("!choices:")) {
								values[cfg.query_id] = JSON.parse(cfg.check_regex.slice("!choices:".length))[0][1];
						}
				}
				configResolved = config;
				return config;
		})();

		let configResolved = null;

		const errors = {};

		const values = {};

		$: {
				if (configResolved) {
						for (const cfg of configResolved) {
								if (cfg.check_regex && !cfg.check_regex.startsWith("!choices:")) {
										if (values[cfg.query_id] && !values[cfg.query_id].match(new RegExp(cfg.check_regex))) {
												errors[cfg.query_id] = "Invalid Value";
										}
										else {
												errors[cfg.query_id] = null;
										}
								}
						}
				}
		};

		async function submit(event) {
				let resp = await fetch(`/auth/api/configuration/${service}`, {
						method: "POST",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
						body: JSON.stringify(values),
				});

				if (resp.status != 201) {
						throw new Error("Error");
				}

				$goto("/auth/go/dash");
		}

</script>


<DefaultFrame>
		<h1>Configure {service}</h1>

		{#await configPr}
				<Loader/>
		{:then config}
				{#each config as step (step.query_id)}
						<h2>{step.title}</h2>
						<p>{step.description}</p>
						{#if step.check_regex.startsWith("!choices:")}
								<div style="width: 80%">
										<Select bind:value={values[step.query_id]}>
												{#each JSON.parse(step.check_regex.slice("!choices:".length)) as [text, value]}
														<option {value}>{text}</option>
												{/each}
										</Select>
								</div>
						{:else}
								<Input bind:value={values[step.query_id]} autocomplete="off" password={step.is_password} placeholder={step.title} error={errors[step.query_id]}/>
						{/if}
				{:else}
						<p>Nothing to configure</p>
				{/each}

				<LoadButton icon="plus" disabled={Object.values(errors).some(e => e != null) || !Object.values(values).every(e => e)} on:clicked={e => e.detail.waitUntil(submit())}>Add Service</LoadButton>

		{:catch e}
				<p>Something went wrong: {e}</p>
		{/await}


</DefaultFrame>



