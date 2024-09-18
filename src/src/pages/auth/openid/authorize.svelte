<script>
    import DefaultFrame from "../../../components/DefaultFrame.svelte";
    import Button from "../../../components/Button.svelte";
    import Icon from "../../../components/Icon.svelte";
    import {onMount} from "svelte";

    let content;
    let scopes = [];

    onMount(() => {
        content.innerHTML = document.getElementById("content").innerHTML;
        scopes = JSON.parse(document.getElementById("scopes").innerText);
    });

    const iconmap = {
        "email": "email",
        "profile": "account",
        "sso_groups": "account-group",
    }

</script>

<DefaultFrame>
    <div bind:this={content}/>
    <div style="width: calc(100% - 10px); padding: 10px; padding-top: 0">
        {#each scopes as scope (scope.scope)}
            <div style="display: flex; flex-direction: column; ">
                <h3 style="display: flex; align-items: end; gap: 5px; margin-bottom: 5px"><Icon icon={iconmap[scope.scope]}/>{scope.name}</h3>
                <span>{scope.description}</span>
                
            </div>
        {/each}
    </div>
    <Button icon="cancel" on:click={() => document.getElementById("deny").click()}>Decline</Button>
    <Button icon="check" on:click={() => document.getElementById("accept").click()}>Accept</Button>

</DefaultFrame>

