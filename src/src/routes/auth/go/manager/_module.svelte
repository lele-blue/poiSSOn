
<script>
import Icon from "@components/Icon.svelte"
import SidebarItem from "@components/SidebarItem.svelte"
import Button from "@components/Button.svelte"
import Loader from "@components/Loader.svelte"
import Input from "@components/Input.svelte"
import {fly, slide} from "svelte/transition"
import {goto} from "@roxi/routify"
import {check_login} from "@/snippets/check_login.ts"
import Dialogs from "@components/Dialogs.svelte"

let manage_pages = import("../../../../data/settings.json")

import {currentUser} from "@/state/currentUser.ts"


export let back = null;
export let settings = true;

let search_term = "";


check_login()


</script>

<style>
    .manager_root {
        background-image: url("/auth/go/static/resolve/login_bg.jpg");
        height: 100vh;
        background-size: cover;
        display: grid;
        grid-template-columns: minmax(200px, 10vw) 1fr;
    }

    .highlight_wrapper {
        max-height: 100%;
        width: 100%;
        display: flex;
        margin-top: 40px;
        justify-content: center;
        overflow-y: auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .highlight_box {
        padding: 5px;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(8px);
        flex-direction: column;
        align-items: center;
        font-family: sans-serif;
        gap: 10px;
    }

    .highlight_box__content {
        padding: 20px;
        border-radius: 3px;
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
        z-index: 10;
    }

    aside {
        margin-top: 40px;
        height: calc(100% - 40px - 10px);
    }

</style>

<Dialogs/>
{#if $currentUser}
    <div in:fly={{y: -40}} class="topbar">
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
        </div>
{/if}
<div class="manager_root">
    <aside class="highlight_box">
        <Input icon="search" placeholder="Search Settings" full_width={true} bind:value={search_term}/>
        {#await manage_pages}
            <Loader/>
        {:then pages}
            {#each pages.categories as category}
                <SidebarItem {...category} {search_term}>{category.name}</SidebarItem>
            {/each}
        {/await}
    </aside>
    <div class="highlight_wrapper">
        <div class="highlight_box login_box highlight_box__content">
            <slot/>
        </div>
    </div>
</div>
