<script>
import TopBar from "@components/TopBar.svelte"


export let back = null;
export let settings = true;


</script>

<style>
    .login_root {
        background-image: var(--poisson-theme-bg);
        height: 100vh;
        width: 100vw;
        background-size: cover;
        display: flex;
        align-items: center;
    }

    .login_wrapper {
        max-height: 100vh;
        width: 100vw;
        display: flex;
        justify-content: center;
        overflow-y: auto;
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
        height: 100%;
    }


</style>

<TopBar {back} {settings}/>
<div class="login_root">
    <div class="login_wrapper">
        <div class="login_box highlight_box__content">
            <slot/>
        </div>
    </div>
</div>
