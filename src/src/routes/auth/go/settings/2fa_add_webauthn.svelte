<script>
    import DefaultFrame from "../../../../components/DefaultFrame.svelte";
    import Loader from "../../../../components/Loader.svelte";
    import LoadButton from "../../../../components/LoadButton.svelte";
    import Icon from "../../../../components/Icon.svelte";
    import Input from "../../../../components/Input.svelte";
    import Button from "../../../../components/Button.svelte";
    import OTPDeviceList from "../../../../components/OTPDeviceList.svelte";
    import {currentUser} from "../../../../state/currentUser.ts";
    import {check_login} from "../../../../snippets/check_login.ts";
    import {csrftoken} from "../../../../snippets/csrf.ts";
    import {handle_400} from "../../../../snippets/handle_2fa_400.ts";
    import {slide} from "svelte/transition";
    import {goto} from "@roxi/routify";
    import {get_icon} from "../../../../components/OTPDeviceList.svelte"

    check_login();

    async function qrcode() {
        const resp = await fetch("/auth/api/2fa/totp/qrcode", {
						method: "POST",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
            body: JSON.stringify({key}),
        });
        if (resp.status !== 200) throw new Error("no qr");
        return URL.createObjectURL(await resp.blob());
    }

    let name = "";
    let token = "";
    let name_error = null;
    let token_error = null;
    let error;

    async function submit() {
        error = null;
        if (!name.length) name_error = "Please enter a name";
        else name_error = null;
        if (token.length < 6) token_error = "Please Enter the Token";
        else token_error = null;

        if (name_error || token_error) return;
        const resp = await fetch("/auth/api/2fa/manage", {
						method: "POST",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
            body: JSON.stringify({key, token, name: "@autofill", type:"otp_webauthn.public-key"}),
        });
        if (resp.status !== 200) error = handle_400(await resp.json(), $goto);
        else {
            $goto("/auth/go/settings/2fa");
        }
    }

</script>

<style>
    .error_box {
        display: flex;
        color: red;
        align-items: center;
        gap: 5px;
    }
</style>

<DefaultFrame back="/auth/go/settings/2fa_choose" settings={false}>
    <h1>Add new Key</h1>
    <Loader/>
    {#if error}
        <div transition:slide class="error_box">
            <Icon icon="alert" color="red"/>
            <p>{error}</p>
        </div>
        <LoadButton icon="reload" on:clicked={e => e.detail.waitUntil(submit())}>Create Device</LoadButton>
    {/if}




</DefaultFrame>
