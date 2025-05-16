<script lang="ts">
    import Loader from "@/components/Loader.svelte"
    import Icon from "@/components/Icon.svelte"

    import Setting from "@/components/manager/Setting.svelte"

    import {params} from "@roxi/routify"
    const settingsPr = import("@/data/settings.json");

    $: page = ($params["data"] ?? [])[0];
    $: section = $params["section"];

    let settings = null;
    let error = null;

    function load(json) {
        let sectionData;
        if ((sectionData = json.categories.filter(cat => cat.slug === section)[0]) == undefined) {
            error = `${section} not found`;
            return;
        }
        let pageData;
        if ((pageData = sectionData.pages.filter(pageData => pageData.slug === page)[0]) === undefined) {
            error = `${page} not found`;
            return;
        }
        if ($params["data"].length - 1 > (pageData.extra_data_depth ?? 0)) {
            error = `${page} cannot work with this data amount`;
            return
        }
        settings = pageData;
    }

    $: {
        settingsPr.then(load);
        // use page and section somewhere so the reactive block is run on change
        void (page, section);
    }

</script>

{#if error}
    <Icon color="red" icon="alert" />
        {error}
{/if}
{#if settings == null}
    <Loader/>
{:else}
    <h1>{settings.name}</h1>
    <p>{settings.header_text}</p>
    {#each settings.content as content (`${section}/${page}/${content.name}}`)}
        <Setting {...content} extra_data={$params.data?.slice(1)}/>
    {:else}
        <p>Missing permissions to view/edit settings</p>
    {/each}
{/if}

