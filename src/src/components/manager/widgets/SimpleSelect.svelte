<script>
    import Select from "@components/Select.svelte"
    import Loader from "@components/Loader.svelte"

    export let choices = [];
    export let setting;

    let loading = true;

    export let value;
    let last_saved_value;
    function load(setting) {
        setting.get().then(val => {
            last_saved_value=val;
            value=val; 
            loading = false
        })
    };
    $: load(setting);
    $: {
        if (value && last_saved_value && last_saved_value != value) {
            last_saved_value = value;
            loading = true;
            setting.set(value).then(() => loading = false);
        }
    }
</script>

<Select bind:value>
    {#each choices as {key, text}}
        <option value={key}>{text}</option>
    {/each}
</Select>

{#if loading}
    <Loader/>
{/if}
