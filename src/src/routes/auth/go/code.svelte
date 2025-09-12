<script>

    import Input from "../../../components/Input.svelte";
    import Loader from "../../../components/Loader.svelte";
    import Icon from "../../../components/Icon.svelte";
    import Button from "../../../components/Button.svelte";
    import LoadButton from "../../../components/LoadButton.svelte";
    import {csrftoken} from "../../../snippets/csrf";
    import {do_redirect} from "../../../snippets/do_redirect.ts";
    import {check_redirect} from "../../../snippets/check_redirect.ts";
    import {goto} from "@roxi/routify";
    import DefaultFrame from "../../../components/DefaultFrame.svelte";
    import Login from "../../../components/Login.svelte";
		import {get, get_basepath, post} from "../../../snippets/fetch.ts";
		import {currentUser} from "../../../state/currentUser.ts";
		import {check_login} from "@/snippets/check_login.ts";

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
    const token = new URLSearchParams(document.location.search).get("token");

    let service_info = (async () => {
				if (token) return;
        const resp = await fetch(`${get_basepath()}/api/services/query?url=${encodeURIComponent(next)}`);
        if (resp.status !== 200) {throw new Error("Cant get service")}

        return await resp.json();
    })()


		let token_info = null;
		let token_error = null;
		let password;
		let password_confirm;
		let errors = {};
		let token_success = false;
		async function get_token_info(token) {
				token_info = await get(`/api/manager/login_links/${token}`, error => {token_error = "The token is either invalid or expired"});
		}
		$: if (token && !$currentUser) get_token_info(token);

		async function redeem_token() {
				errors = {};
				if (password !== password_confirm) {
						errors.password_confirm = "Passwords do not match"
						return;
				}
				if (await post(`/api/manager/login_links/${token}/redeem`, {password}, data => errors = data)) {
						await check_login();
						token_success = true;
				}
		}


    function submit_code(event) {
        let body = new FormData();
        body.append('code', code);
        event.detail.waitUntil((async () => {
            const resp = await fetch(`${get_basepath()}/api/consume_code`, {
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


<style>
		form {
				width: 80%;
				display: flex;
				flex-direction: column;
				gap: 10px;
		}
</style>


<DefaultFrame>

		{#if token}
				<h1>Token Login</h1>

				{#if token_success}
						<p>Password has been changed, and you are now logged in.</p>
						<Button icon="arrow-right" on:click={() => $goto("/auth/go/dash")}>To Dashboard</Button>
				{:else if $currentUser}
						<p>To use a token, you must be logged out.</p>
				{:else}
						{#if token_info}
								{#if token_info.purpose === "poisson.loginlink.purpose.password_reset"}
										<form>
												<span>Set password for {token_info.username}</span>
												<div style="display: none"><Input placeholder="Username" value={token_info.username}/></div>
												<Input bind:value={password} password={true} full_width={true} icon="key" placeholder="New Password" error={errors["password"]}/>
												<Input bind:value={password_confirm} password={true} full_width={true} icon="key" placeholder="Repeat Password" error={errors["password_confirm"]}/>
												<LoadButton submit={true} icon="arrow-right" on:clicked={event => event.detail.waitUntil(redeem_token())}>Set Password</LoadButton>
										</form>
								{:else if token_info.purpose === "poisson.loginlink.purpose.session_login"}
										<p>Log in as {token_info.username}</p>
										<Button icon="arrow-right" on:click={() => location.reload()}>Log In</Button>
								{:else}
										<p>Unknown token type {token_info.purpose}</p>
								{/if}
						{/if}
						{#if token_info == null && token_error === null}
								<Loader/>
						{/if}
						{#if token_error !== null}
								<div style="display: flex; align-items: center; gap: 5px;"><Icon icon="alert" color="red"/> {token_error} </div>
						{/if}
				{/if}
		{:else}
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
		{/if}
</DefaultFrame>
