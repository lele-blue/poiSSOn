<script>
    import Icon from "./Icon.svelte";
    import {slide} from "svelte/transition";
    import {createEventDispatcher} from "svelte";
    export let placeholder;
    export let value = "";
		export let autocomplete;
    export let icon = null;
    export let error = null;
    export let trailingIcon = null;
    export let password = false;

    $: endIcon = error? 'alert-circle': trailingIcon;

    let focused = false;
    $: content = value.length;
    $: focused2 = focused || content;

    const dispatch = createEventDispatcher();

    let labelElem;
    let wiggleElem = false;

    function wiggle() {
        wiggleElem = false;
        setTimeout(() => {
            void labelElem.offsetWidth;
            wiggleElem = true;
        }, 10)
    }

    function keydown(event) {
        if (event.code === "Enter") {
            dispatch("submitted")
        }
    }
</script>

<style>
    input {
        border: none;
        border-bottom: var(--icon-secondary-col) 2px solid;
        transition: 0.4s ease;
        background: var(--material-background-important);
        width: calc(100% - 10px - var(--left-padding));
        margin: 0;
        border-radius: 4px;
        padding: 11px 10px 4px var(--left-padding);
    }

    input.error {
        border-color: var(--material-error-color);
    }

    input:focus {
        outline: none;
        /*border-color: var(--material-accent-color);*/
    }

    .label {
        display: flex;
        position: absolute;
        top: calc(50% - 1em + 5px);
        left: var(--left-padding);
        transition: 0.2s ease;
        color: var(--icon-secondary-col);
        pointer-events: none;
        align-items: center;
    }

    .label.content {
        transform: scale(0.7);
        transform-origin: left 50%;
        top: -10px;
    }

    @keyframes wiggle {
        0% {
            transform: translateX(0px) scale(0.7);
        }
        50% {
            transform: translateX(5px) scale(0.7);
        }
        100% {
            transform: translateX(0px) scale(0.7);
        }
    }

    .label.wiggle {
        animation: wiggle 1 cubic-bezier(0.68, -0.55, 0.27, 1.55) 0.5s;
    }

    .label.content.focused {
        color: var(--material-accent-color)
    }

    label {
        position: relative;
        --left-padding: 10px;
        margin: 0 0 0.5em 0;
    }

    label.icon {
        --left-padding: calc(10px + 24px);
    }

    .icon-container {
        top: calc(50% - 1em + 3px);
        left: 3px;
        position: absolute;
    }

    .active_bar {
        height: 3px;
        width: 100%;
        position: absolute;
        bottom: -5px;
        left: 0;
        transform: scale(0, 1);
        transform-origin: 50% 50%;
        background: var(--material-accent-color);
        transition: 0.4s ease;
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
    }

    .active_bar.focused {
        transform: scale(1, 1);
    }

    .icon-container-end {
        right: 3px;
        left: unset;
    }

    .input-error {
        color: var(--material-error-color);
        font-size: 0.8em;
        margin-bottom: 5px;
        margin-left: 7px;
    }

    .label.error {
        color: var(--material-error-color) !important;
    }
</style>

<div style="border-radius: 3px; width: 80%">
    <label class:icon>
        {#if icon}
            <div aria-hidden="true" class="icon-container">
                <Icon {icon} color={focused?"var(--material-accent-color)":"var(--material-ambient-color)"}/>
            </div>
        {/if}
        <span bind:this={labelElem} class:wiggle={wiggleElem && content} class="label" class:content class:focused class:error>{placeholder}</span>
        {#if password}
            <input on:keydown={keydown} {autocomplete} type="password" class:error bind:value on:focus={() => {focused = true}} on:blur={() => {focused = false; if(error) wiggle()}}>
        {:else}
            <input on:keydown={keydown} {autocomplete} class:error bind:value on:focus={() => {focused = true}} on:blur={() => {focused = false; if(error) wiggle()}}>
        {/if}
        {#if endIcon}
            <div aria-hidden="true" class="icon-container icon-container-end" title={error}>
                <Icon icon={endIcon} color={error?"var(--material-error-color)":"var(--material-ambient-color)"}/>
            </div>
        {/if}
        <!--suppress CheckEmptyScriptTag -->
        <div aria-hidden="true" class="active_bar" class:focused/>
    </label>
    {#if error}
        <div transition:slide class="input-error">{error}</div>
    {/if}
</div>
