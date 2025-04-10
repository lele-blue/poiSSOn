import {writable} from "svelte/store";
import {check_login} from "../snippets/check_login";

export let currentUser = writable<string|null>(null)

check_login()
