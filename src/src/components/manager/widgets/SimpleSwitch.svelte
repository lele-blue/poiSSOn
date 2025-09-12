<script>
    import Switch from "@components/Switch.svelte"
    import Loader from "@components/Loader.svelte"

    export let setting;
		export let error;

    let loading = true;

    export let value = "";
    let last_saved_value = null;
    function load(setting) {
        setting.get({boolean: true}).then(async val => {
            last_saved_value=val;
            value=val; 
            loading = false
        })
    };
    $: load(setting);
    function save() {
        if (last_saved_value !== null && last_saved_value != value) {
            last_saved_value = value;
            loading = true;
						setting.set(value).then(() => loading = false).catch(() => {value = !value; last_saved_value = value; loading = false});
        }
    }
		$: save(value);
</script>

{#if loading}
    <Loader/>
{/if}
<Switch bind:value {error}/>
