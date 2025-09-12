<script context="module">
    let id_setting_map = {};
</script>

<script>
    import {params} from "@roxi/routify"
    import {slide} from "svelte/transition"
    import {onDestroy} from "svelte"
    import {readable} from "svelte/store"

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
    export let form = false;
    export let derived = false;
    export let id = undefined;
    export let condition = null;
    export let widget_data = {};
    export let warn_if = [];
    export let extra_data = null;
    export let extended = false;
    export let hidden = false;
    export let content = null; // this is just for context groups nested settings

    let prev_id;
    $: {
        if (prev_id !== undefined && prev_id !== id) {
            id_setting_map[prev_id] = undefined;
            // fixme clearing should not be necessary
            id_setting_map = {};
            call_on_id_change.map(elem => elem());
            call_on_id_change = [];
            current_condition_met = false;
            prev_id = id;
            errors = readable();
        }
        else if (prev_id === undefined) prev_id = id ?? null;
    }
    onDestroy(() => {
        id_setting_map[id] = undefined;
        // fixme clearing should not be necessary
        call_on_id_change.map(elem => elem());
        id_setting_map = {};
        call_on_id_change = [];
        errors = readable();
    })

    const setting_type_map = {
        "poisson.core_setting": async () => (await import("@components/manager/coreSetting")).default,
        "poisson.users": async () => (await import("@components/manager/users")).default,
        "poisson.user": async () => (await import("@components/manager/user")).default,
        "poisson.oobe.admin_creation": async () => (await import("@components/manager/oobe_admin_creation")).default,
        "poisson.oobe.finish": async () => (await import("@components/manager/oobe_finish")).default,
        "null": async () => class{}
    }

    const setting_widget_map = {
        "poisson.context_group": () => null, // is special, handled in this component
        "poisson.simple.choice": () => import("@components/manager/widgets/SimpleSelect.svelte"),
        "poisson.simple.input": () => import("@components/manager/widgets/SimpleInput.svelte"),
        "poisson.simple.switch": () => import("@components/manager/widgets/SimpleSwitch.svelte"),
        "poisson.table": () => import("@components/manager/widgets/Table.svelte"),
        "poisson.timedelta": () => import("@components/manager/widgets/TimeRange.svelte"),
        "poisson.choice.link":  () => import("@components/manager/widgets/LinkChoice.svelte"),
        "poisson.custom.theme": () => import("@components/manager/widgets/ThemeChoose.svelte"),
        "poisson.custom.oobe_nav": () => import("@components/manager/widgets/OOBENav.svelte"),
    }

    export let external_setting = null; // in context groups, the setting is provided by the parent
    export let group_key = null;

    let setting = null;

    let value;

    let call_on_id_change = [];

    // ugly workaround so the reactive block is not reexeced when id is written
    function on_setting_ready(new_setting, create=true) {
        if (create) setting = new new_setting(type_data, extra_data);
        if (id) id_setting_map[id] = setting;
        if (setting.errors) {
            errors = setting.errors;
        }
        setting.reload = () => setting_type_map[type]().then(on_setting_ready)
    }


    $: {
        // when extra data changes, re-init settings
        void(extra_data);

        if (external_setting) {
            setting = external_setting;
            on_setting_ready(external_setting, false);
        }
        else setting_type_map[type]().then(on_setting_ready);
    }

    $: {
        if (condition) {
            resolve_condition(condition);
        }
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

    let current_condition_met = false;
    let errors = readable({});

    async function resolve_condition(condition) {
        if (condition.call) {
            current_condition_met = await setting[condition.call]();
            if (condition.invert) {
                current_condition_met = !current_condition_met;
            }
        }
        if (condition.by_id) {
            let rem = 10
            while (rem-- > 0) {
                if (!id_setting_map[condition.by_id]) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                    continue;
                }
                const setting = id_setting_map[condition.by_id];
                const store = setting.get_store();
                call_on_id_change.push(store.subscribe(cond_new_val => {
                    current_condition_met = cond_new_val === condition.match;
                }));
                break;
            }
        }
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

    .hidden {
        display: none;
    }
</style>

{#if widget === "poisson.context_group"}
    {#if !setting}
        <Loader/>
    {:else}
        {#await setting.context_group_init()}
            <Loader/>
        {:then}
            {#if form}
                <form>
                    {#each content as content (`${name}/context_group/${content.name}}`)}
                        <!-- wrap the settings to inject the key via the options parameter -->
                        <svelte:self {...content} 
                            external_setting={wrap_setting(setting, content.group_key)} 
                            extra_data={$params.data?.slice(1)}
                        />
                    {:else}
                        <p>No settings in this context block</p>
                    {/each}
                </form>
            {:else}
                {#each content as content (`${name}/context_group/${content.name}}`)}
                    <!-- wrap the settings to inject the key via the options parameter -->
                    <svelte:self {...content} 
                        external_setting={wrap_setting(setting, content.group_key)} 
                        extra_data={$params.data?.slice(1)}
                    />
                {:else}
                    <p>No settings in this context block</p>
                {/each}
            {/if}
        {/await}
    {/if}
{:else}
    {#if (condition && current_condition_met) || !condition}
        <div class="setting" class:extended class:hidden>
            <div class="setting-title">
                <label for="poisson-settings-element-{name.replaceAll(" ","")}">
                    <h3>{#if derived}→{/if}{name}</h3>
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
                    <svelte:component bind:value error={$errors[group_key ?? "@"]} this={component.default} {...widget_data} {setting}/>
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
{/if}
