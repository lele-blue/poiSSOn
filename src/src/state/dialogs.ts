import {writable} from "svelte/store";

export let dialogs = writable<{"component": SvelteComponentDev, "data": any}[]>([]);

export function showDialog(component: SvelteComponentDev, data: any) {
	dialogs.update(prev => [...prev, {component, data}]);
}

