<script>

    import Input from "../../../components/Input.svelte";
    import LoadButton from "../../../components/LoadButton.svelte";
    import Button from "../../../components/Button.svelte";
    import {csrftoken} from "../../../snippets/csrf";
    import {goto} from "@roxi/routify";
    import {slide} from "svelte/transition"
    import {do_redirect} from "../../../snippets/do_redirect.ts";
    import Loader from "../../../components/Loader.svelte";

    let username = "";
    let password = "";

    let services = null;
    let pending_configuration_servies = [];

    (async () => {
        await (async () => {
            const res = await fetch("/auth/api/alt_ping");
            if (res.status !== 200) {
                $goto("/auth")
            }
        })()
        const res = await fetch("/auth/api/services");
        if (res.status === 200) {
            services = await res.json();
            pending_configuration_servies = services.filter(e => e.service.has_configurations < e.service.max_configurations);
            services = services.filter(e => (e.service.max_configurations != 0 && e.service.has_configurations > 0) || e.service.max_configurations == 0)
        }
    })();

    async function select_service(registration) {
        if (registration.username || registration.passwordPlain) {
            await fetch("/auth/api/next_credentials/store", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken(),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({next_credentials: registration.service.name})
            });
        }
        if (registration.service.origin) registration.service.origin = `${location.protocol}//${registration.service.origin}`;
        const url = (registration.service.sub_url.startsWith("http")?"":(registration.service.origin??location.origin)) + registration.service.sub_url;
        if (registration.service.origin) do_redirect(url);
        else location.href = url;
    }
=======
        const url = (registration.service.sub_url.startsWith("http")?"":(registration.service.origin??location.origin)) + registration.service.sub_url;
        if (registration.service.origin) do_redirect(url);
        else location.href = url;
    }

    let opened_services = {};
>>>>>>> master
</script>

<style>
    .login_root {
        background-image: url("/auth/go/static/resolve/login_bg.jpg");
        height: 100vh;
        width: 100vw;
        background-size: cover;
    }

    .login_wrapper {
        height: 100vh;
        width: 100vw;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .login_box {
        display: flex;
        width: 500px;
        max-width: 100vw;
        padding: 10px;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(8px);
        border-radius: 3px;
        flex-direction: column;
        align-items: center;
        font-family: sans-serif;
        gap: 10px;
    }

    .service_row {
        display: flex;
        gap: 5px;
        width: 100%;
    }

    :global(.service_row>*:nth-child(1)) {
        flex-grow: .8;
    }

    :global(.service_row>*:not(:nth-child(1))) {
        flex-grow: .2;
        width: 20%;
        max-width: 50px;
    }

</style>

<div class="login_root">
    <div class="login_wrapper">
        <div class="login_box">
            <h1>Services</h1>
            {#if !services}
                <Loader/>
            {:else}
                {#each services as registration}
                    <div class="service_row">
                        <LoadButton on:clicked={event => {event.detail.waitUntil(new Promise(() => {})); select_service(registration)}} icon={registration.service.icon}>{registration.service.name}</LoadButton>
                            {#if registration.service.can_have_application_password || registration.service.configuration_view_template}
                                <Button on:click={() => {opened_services[registration.service.name] = !opened_services[registration.service.name]}} icon="cog"></Button>
                            {/if}

                    </div>
                    {#if opened_services[registration.service.name]}
                        <div transition:slide style="width: calc(100% - 20px); display: flex; flex-direction: column; gap: 5px;">
                            {#if registration.service.can_have_application_password}
                                <Button icon="key" on:click={() => location.href = "/auth/go/application_password/" + registration.service.name}>Set Application Password for {registration.service.name}</Button>
                            {/if}
                            {#if registration.service.configuration_view_template && registration.service.has_configurations > 0}
                                <Button icon="eye" on:click={() => location.href = "/auth/go/configure/view/" + registration.service.name}>View {registration.service.name} Configuration</Button>
                            {/if}
                        </div>
                    {/if}
                {:else}
                    <p>Keine Dienste vorhanden.</p>
                {/each}
            {/if}
            {#if pending_configuration_servies.length}
                <h1>Configure new Service</h1>
                {#each pending_configuration_servies as pcs}
<LoadButton vertical={true} on:clicked={event => {event.detail.waitUntil(new Promise(() => {})); $goto(`/auth/go/configure/${pcs.service.name}`)}} icon={pcs.service.icon}>{pcs.service.name}</LoadButton>
                {/each}
            {/if}
        </div>
    </div>
</div>
