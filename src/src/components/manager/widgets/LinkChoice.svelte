<script>
    import LoadButton from "@components/LoadButton.svelte"
    import {goto} from "@roxi/routify"

    export let choices = [];
    export let setting;

    export const value = "";
    let last_saved_value;
    async function redir(path, params, call, mode, path_rel){
        if (call) {
						if (await setting[call]() === false) {
								return
						}
        }
				if (path) {
						// create a copy so repeated calls get re-evaluated every time in case of a $val
						let params_copy = {};
						for (const [key, val] of Object.entries(params)) {
								if (Array.isArray(val)) {
										params_copy[key] = await Promise.all(val.map(elem => elem === "$val"?setting.get():Promise.resolve(elem)));
								} else {
										params_copy[key] = val;
								}
						}
						$goto(path, params_copy, {mode: mode ?? "push"});
				}
				if (path_rel) {
						history.pushState({}, "", new URL(location.href + "/" + path_rel).href);
				}
    }
</script>

{#each choices as {text, icon, path, params, call, mode, path_rel, submit}}
    <LoadButton {submit} on:clicked={event => event.detail.waitUntil(redir(path, params, call, mode, path_rel))} {icon}>{text}</LoadButton>
{/each}
