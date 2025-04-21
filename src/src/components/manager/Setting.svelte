<script>
    import {slide} from "svelte/transition"

    import Button from "@components/Button.svelte"
    import Loader from "@components/Loader.svelte"
    import Icon from "@components/Icon.svelte"
    import AlertBox from "@components/AlertBox.svelte"

    import {showDialog} from "@/state/dialogs"

    export let name;
    export let help_text;
    export let type;
    export let type_data;
    export let widget;
    export let widget_data;
    export let warn_if;


    const setting_type_map = {
        "poisson.core_setting": async () => (await import("@components/manager/coreSetting")).default,
    }

    const setting_widget_map = {
        "poisson.simple.choice": () => import("@components/manager/widgets/SimpleSelect.svelte"),
    }

    let setting = null;

    let value;

    $: {
        setting_type_map[type]().then(val => setting = new val(type_data));
    }

</script>

<style>
    .setting-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 45vw;
    }

    .setting {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>

<div class="setting">
    <div class="setting-title">
        <label for="poisson-settings-element-{name.replaceAll(" ","")}">
            <h3>{name}</h3>
        </label>
        {#if help_text}
            <div>
                <Button icon="help-circle" dialogButton={true} on:click={showDialog(AlertBox, {title: name, text: help_text, is_html: true})}/>
            </div>
        {/if}
    </div>
    {#if setting}
        {#await setting_widget_map[widget]()}
            <Loader/>
        {:then component}
            <svelte:component bind:value this={component.default} {...widget_data} {setting}/>
        {/await}
    {/if}
</div>
{#if warn_if}
    {#each warn_if.filter(warn => value && value.match(warn.match)) as {message}}
        <div transition:slide class="setting" style="justify-content: left;">
            <Icon icon="alert" color="orange"/>
            {@html message}
        </div>
    {/each}
{/if}
