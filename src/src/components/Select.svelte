<script lang="ts">
    import {createEventDispatcher, onDestroy, onMount, tick} from "svelte";
    import Icon from "./Icon.svelte";
		import {ripple} from "../snippets/Ripple";
    import {slide, fade, scale} from "svelte/transition"

    export let value;
    export let icon = null;

    /** @type HTMLSelectElement & Node*/
    let select;
    /** @type MutationObserver*/
    let mo;

    let focused = false;
    let opened = false;

    const options = [];
    const dispatch = createEventDispatcher();

    function rescan_options() {
        /** @type HTMLOptionElement*/
        let option;

        for (option of select.children) {
            for (let child of option.children) {
                child.style.pointerEvents = "none";
            }

            options.push({content: option.innerHTML, value: option.value})
        }

    }

    onMount(() => {
        mo = new MutationObserver(rescan_options)
        mo.observe(select, {subtree: true, childList: true})

        rescan_options();
    })

    onDestroy(() => {
        mo.disconnect()
    })

    function click(event) {
        if (opened) {
            if (!event.target.classList.contains("select_menu_option")) {
                event.preventDefault();
                event.stopPropagation();
                event.cancelBubble = true;
                opened = false;
            }
        }
    }

    function position_menu(node: Node, {target}) {
        const rect = target.getBoundingClientRect();
				const root = document.querySelector(".login_box");

				// node.style.left = rect.left + "px";

        if (rect.top > (root.innerHeight)/2) {
            node.style.bottom = (root.innerHeight - rect.top) + "px";
        }
        else {
            node.style.top = rect.bottom + 2 - root.getBoundingClientRect().top + "px"; 
        }
    }

    function keydown(event) {
        if (event.code === "Escape") {
            opened = false;
        }
    }
</script>

<style>
    .select_root {
        position: relative;
        height: 31px;
        min-width: 2rem;
        background: var(--material-background-important);
        border-radius: 4px;
        border-bottom: var(--icon-secondary-col) 2px solid;
        user-select: none;
    }

    select {
        opacity: 0;
        width: 100%;
        height: 100%;
        transform: translateY(-100%);
        pointer-events: none;
    }

    .active_bar {
        position: absolute;
        bottom: -2px;
        width: 100%;
        left: 0;
        height: 3px;
        background: var(--material-accent-color);
        transform: scale(0, 1);
        transition: 0.2s ease;
        border-bottom-left-radius: 2px;
        border-bottom-right-radius: 2px;
    }

    .select_root.focused .active_bar {
        transform: scale(1, 1);
    }

    .content {
        flex-grow: 1;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .select_menu {
        box-shadow: 0 0 8px 0 black;
        position: fixed;
        background: var(--material-background-color);
        border-radius: 5px;
        z-index: 100;
    }

    .select_menu_option:first-child {
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
    }

    .select_menu_option:last-child {
        border-bottom-right-radius: 5px;
        border-bottom-left-radius: 5px;
    }

    .select_menu_option {
        padding: 10px 5px;
        user-select: none;
    }
    .select_menu_option:hover {
        background-color: var(--material-accent-color-light);
        color: var(--material-accent-color-text);
    }

    .select_icon {
        display: flex;
        align-items: center;
        transition: transform 0.2s ease;
    }

    .select_icon.opened {
        transform: rotate(180deg);
    }
</style>

<svelte:window on:click|capture={click} on:keydown={keydown}/>

<div class="select_root" class:focused={focused || opened} on:click|capture|preventDefault={event => {opened = !opened; event.stopPropagation()}}>
    <div class="flex flex-align-items-center" style="height: 100%; display: flex;
    align-items: center;
    padding-left: 5px;" aria-hidden="true">
        {#if icon}
            <div class="flex flex-align-items-center" style="margin: 0 3px">
                <Icon {icon} color={focused? "var(--material-accent-color)": "var(--icon-secondary-col)"}/>
            </div>
        {/if}
        <div class="content" class:opened>
            {#if select}
                {@html options[select.selectedIndex].content}
            {/if}
        </div>
        <div class="select_icon">
            <Icon color="var(--icon-secondary-col)" icon="chevron-down"/>
        </div>
    </div>
    <select bind:value bind:this={select} on:change={async () => {await tick(); select = select; opened = false; dispatch("change")}} on:focus={() => {focused = true}} on:blur={focused = false}>
        <slot/>
    </select>
    <div class="active_bar" aria-hidden="true"></div>
</div>
{#if opened}
    <div aria-hidden="true" class="select_menu" use:position_menu={{target: select}} out:scale in:slide={{duration: 200}} style="width: {select.getBoundingClientRect().width}px">
        {#each options as option, i}
            <div use:ripple transition:fade={{delay: i*100}} on:click={async () => {value = option.value; await tick(); select = select; opened = false; dispatch("change")}} class="select_menu_option">{@html option.content}</div>
        {/each}
    </div>
{/if}
