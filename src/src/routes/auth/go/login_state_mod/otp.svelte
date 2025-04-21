<script>

    import {check_redirect} from "../../../../snippets/check_redirect.ts";
    import {do_redirect} from "../../../../snippets/do_redirect.ts";
    import {csrftoken} from "../../../../snippets/csrf.ts";
    import Icon from "../../../../components/Icon.svelte";
    import Button from "../../../../components/Button.svelte";
    import LoadButton from "../../../../components/LoadButton.svelte";
    import Loader from "../../../../components/Loader.svelte";
    import OTPDeviceList, {get_icon} from "../../../../components/OTPDeviceList.svelte";
    import Input from "../../../../components/Input.svelte";
    import {goto} from "@roxi/routify";
    import DefaultFrame from "../../../../components/DefaultFrame.svelte";
    import {post} from "@/snippets/fetch"

    const devices = (async () => {
        const resp = await fetch("/auth/api/2fa/verification");
        if (resp.status !== 200) {
            throw new Error("Failed to fetch devices")
        }
        const json = await resp.json()
        if (json && json.length == 1) {
            device = json[0];
        }
        return json
    })();

    let device = null;

    let token = "";
    let error = null;
    const next = new URLSearchParams(document.location.search).get("next") ?? "/auth/go/dash";

    async function submit() {
        console.log(device)
        const resp = await fetch("/auth/api/2fa/verification", {
						method: "POST",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
            body: JSON.stringify({token, id: device.persistent_id, step: "submit"}),
        });
        if (resp.status == 200) {
            await redirect()
        }
        else if (resp.status == 400) {
            error = (await resp.json()).detail
        }
        else if (resp.status == 404) {
            error = "Device not found"
        }
        else {
            throw new Error("Verification Failed")
        }
    }

    async function redirect(){
        if (!await check_redirect(next)) {
            throw new Error('Unsafe redirect');
        }
        await do_redirect(next);
    }

    async function webauthn_verify(device) {
        const data = await post("/auth/api/2fa/verification", {id: device.persistent_id, step: "challenge"})
        if (data.action === "continue") await redirect();
        const creds = await navigator.credentials.get({publicKey: PublicKeyCredential.parseRequestOptionsFromJSON(data), mediation: "required"})
        // will throw if invalid
        const data2 = await post("/auth/api/2fa/verification", {id: device.persistent_id, step: "submit", token: creds.toJSON()})
        if (data2.action === "continue") await redirect();
        else throw new Error("Unexpected response after successful verification")
    }



</script>


<style>
.error_box {
    display: flex;
    align-items: center;
}
</style>


<DefaultFrame>
    <h2>Please authenticate for this action.</h2><br/>
    {#if !device}
        {#await devices}
            <Loader/>
        {:then devices}
            {#if devices == null}
                <p>No 2FA necessary</p>
                <LoadButton on:clicked={e => e.detail.waitUntil(redirect())} icon="arrow-right">Continue</LoadButton>
            {:else}
            <span>Select a device to perform OTP Authentication</span>
            <OTPDeviceList on:selected={ev => device=ev.detail} {devices}/>
            {/if}
        {:catch e}
            <p>{e}</p>
        {/await}

    {:else}
        {#if device.type == "otp_webauthn.webauthndevice"}
            {#await webauthn_verify(device)}
                <Loader/>
            {:catch e}
                <Icon icon="alert" color="red"/>
                {#if e.name === "NotAllowedError"}
                    <span>Browser refused operation</span>
                {:else}
                    <span>{e}</span>
                {/if}
                <!-- device=device invalidates `device`, so the {#await} is re-evaluated  -->
                <Button icon="reload" on:click={() => device=device}>Retry</Button>
            {/await}
        {:else if device.type == "otp_totp.totpdevice"}
            <p>Please enter the code shown on {device.name}</p>
            <Input autofocus={true} bind:value={token} {error} icon={get_icon(device.name)} placeholder="{device.name} Token"/>
            <LoadButton icon="arrow-right" on:clicked={ev => ev.detail.waitUntil(submit())}>Authenticate</LoadButton>
        {/if}
        <Button dialogButton={true} icon="chevron-left" on:click={() => {device = null; error = null}}>Select different Device</Button>
    {/if}

</DefaultFrame>
