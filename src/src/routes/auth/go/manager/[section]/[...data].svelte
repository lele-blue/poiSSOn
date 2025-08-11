<script lang="ts">
    import Loader from "@/components/Loader.svelte"
    import Icon from "@/components/Icon.svelte"

    import Setting from "@/components/manager/Setting.svelte"
    import {contextStore} from "@/state/globalContextStore"

    import {params} from "@roxi/routify"
    const settingsPr = import("@/data/settings.json");


    $: page = ($params["data"] ?? [])[0];
    $: section = $params["section"];

    let settings = null;
    let error = null;

    function load(json) {
        settings= null;
        error = null;
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
        let subpagedata = pageData;
        for(let i = 1;;i++) {
            if ($params.data[i] && (subpagedata = (subpagedata.subpages[$params.data[i]] || subpagedata.subpages["*"]))) {
                pageData = subpagedata;
            }
            else break;
        }
        settings = pageData;
    }

    $: {
        settingsPr.then(load);
        // use page and section somewhere so the reactive block is run on change
        void (page, section, $params);
    }

</script>

{#if error}
    <Icon color="red" icon="alert" />
        {error}
{/if}
{#if settings == null}
    <Loader/>
{:else}
    {#if settings.name.match(/\$\{.+\}/)}
        <h1>{$contextStore[settings.name.match(/\$\{(.+)\}/)[1]] ?? "Loading..."}</h1>
    {:else}
        <h1>{settings.name}</h1>
    {/if}
    <p>{settings.header_text}</p>
    {#each settings.content as content (`${section}/${page}/${content.name}}`)}
        <Setting {...content} extra_data={$params.data?.slice(1)}/>
    {:else}
        <p>Missing permissions to view/edit settings</p>
    {/each}
{/if}

