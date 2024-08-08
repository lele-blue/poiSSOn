<script>
    import Icon from "./Icon.svelte";
    import Loader from "./Loader.svelte";
    import {ripple} from "../snippets/Ripple";

    export let icon = null;
    export let icon_color = "var(--icon-col)";
    export let positive = false;
    export let destroy = false;
    export let vertical = false;
    export let passive = false;
    export let grow = false;
    export let margin = false;
    export let noNewLine = false;
    export let loading = false;
    export let label = null;
    export let smallLink = false;
    export let dialogButton = false;

    let iconSize = undefined;

    $: {
        if (smallLink) {
            iconSize = "15"
        }
    }
</script>

<style>
    button {
        padding: 5px 7px;
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        border: 1px solid black;
        cursor: pointer;
        color: inherit;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 40px;
        min-height: 40px;

        background: var(--material-accent-color);
        border-radius: 3px;
        transition: background-color 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 0 3px 0px black;
        color: var(--material-accent-color-text);
        --icon-col: var(--material-accent-color-text);
        border: none;
        margin: 2px;
        width: 100%;
    }

    button:hover, button:focus {
        background: var(--material-accent-color-light);
        box-shadow: 0 0 5px 0px black;
    }

    button.positive {
        background: green;
    }

    button.positive:hover {
        background: #004a00;
    }

    button.destroy {
        background: red;
        color: white;
        --icon-col: white;
    }

    button.destroy:hover {
        background: #620000;
    }

    button.vertical {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100%;
        width: 100%;
    }

    button.passive {
        padding: 0;
        border: none;
        box-shadow: none;
        margin: 0;
    }

    button.grow {
        width: 100%;
        justify-content: center;
    }

    button.margin {
        margin: 2px;
    }

    button.noNewLine {
        white-space: nowrap;
    }

    button.smallLink {
        border: 1px solid transparent;
        background: transparent;
        font-size: inherit;
        transition: 0.2s ease;
        color: var(--material-text);
        --icon-col: var(--material-text);
    }

    button.smallLink:hover {
        border: 1px solid black;
        text-decoration: underline black;
    }

    button.dialogButton {
        background: transparent;
        color: var(--material-accent-color);
        --icon-col: var(--material-accent-color);
        box-shadow: none;
        text-transform: uppercase;
    }
</style>

<button use:ripple aria-label={label} on:click class:dialogButton class:smallLink class:noNewLine class:margin class:grow class:positive class:vertical class:destroy class:passive class="flex-align-items-center flex">
    {#if icon !== null && !loading}
        <Icon height={iconSize} width={iconSize} description={label} icon={icon} color={icon_color}/>
    {/if}
    {#if loading}
        <div style="margin: 0 2px">
            <Loader/>
        </div>
    {/if}
    <slot/>
</button>