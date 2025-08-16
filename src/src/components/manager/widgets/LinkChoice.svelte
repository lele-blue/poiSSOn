<script>
    import LoadButton from "@components/LoadButton.svelte"
    import {goto} from "@roxi/routify"

    export let choices = [];
    export let setting;

    export const value = "";
    let last_saved_value;
    async function redir(path, params, call, mode){
        if (call) {
						if (await setting[call]() === false) {
								console.log("Rej")
								return
						}
						console.log("acc")
        }
				if (path) {
						for (const [key, val] of Object.entries(params)) {
								if (Array.isArray(val)) {
										params[key] = await Promise.all(val.map(elem => elem === "$val"?setting.get():Promise.resolve(elem)))
								}
						}
						$goto(path, params, {mode: mode ?? "push"});
				}
    }
</script>

{#each choices as {text, icon, path, params, call, mode}}
    <LoadButton on:clicked={event => event.detail.waitUntil(redir(path, params, call, mode))} {icon}>{text}</LoadButton>
{/each}
