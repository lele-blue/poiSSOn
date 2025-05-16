<script>
    import Loader from "@components/Loader.svelte"
    import LoadButton from "@components/LoadButton.svelte"
    import Icon from "@components/Icon.svelte"
    import {goto} from "@roxi/routify"
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

    function add() {
        if (add_button.action === "url") {
            console.log(add_button.action_data.href);
            $goto("/auth/go/manager/users/manager");
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

</style>

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
                    animate:flip={{duration: 100}}
                    transition:slide
                >
                    {#each columns as {key, column_role, warn_if, bold}}
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
                                        {data[key]}
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

{#if count && value}
    <div class="pagination">
        <LoadButton icon="chevron-left" dialogButton={true} disabled={!previous} on:clicked={event => event.detail.waitUntil(navigate(previous))}>Previous</LoadButton>
            <span style="white-space: pre;">Showing {value.length} of {count}</span>
        <LoadButton icon="chevron-right" dialogButton={true} disabled={!next} on:clicked={event => event.detail.waitUntil(navigate(next))}>Next</LoadButton>
    </div>
{/if}

{#if add_button && add_button.enable}
    <LoadButton icon="plus" on:clicked={add}>{add_button.text}</LoadButton>
{/if}

{#if loading}
    <Loader/>
{/if}
