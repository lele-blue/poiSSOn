<script>
    import DefaultFrame from "../../../../components/DefaultFrame.svelte";
    import Button from "../../../../components/Button.svelte";
    import {currentUser} from "../../../../state/currentUser.ts";
    import {goto} from "@roxi/routify";
</script>

<DefaultFrame back="/auth/go/dash" settings={false}>
    <h1>Settings</h1>

    <Button on:click={() => $goto("/auth/go/settings/2fa")} icon="key">Two Factor Authentication</Button>
</DefaultFrame>
