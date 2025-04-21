<script>
import Icon from "./Icon.svelte"
import Button from "./Button.svelte"
import LoadButton from "./LoadButton.svelte"
import {currentUser} from "../state/currentUser.ts"
import {fly, slide} from "svelte/transition"
import {post} from "@/snippets/fetch"
import {goto} from "@roxi/routify"


export let back = null;
export let settings = true;

async function logout() {
    await post("/auth/api/logoff", {});
    currentUser.set(null);
    $goto("/auth", {next: location.href});
}
</script>


<style>
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
        z-index: 10;
    }
</style>
{#if $currentUser}
    <div in:fly={{y: -40}} class="topbar">
        <slot name="before"/>
        {#if back}
            <div in:slide>
                <Button dialogButton={true} on:click={() => $goto(back)} icon="chevron-left">Back</Button>
            </div>
        {/if}
        <Icon icon="account"/>
        <span>Logged in as {$currentUser.username}</span>
        <div style="flex-grow: 1"/>
        {#if settings}
            <div in:slide>
                <Button on:click={$goto("/auth/go/settings")} icon="cog" dialogButton={true}>Settings</Button>
            </div>
        {/if}
        <div>
            <LoadButton dialogButton={true} icon="logout" on:clicked={event => event.detail.waitUntil(logout())}>Log out</LoadButton>
        </div>
        </div>
{/if}
