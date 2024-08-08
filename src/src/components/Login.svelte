<script lang="ts">
    import Input from "../components/Input.svelte";
    import LoadButton from "../components/LoadButton.svelte";
    import {csrftoken} from "../snippets/csrf";
    import {do_redirect} from "../snippets/do_redirect.ts";
    import {check_redirect} from "../snippets/check_redirect.ts";
    import {goto} from "@roxi/routify";
    import {createEventDispatcher} from "svelte";
    let username = "";
    let password = "";

    export let redir_on_logged_in = false;

    const dispatch = createEventDispatcher();

    let already_logged_in = false;

    const next = new URLSearchParams(document.location.search).get("next");

    function login(event) {
        let body = new FormData();
        body.append('username', username);
        body.append('password', password);

        ((event ?? {}).detail ?? {waitUntil: func => {}}).waitUntil((async () => {
            const res = await fetch("/auth/api/logon", {
                method: "POST",
                body,
                headers: {
                    "X-CSRFToken": csrftoken()
                }
            });
            if (res.status === 200) {
                if (!redir_on_logged_in) {
                    let blockWaitPrResolve: () => void;
                    const blockWaitPr = new Promise<void>(resolve => {blockWaitPrResolve = resolve});
                    dispatch("login", {waitUntil: (pr: Promise<void>) => {pr.then(() => {
                        already_logged_in = true;
                        blockWaitPrResolve();
                    })}});
                    await blockWaitPrResolve;
                }
                else if (next && await check_redirect(next)) {
                    await do_redirect(next);
                }
                else {
                    $goto("/auth/go/dash")
                }
            } else {
                throw new Error("Wrong credentials")
            }
        })());
    }

    async function check_permissions(url) {
        return (await fetch(`/auth/api/services/check?url=${encodeURIComponent(url)}`)).status === 200;
    }

    (async () => {
        const res = await fetch("/auth/api/alt_ping");
        if (res.status === 200) {
            already_logged_in = true;
        }
        if (already_logged_in && next && await check_permissions(next) && await check_redirect(next)) {
            await do_redirect(next);
        }
    })()

</script>


{#if !already_logged_in}
    <h1>Log in to your account</h1>
    <Input on:submitted={login} bind:value={username} icon="user" placeholder="Nutzername"/>
    <Input on:submitted={login} bind:value={password} icon="key" password={true} placeholder="Passwort"/>
    <div style="width: 80%">
        <LoadButton on:clicked={login} icon="arrow-right">Login</LoadButton>
    </div>
{:else if redir_on_logged_in}
    <h1>Bereits eingeloggt</h1>
    <div style="width: 80%">
        <LoadButton on:clicked={() => $goto("/auth/go/dash")} icon="arrow-right">Weiter</LoadButton>
    </div>
{:else}
    <slot/>
{/if}
