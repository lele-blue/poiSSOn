import {writable} from "svelte/store";

export let contextStore = writable<Record<any, any>>({})
