<script lang="ts">
    import Loader from "@/components/Loader.svelte"
    import Icon from "@/components/Icon.svelte"

    import Setting from "@/components/manager/Setting.svelte"

    import {params} from "@roxi/routify"
    const settingsPr = import("@/data/settings.json");

    export let page;
    let section = $params["section"];

    let settings = null;
    let error = null;

    settingsPr.then(json => {
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
        settings = pageData;
    })

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
    {#each settings.content as content}
        <Setting {...content}/>
    {:else}
        <p>Missing permissions to view/edit settings</p>
    {/each}
{/if}

