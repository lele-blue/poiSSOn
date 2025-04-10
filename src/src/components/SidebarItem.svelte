<script lang="ts">
    import Icon from "@components/Icon.svelte"
    import {ripple} from "@/snippets/Ripple.ts"
    import {slide} from "svelte/transition"

    export let pages = [];
    export let icon;
    export let name;
    export let slug;

    export let active = false;

    export let search_term = "";

    $: my_search_terms = (() => {
        let result = {"all": [name, slug, icon]};
        for (const page of pages) {
            if (result[page.slug] === undefined) result[page.slug] = [];
            result[page.slug].push(page.name);
            result.all.push(page.name);
        }
        return result;
    })()
</script>

<style>
    .header {
        display: flex;
        align-items: center;
        gap: 5px;
        justify-content: space-between;
        cursor: pointer;
    }

    .root {
        margin: 5px;
        padding: 5px;
        padding-left: 0;
        --icon-col: var(--material-accent-color);
        background: transparent;
        transition: background .5s ease;
        border-radius: 3px;
    }

    .root.active {
        background: #ffffff44;
    }

    .title {
        font-weight: bold;
        color: var(--material-accent-color);
    }

    .title_chevron {
        transform: rotate(0deg);
        transition: .5s ease;
        transform-origin: center;
        display: flex;
    }

    .root.active .title_chevron {
        transform: rotate(180deg);
    }

    .items_list {
        margin: 0;
        list-style-type: none;
        padding: 10px;
    }

    a {
        color: var(--material-accent-color);
        text-decoration: none;
    }
</style>

{#if !search_term.length || my_search_terms.all.some(term => term.toLowerCase().includes(search_term.toLowerCase()))}
    <div class="root" class:active={active || search_term.length} transition:slide>
        <div class="header" use:ripple on:click={() => active = !active}>
            <Icon {icon}/>
            <span class="title">{name}</span>
            <div style="flex-grow: 1"/>
            <div class="title_chevron"><Icon icon="chevron-down"/></div>
            </div>
            {#if active || search_term.length}
                <div class="items" transition:slide>
                    <ul class="items_list">
                        {#each pages as page}
                            <li>
                                <a href="/auth/go/manager/{slug}/{page.slug}{search_term?`?q=${search_term}`:''}">→ {page.name}</a>
                            </li>
            {:else}
                <span>Nothing to manage here</span>
                        {/each}
                    </ul>
                </div>
            {/if}
        </div>
{/if}
