<script>
    import Input from "@components/Input.svelte"
    import Loader from "@components/Loader.svelte"
    import Button from "@components/Button.svelte"
    import Select from "@components/Select.svelte"

    export let setting;
    export let input = {};

    let loading = true;

		export let disabled_func = null;

		let disabled = false;

		let amount = "Days";

    export let value = "";
    let last_saved_value = null;
    function load(setting) {
        setting.get().then(async val => {
						for (const [unit, div] of Object.entries(mult_map)) {
								if (Number.parseInt(val) % div == 0) {
										amount = unit;
										val /= div;
										val = val.toString()
										break;
								}
						}
            last_saved_value=val;
            value=val; 
						if (disabled_func) {
								disabled = await setting[disabled_func]();
						}
            loading = false
        })
    };
    $: load(setting);

		const mult_map = {
				"Weeks": 60 * 24 * 7,
				"Days": 60 * 24,
				"Hours": 60,
				"Minutes": 1,
		}

    function save() {
        if (value && last_saved_value !== null && last_saved_value != value) {
            last_saved_value = value;
            loading = true;
            setting.set(value * mult_map[amount]).then(() => loading = false);
        }
    }
</script>

<div style="display: flex; align-items: center; gap: 5px">
		<Input placeholder={amount} bind:value {...input} on:submit_intent={save} {disabled}/>
		<Select bind:value={amount}>
				<option value="Minutes">Minutes</option>
				<option value="Hours">Hours</option>
				<option value="Days">Days</option>
				<option value="Weeks">Weeks</option>
		</Select>
</div>


{#if loading}
    <Loader/>
{/if}
