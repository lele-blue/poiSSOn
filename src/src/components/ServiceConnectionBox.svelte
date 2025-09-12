<script>
    import Button from "@components/Button.svelte"
    import LoadButton from "@components/LoadButton.svelte"
    import Icon from "@components/Icon.svelte"
    import Switch from "@components/Switch.svelte"
    import Loader from "@components/Loader.svelte"

    export let title;
    export let text;
		export let setting;

		let step = "select"

    export let closeDialog;

		let services = null;
		let servicePr = setting.get_available_services()
		servicePr.then(res => services = res);

		const servicesConnectedMap = {};
		const servicesConnectedMap_orig = {};

		const added_services = [];
		const removed_services = [];

		let connected_services = null;
		setting.get_user_service_uids().then(async res => {
				await servicePr;
				connected_services = res;
				for (const service of services) {
						servicesConnectedMap[service.uid] = connected_services.includes(service.uid);
						servicesConnectedMap_orig[service.uid] = connected_services.includes(service.uid);
				}
		});

		function compute_changes() {
				for (const [service_uid, enabled] of Object.entries(servicesConnectedMap)) {
						if (servicesConnectedMap_orig[service_uid] && !enabled) removed_services.push(services.filter(s => s.uid === service_uid)[0])
						if (!servicesConnectedMap_orig[service_uid] && enabled) added_services.push(services.filter(s => s.uid === service_uid)[0])
				}
		}

		async function apply() {
				await setting.set_user_service_connections(Object.entries(servicesConnectedMap).filter(elem => elem[1]).map(elem => elem[0]));
				closeDialog();
		}

</script>

<style>
		table {
				width: 100%;
		}

		.service {
				display: flex;
				align-items: center;
				padding: 5px;
		}

		.card {
				display: flex;
				align-items: center;
				gap: 5px;
				border-radius: 10px;
				/* box-shadow: black 0px 0px 3px 0px; */
				padding: 7px;
				border: var(--material-accent-color) 2px solid;
		}

		.changes {
				display: flex;
				align-items: center;
				gap: 10px;
		}

		.services_stack {
				display: flex;
				flex-direction: column;
				gap: 5px;
		}
</style>

<svelte:body on:keydown|capture={event => {if (event.code == "Enter") closeDialog()}}/>

{#if step === "select"}
		<h1>{title}</h1>
		<p>{text}</p>

		{#if services !== null && connected_services !== null}
				<table>
						{#each services as service}
								<tr>
										<td>
												<div class="service"> 
														<Icon icon={service.icon}/>
														{service.name}
												</div>
										</td>
										<td>
												<Switch bind:value={servicesConnectedMap[service.uid]}/>
										</td>
								</tr>
						{:else}
								<p>No services added yet.</p>
						{/each}
				</table>
		{:else}
				<Loader/>
		{/if}

		<div style="display: flex; gap: 5px; width:100%;">
				<Button icon="close" on:click={closeDialog} dialogButton={true}>Cancel</Button>
				<Button icon="arrow-right" on:click={() => {step = "review"; compute_changes()}} dialogButton={true}>Continue</Button>
		</div>
{:else if step === "review"}
		<h1>Review Changes</h1>
		<div>
				<h3>User {setting.user.username}</h3>
				{#if added_services.length}
						<div class="changes">
								<Icon width={40} height={40} icon="plus"/> The user can now access the following new services:
								<div class="services_stack">
										{#each added_services as service}
												<div class="card">
														<Icon icon={service.icon}/> {service.name} 
												</div>
										{/each}
								</div>
						</div>
				{/if}
				{#if removed_services.length}
						<div class="changes">
								<Icon width={40} height={40} icon="close" color="var(--material-error-color)"/> The user can no longer access the following services:
								<div class="services_stack">
										{#each removed_services as service}
												<div class="card">
														<Icon icon={service.icon}/> {service.name} 
												</div>
										{/each}
								</div>
						</div>
				{/if}
				{#if !removed_services.length && !added_services.length}
						<div class="changes">
								<Icon width={40} height={40} icon="close"/> No changes to be applied
						</div>
				{/if}
		</div>
		<div style="display: flex; gap: 5px; width:100%;">
				<Button icon="close" on:click={closeDialog} dialogButton={true}>Cancel</Button>
				<LoadButton icon="check" on:clicked={event => event.detail.waitUntil(apply())} dialogButton={true}>Apply</LoadButton>
		</div>
{/if}
