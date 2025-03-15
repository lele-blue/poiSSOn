<script>
    import DefaultFrame from "../../../../components/DefaultFrame.svelte";
    import Button from "../../../../components/Button.svelte";
    import {currentUser} from "../../../../state/currentUser.ts";
    import {check_login} from "../../../../snippets/check_login.ts";
    import {goto} from "@roxi/routify";
    check_login();
</script>

<DefaultFrame back="/auth/go/settings/2fa" settings={false}>
    <h1>Choose 2-Factor type</h1>

    <div style="display: flex; gap: 10px">
        <Button on:click={() => $goto("/auth/go/settings/2fa_add")} icon="numeric" vertical={true}>Authenticator App (TOTP)</Button>
        <Button on:click={() => $goto("/auth/go/settings/2fa_add_webauthn")} icon="key-chain" vertical={true}>Security Key / Passkey</Button>
    </div>
</DefaultFrame>
