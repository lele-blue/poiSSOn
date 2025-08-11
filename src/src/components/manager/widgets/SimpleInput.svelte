<script>
    import Input from "@components/Input.svelte"
    import Loader from "@components/Loader.svelte"
    import Button from "@components/Button.svelte"

    export let setting;
    export let input = {};

    let loading = true;

    export let value = "";
    let last_saved_value;
    function load(setting) {
        setting.get().then(val => {
            last_saved_value=val;
            value=val; 
            loading = false
        })
    };
    $: load(setting);
    function save() {
        if (value && last_saved_value && last_saved_value != value) {
            last_saved_value = value;
            loading = true;
            setting.set(value).then(() => loading = false);
        }
    }
</script>

<Input bind:value {...input} on:submit_intent={save} />


{#if loading}
    <Loader/>
{/if}
