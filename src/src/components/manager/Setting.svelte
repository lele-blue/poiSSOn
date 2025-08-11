<script>
    import {params} from "@roxi/routify"
    import {slide} from "svelte/transition"

    import Button from "@components/Button.svelte"
    import Loader from "@components/Loader.svelte"
    import Icon from "@components/Icon.svelte"
    import AlertBox from "@components/AlertBox.svelte"

    import {showDialog} from "@/state/dialogs"

    export let name;
    export let help_text = null;
    export let type;
    export let type_data = {};
    export let widget;
    export let widget_data = {};
    export let warn_if = [];
    export let extra_data = null;
    export let extended = false;
    export let content = null; // this is just for context groups nested settings


    const setting_type_map = {
        "poisson.core_setting": async () => (await import("@components/manager/coreSetting")).default,
        "poisson.users": async () => (await import("@components/manager/users")).default,
        "poisson.user": async () => (await import("@components/manager/user")).default,
        "null": async () => class{}
    }

    const setting_widget_map = {
        "poisson.context_group": () => null, // is special, handled in this component
        "poisson.simple.choice": () => import("@components/manager/widgets/SimpleSelect.svelte"),
        "poisson.simple.input": () => import("@components/manager/widgets/SimpleInput.svelte"),
        "poisson.table": () => import("@components/manager/widgets/Table.svelte"),
        "poisson.choice.link":  () => import("@components/manager/widgets/LinkChoice.svelte"),
        "poisson.custom.theme": () => import("@components/manager/widgets/ThemeChoose.svelte"),
    }

    export let external_setting = null; // in context groups, the setting is provided by the parent
    export const group_key = null;

    let setting = null;

    let value;

    $: {
        if (external_setting) setting = external_setting;
        else setting_type_map[type]().then(val => setting = new val(type_data, extra_data));
    }

    // injects the key option into the setting get/set calls
    function wrap_setting(setting, key) {
        const handler = {
            get(target, prop, receiver) {
                if (prop === "get") {
                    return function(options) {
                        return target[prop].apply(this === receiver ? target : this, [{...options, key}]);
                    }
                }
                else if (prop === "set") {
                    return function(value, options) {
                        return target[prop].apply(this === receiver ? target : this, [value, {...options, key}]);
                    }
                }
                const value = target[prop];
                if (value instanceof Function) {
                  return function (...args) {
                    return value.apply(this === receiver ? target : this, args);
                  };
                }
                return value;
            }
        }
        return new Proxy(setting, handler);
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

    .setting.extended {
        flex-direction: column;
        align-items: flex-start;
    }
</style>

{#if widget === "poisson.context_group"}
    {#if !setting}
        <Loader/>
    {:else}
        {#await setting.context_group_init()}
            <Loader/>
        {:then}
            {#each content as content (`${name}/context_group/${content.name}}`)}
                <!-- wrap the settings to inject the key via the options parameter -->
                <svelte:self {...content} 
                    external_setting={wrap_setting(setting, content.group_key)} 
                    extra_data={$params.data?.slice(1)}
                />
            {:else}
                <p>No settings in this context block</p>
            {/each}
        {/await}
    {/if}
{:else}
    <div class="setting" class:extended>
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
        {#each warn_if.filter(warn => warn.call && value !== undefined) as {call}}
            {#await setting[call](value)}
                <!-- -->
            {:then message}
                {#if message}
                    <div transition:slide class="setting" style="justify-content: left;">
                        <Icon icon="alert" color="orange"/>
                        {message}
                    </div>
                {/if}
            {/await}
        {/each}
        {#each warn_if.filter(warn => warn.match && value && value.match(warn.match)) as {message}}
            <div transition:slide class="setting" style="justify-content: left;">
                <Icon icon="alert" color="orange"/>
                {@html message}
            </div>
        {/each}
    {/if}
{/if}
