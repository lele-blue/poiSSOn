<script>
import Icon from "./Icon.svelte"
import Button from "./Button.svelte"
import {fly, slide} from "svelte/transition"
import {goto} from "@roxi/routify"

import {currentUser} from "../state/currentUser.ts"


export let back = null;
export let settings = true;


</script>

<style>
    .login_root {
        background-image: url("/auth/go/static/resolve/login_bg.jpg");
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
    }

    .topbar {
        display: flex;
        align-items: center;
        gap: 5px;
        height: 40px;
        width: 100vw;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(8px);
        position: fixed;
        top: 0;
        box-shadow: 1px 1px 5px 2px #00000045;
        font-family: sans-serif;
    }

</style>

{#if $currentUser}
    <div in:fly={{y: -40}} class="topbar">
        {#if back}
            <div in:slide>
                <Button dialogButton={true} on:click={() => $goto(back)} icon="chevron-left">Back</Button>
            </div>
        {/if}
        <Icon icon="account"/>
        <span>Logged in as {$currentUser}</span>
        <div style="flex-grow: 1"/>
        {#if settings}
            <div in:slide>
                <Button on:click={$goto("/auth/go/settings")} icon="cog" dialogButton={true}>Settings</Button>
            </div>
        {/if}
        </div>
{/if}
<div class="login_root">
    <div class="login_wrapper">
        <div class="login_box">
            <slot/>
        </div>
    </div>
</div>
