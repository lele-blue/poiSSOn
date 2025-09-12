<script>
    import DefaultFrame from "../../../../components/DefaultFrame.svelte";
    import Button from "../../../../components/Button.svelte";
    import {currentUser} from "../../../../state/currentUser.ts";
    import {goto} from "@roxi/routify";
</script>

<DefaultFrame back="/auth/go/dash" settings={false}>
    <h1>Settings</h1>

    <Button on:click={() => $goto("/auth/go/settings/2fa")} icon="key">Two Factor Authentication</Button>
    {#if $currentUser?.permissions.includes("poisson.self_service.password_change")}
				<Button on:click={() => $goto("/auth/go/settings/password_change")} icon="key">Change Password</Button>
    {/if}
    {#if $currentUser?.permissions.includes("poisson.manage")}
        <Button on:click={() => $goto("/auth/go/manager")} icon="tune">Configure this PoiSSOn instance</Button>
    {/if}
    {#if $currentUser?.permissions.includes("poisson.admin")}
        <Button on:click={() => location.href="/auth/go/admin"} icon="admin">Admin</Button>
    {/if}
</DefaultFrame>
