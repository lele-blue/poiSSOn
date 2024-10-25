import {writable} from "svelte/store";

export let currentUser = writable<string|null>(null)
