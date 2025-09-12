<script>
    import DefaultFrame from "@components/DefaultFrame.svelte";
    import Loader from "@components/Loader.svelte";
		import Setting from "@components/manager/Setting.svelte";
    import {currentUser} from "@/state/currentUser.ts";
    const settingsPr = import("@/data/settings.json");
</script>
<DefaultFrame back="/auth/go/settings" settings={false}>
		<h1>Set new password</h1>
		{#await settingsPr}
				<Loader/>
		{:then settings}
				{#each settings.categories.filter(c => c.slug === "users")[0].pages.filter(p => p.slug === "manager")[0].subpages['*'].subpages.set_password.content as setting}
						<Setting extra_data={[$currentUser.uid]} {...setting} />
				{/each}
		{/await}
</DefaultFrame>
