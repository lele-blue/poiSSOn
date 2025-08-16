<script>
import Icon from "@components/Icon.svelte"
import SidebarItem from "@components/SidebarItem.svelte"
import Button from "@components/Button.svelte"
import Loader from "@components/Loader.svelte"
import TopBar from "@components/TopBar.svelte"
import Input from "@components/Input.svelte"
import {fly, slide} from "svelte/transition"
import {onDestroy} from "svelte"
import {goto, url} from "@roxi/routify"
import {check_login} from "@/snippets/check_login.ts"
import Dialogs from "@components/Dialogs.svelte"

let manage_pages = import("../../../../data/settings.json")

import {currentUser} from "@/state/currentUser.ts"


let search_term = "";


check_login()

let sidebar_active = false;

onDestroy(url.subscribe(() => sidebar_active = false))


</script>

<style>
    .manager_root {
        background-image: var(--poisson-theme-bg);
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
        overflow-y: hidden;
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
        overflow-y: auto;
        max-height: 100%;
    }

    .highlight_box__content {
        padding: 20px;
        border-radius: 3px;
    }

    aside {
        margin-top: 40px;
        height: calc(100% - 40px - 10px);
    }

    .expand-sidebar {
        display: none;
    }

    @media screen and (max-width: 700px) {
        .manager_root {
            grid-template-columns: 1fr;
        }

        aside {
            width: calc(100vw - 10px);
            transform: translateX(-100vw);
            position: absolute;
            transition: .3s ease transform;
            z-index: 20;
        }

        aside.active {
            transform: translateX(0); 
        }

        .expand-sidebar {
            display: block;
        }
    }

</style>

<Dialogs/>
<TopBar settings={!location.pathname.startsWith("/auth/go/manager/oobe")}>
    <div slot="before" class="expand-sidebar">
        <Button on:click={() => sidebar_active = !sidebar_active} icon="menu" dialogButton={true}/>
    </div>
</TopBar>
<div class="manager_root">
    <aside class="highlight_box" class:active={sidebar_active}>
        {#if !location.pathname.startsWith("/auth/go/manager/oobe") }
            <Input icon="search" placeholder="Search Settings" full_width={true} bind:value={search_term}/>
            {#await manage_pages}
                <Loader/>
            {:then pages}
                {#each pages.categories.filter(category => category.hidden !== true) as category}
                    <SidebarItem {...category} {search_term}>{category.name}</SidebarItem>
                {/each}
            {/await}
        {/if}
    </aside>
    <div class="highlight_wrapper">
        <div class="highlight_box login_box highlight_box__content">
            <slot/>
        </div>
    </div>
</div>
