<script>
		import DefaultFrame from "../../../../components/DefaultFrame.svelte"
		import Loader from "../../../../components/Loader.svelte"
		import LoadButton from "../../../../components/LoadButton.svelte"
		import Input from "../../../../components/Input.svelte"
		import Select from "../../../../components/Select.svelte"
		import {csrftoken} from "../../../../snippets/csrf.ts"
    import {goto} from "@roxi/routify";

		export let service_name;


    let pw = "";


    async function set() {
        const resp = await fetch("/auth/api/application_password/" + service_name, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken(),
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"password": pw})
        });
        if (resp.status !== 200) {
            throw new Error("PW set failed");
        }
        $goto("/auth/go/dash");
    }
</script>

<DefaultFrame>
	<h1>Set Application Password for {service_name}</h1>
  <Input bind:value={pw} password={true} placeholder="{service_name} Password" icon="key"/>
  <LoadButton disabled={pw.length < 8} on:clicked={event => event.detail.waitUntil(set())} icon="arrow-right">Set {service_name} Password</LoadButton>
</DefaultFrame>
