<script lang="ts">
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
    import {get_icon} from "@components/OTPDeviceList.svelte"
    import {post} from "@/snippets/fetch"
    import {onMount} from "svelte";

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

    let error;
    let loading = true;

    async function prepare() {
        const data = await post("/auth/api/2fa/manage", {step: "challenge", type:"otp_webauthn.webauthndevice"});
        try{
            const creds = await navigator.credentials.create(
                {publicKey: PublicKeyCredential.parseCreationOptionsFromJSON(data)}
            )
            await submit(creds.toJSON())
        }
        catch (e) {
            loading = false;
            error = `Browser refused to register key<br>`
            if (e.name !== "NotAllowedError") error += e;
            throw e;
        }
    }

    async function submit(credentials) {
        error = null;

        const resp = await fetch("/auth/api/2fa/manage", {
						method: "POST",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
            body: JSON.stringify({step: "submit", type:"otp_webauthn.webauthndevice", data: credentials}),
        });
        if (resp.status !== 200) {
            error = handle_400(await resp.json(), $goto);
            loading = false
        }
        else {
            $goto("/auth/go/settings/2fa");
        }
    }

    onMount(prepare);

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
    {#if loading}
        <Loader/>
    {/if}
    {#if error}
        <div transition:slide class="error_box">
            <Icon icon="alert" color="red"/>
            <p>{@html error}</p>
        </div>
        <LoadButton icon="reload" on:clicked={e => e.detail.waitUntil(prepare())}>Retry</LoadButton>
    {/if}




</DefaultFrame>
