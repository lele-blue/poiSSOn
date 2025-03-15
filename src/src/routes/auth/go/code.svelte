<script>

    import Input from "../../../components/Input.svelte";
    import LoadButton from "../../../components/LoadButton.svelte";
    import {csrftoken} from "../../../snippets/csrf";
    import {do_redirect} from "../../../snippets/do_redirect.ts";
    import {check_redirect} from "../../../snippets/check_redirect.ts";
    import {goto} from "@roxi/routify";
    import DefaultFrame from "../../../components/DefaultFrame.svelte";
    import Login from "../../../components/Login.svelte";

    let code = "";
    let code_error = null;
    let already_logged_in = false;

    function login(event) {
        event.detail.waitUntil(new Promise(async (resolve) => {
            if (next && await check_redirect(next)) {
                await do_redirect(next);
            }
            resolve();
        }))
    }
    
    const next = new URLSearchParams(document.location.search).get("next");

    let service_info = (async () => {
        const resp = await fetch(`/auth/api/services/query?url=${encodeURIComponent(next)}`);
        if (resp.status !== 200) {throw new Error("Cant get service")}

        return await resp.json();
    })()


    function submit_code(event) {
        let body = new FormData();
        body.append('code', code);
        event.detail.waitUntil((async () => {
            const resp = await fetch('/auth/api/consume_code', {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken()
                },
                body
            });
            if (resp.status === 201) {
                try {
                    await service_info
                    await do_redirect(next);
                }
                catch (e) {
                    if (!await check_redirect(next)) {
                        throw new Error('Unsafe redirect');
                    }
                    await do_redirect(next);
                }
            }
            else if (resp.status === 403) {
                code_error = "Too many tries";
                throw new Error("ratelimit");
            }
            else {
                code_error = "Invalid Code";
                throw new Error("invalid code");
            }
        })())
    }
</script>


<DefaultFrame>

    {#if !already_logged_in}
        <Login on:login={login} redir_on_logged_in={false}>
            <p>Your account is not authorized to access this. You can still sign in by code though.</p>
        </Login>
    {/if}


    {#await service_info}
        <h1>Login by code</h1>
    {:then info}
        <h1>Login by code to {info.name}</h1>
    {:catch e}
        <h1>Login by code</h1>
    {/await}
    <Input bind:value={code} error={code_error} icon="key" password={true} placeholder={"Code"}/> 
    <div style="width: 80%">
        <LoadButton vertical={true} on:clicked={submit_code} icon="arrow-right">Login</LoadButton>
    </div>
</DefaultFrame>
