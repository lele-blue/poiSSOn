<script>
    import Loader from "../../../components/Loader.svelte";
    import Icon from "../../../components/Icon.svelte";

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = () => getCookie('csrftoken');

    let error = null;


    (async () => {
        const res = await fetch("/auth/api/next_credentials/retrieve", {method: "POST", headers: {"X-CSRFToken": csrftoken()}});
        const data = await res.json();

        const res2 = await fetch("/foundry/join", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({action: "join", adminKey: "", password: data.passwordPlain, userid: data.username})
        });

        try {
            let data = await res2.json();
            if (!data.redirect) {
                error = "Falsche zugangsdaten :("
                return;
            }
            location.href = data.redirect;
        } catch (e) {
            error = "Foundry verhält sich weird, kp was los ist :/"
        }
    })()
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
            {#if error}
                <Icon icon="alert"/>
                {error}
            {:else}
                <Loader/>
            {/if}
        </div>
    </div>
</div>