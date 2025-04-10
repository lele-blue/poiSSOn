<script>
    import Button from "@components/Button.svelte"

    export let title;
    export let text;
    export let is_html = false;

    export let closeDialog;

</script>

<svelte:body on:keydown|capture={event => {if (event.code == "Enter") closeDialog()}}/>

<h1>{title}</h1>
<p>{#if is_html}{@html text}{:else}{text}{/if}</p>

<Button icon="check" on:click={closeDialog} dialogButton={true}>OK</Button>
