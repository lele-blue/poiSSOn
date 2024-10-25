<script>
    import {slide} from "svelte/transition";
    import DefaultFrame from "../../../../components/DefaultFrame.svelte";
    import Loader from "../../../../components/Loader.svelte";
    import Input from "../../../../components/Input.svelte";
    import Icon from "../../../../components/Icon.svelte";
    import Button from "../../../../components/Button.svelte";
    import LoadButton from "../../../../components/LoadButton.svelte";
    import OTPDeviceList, {get_icon} from "../../../../components/OTPDeviceList.svelte";
    import {currentUser} from "../../../../state/currentUser.ts";
    import {check_login} from "../../../../snippets/check_login.ts";
    import {handle_400} from "../../../../snippets/handle_2fa_400.ts";
    import {csrftoken} from "../../../../snippets/csrf.ts";
    import {goto, redirect} from "@roxi/routify";

    check_login();
    const goto_ = $goto;

    const fetchDevices = async () => {
        const resp = await fetch("/auth/api/2fa/manage");

        if (400 <= resp.status && resp.status < 500) {
            handle_400(await resp.json(), $redirect)
            return []
        }
        if (resp.status !== 200) {
            throw new Error("Failed to fetch devices")
        }
        return await resp.json()

    }
    let devicesPr = fetchDevices();

    let devices = null;
    devicesPr.then(devs => devices = devs);
    let editing = [];
    let new_names = {};

    async function delete_device(id) {
        const resp = await fetch("/auth/api/2fa/manage", {
						method: "DELETE",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
            body: JSON.stringify({id: id}),
        });
        if (resp.status !== 200) throw new Error("Name change failed");
        devicesPr = fetchDevices();
        devices = await devicesPr;
    }
    async function set_new_name(id, name) {
        const resp = await fetch("/auth/api/2fa/manage", {
						method: "PATCH",
						headers: {
								"Content-Type": "application/json",
								"X-CSRFToken": csrftoken(),
						},
            body: JSON.stringify({id: id, name: name}),
        });
        if (resp.status !== 200) throw new Error("Name change failed");
        editing = [];
        devicesPr = fetchDevices();
        devices = await devicesPr;
    }
</script>

<DefaultFrame back="/auth/go/settings" settings={false}>
    <h1>Manage 2FA</h1>

    {#if devices}
        <OTPDeviceList {devices}>
            <div slot="buttons" let:device>
                <div style="display: flex; align-items: center; gap:5px">
                    {#if !editing.includes(device.id)}
                        <Button dialogButton={true} icon="pencil" on:click={() => {editing = [...editing, device.id]; new_names[device.id] = device.name}} />
                    {:else}
                        <LoadButton on:clicked={ev => ev.detail.waitUntil(set_new_name(device.id, new_names[device.id]))} icon="check"/>
                    {/if}
                    <LoadButton on:clicked={e => {e.detail.waitUntil(delete_device(device.id))}} destroy={true} dialogButton={true} icon="delete" />
                </div>
            </div>

            <div style="flex-grow: 1" slot="main" let:device>
            {#if !editing.includes(device.id)}

                <div style="display: flex; align-items: center; gap:5px">
                    <Icon icon={get_icon(device.name)}/>
                    {device.name}
                </div>
            {:else}
                <div>
                    <Input autofocus={true} icon={get_icon(new_names[device.id])} bind:value={new_names[device.id]} placeholder={`New Name for ${device.name}`}/>
                </div>
            {/if}
            </div>
        </OTPDeviceList>
        <Button icon="plus" on:click={() => $goto("/auth/go/settings/2fa_add")}>Add new Device</Button>
    {/if}

    {#await devicesPr}
        <Loader/>
    {:catch e}
        <Icon icon="alert" color="red"/>
        <p>{e}</p>
    {/await}

</DefaultFrame>
