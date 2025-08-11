<script>
    import Loader from "@components/Loader.svelte"
    import LoadButton from "@components/LoadButton.svelte"
    import Icon from "@components/Icon.svelte"
    import {goto, url} from "@roxi/routify"
    import { flip } from 'svelte/animate';
    import { slide } from 'svelte/transition';


    export let columns = [];
    export let setting;

    let loading = true;

    export let value;
    export let sort_by;
    let sort_dir = "asc";
    export let actions = [];
    export let uid_key = "uid";
    export let no_data_text = "No Entries";
    export let add_button = null;
    export let paginate = false;
    let add_params = {}
    let next, previous, count;

    async function load(setting, options) {
        const resp = await setting.get(options);
        value = paginate?resp.results:resp;
        if (paginate) {
            ({next, previous, count} = resp);
        }
        loading = false;
        
    };
    $: load(setting);

    function process_goto(path, params, elem, func) {
        let params_entries = Object.entries({...params});
        for (let i = 0; i<params_entries.length;i++) {
            if (Array.isArray(params_entries[i][1])) {
                for (let u = 0; u<params_entries[i][1].length;u++) {
                    let match;
                    if (match = params_entries[i][1][u].match(/\$\{(.+)\}/)) {
                        // copy the array so the result is not written back (reference shenanigans)
                        params_entries[i][1] = [...params_entries[i][1]];
                        params_entries[i][1][u] = setting[match[1]](elem)
                    }
                }
            }
        }
        return(func ?? $goto)(path, Object.fromEntries(params_entries));
    }

    function add() {
        if (add_button.action === "url") {
            process_goto(add_button.action_data.path, add_button.action_data.params, null);
        }
    }

    function navigate(url) {
        add_params = {...Object.fromEntries(new URLSearchParams((new URL(url)).search).entries())};
        return refetch();
    }

    async function refetch(key) {
        if (key) {
            add_params = {}
            if (key === sort_by) {
                if (sort_dir === "asc") sort_dir = "desc";
                else sort_dir = "asc";
            }
            else {
                sort_dir = "asc";
                sort_by = key;
            }
        }
        await load(setting, {
            sort: sort_by?{
                key: sort_by,
                dir: sort_dir,
            }:undefined,
            add_params
        });
    }
</script>

<style>

    th>div, .warning {
        display: flex;
        align-items: center;
    }

    .bold {
        font-weight: bold;
    }

    .data {
        display: flex;
        flex-direction: column;
    }
    .pagination {
        display: flex;
        align-items: center;
        justify-content: space-evenly;
        width: 100%;
        gap: 5px;
    }
    .table_wrapper {
        max-width: calc(100vw - 40px);
        overflow-x: auto;
    }

</style>

<div class="table_wrapper">
    <table>
        <thead>
            <tr>
                {#each columns as {text, icon, can_sort, key}}
                    <th scope="col">
                        <div style="white-space: nowrap;">
                            {#if icon}
                                <Icon {icon}/>
                            {/if}
                            {text}
                            {#if can_sort}
                                <LoadButton icon={sort_by === key?(sort_dir==="asc"?"sort-ascending":"sort-descending"):"sort"} dialogButton={true} on:clicked={event => {event.detail.waitUntil(refetch(key))}}/>
                            {/if}
                        </div>
                    </th>
                {/each}
            </tr>
        </thead>
        {#if value}
            <tbody>
                {#each value as data (data[uid_key ?? Math.random()])}
                    <tr
                        >
                        {#each columns as {key, column_role, warn_if, bold, link}}
                            {#if column_role == "actions"}
                                <td>
                                    {#each actions as {button, action, text, condition}}
                                        {#await (condition?setting[condition](data):Promise.resolve(true))}
                                            <Loader/>
                                        {:then fulfilled}
                                            <LoadButton {...button ?? {}} disabled={!fulfilled} on:clicked={event => event.detail.waitUntil(setting[action](data))}>{text}</LoadButton>
                                        {/await}
                                    {/each}
                                </td>
                            {:else}
                                <td>
                                    <div class="data">
                                        <span class:bold>
                                            {#if link}
                                                <a href={process_goto(link.path, link.params, data, $url)}>
                                                    {data[key]}
                                                </a>
                                            {:else}
                                                {data[key]}
                                            {/if}
                                        </span>
                                        {#if warn_if}
                                            {#await setting[warn_if](data)}
                                                <div/>
                                            {:then warning}
                                                {#if warning}
                                                    <div class="warning">
                                                        <Icon icon="alert" color="orange"/>
                                                        {@html warning}
                                                    </div>
                                                {/if}
                                            {/await}
                                        {/if}
                                                </div>
                                </td>
                            {/if}
                        {/each}
                    </tr>
        {:else}
            <tr>
                <td colspan={columns.length}>{no_data_text}</td>
            </tr>
                {/each}
            </tbody>
        {/if}
    </table>
</div>

{#if count && value}
    <div class="pagination">
        {#if next || previous}
            <LoadButton icon="chevron-left" dialogButton={true} disabled={!previous} on:clicked={event => event.detail.waitUntil(navigate(previous))}>Previous</LoadButton>
        {/if}
        <span style="white-space: pre;">Showing {value.length} of {count}</span>
        {#if next || previous}
            <LoadButton icon="chevron-right" reverse={true} dialogButton={true} disabled={!next} on:clicked={event => event.detail.waitUntil(navigate(next))}>Next</LoadButton>
        {/if}
    </div>
{/if}

{#if add_button && add_button.enable}
    <LoadButton icon="plus" on:clicked={add}>{add_button.text}</LoadButton>
{/if}

{#if loading}
    <Loader/>
{/if}
