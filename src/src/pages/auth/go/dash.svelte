<script>

    import Input from "../../../components/Input.svelte";
    import LoadButton from "../../../components/LoadButton.svelte";
    import {csrftoken} from "../../../snippets/csrf";
    import {goto} from "@roxi/routify";
    import {do_redirect} from "../snippets/do_redirect.ts";
    import Loader from "../../../components/Loader.svelte";

    let username = "";
    let password = "";

    let services = null;

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
        do_redirect((registration.service.sub_url.startsWith("http")?"":(registration.service.origin??location.origin)) + registration.service.sub_url);
    }
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

</style>

<div class="login_root">
    <div class="login_wrapper">
        <div class="login_box">
            <h1>Services</h1>
            {#if !services}
                <Loader/>
            {:else}
                {#each services as registration}
                    <LoadButton vertical={true} on:clicked={event => {event.detail.waitUntil(new Promise(() => {})); select_service(registration)}} icon={registration.service.icon}>{registration.service.name}</LoadButton>
                {:else}
                    <p>Keine Dienste vorhanden.</p>
                {/each}
            {/if}
        </div>
    </div>
</div>
