<script>
    import Button from "@components/Button.svelte"
    import LoadButton from "@components/LoadButton.svelte"

    export let title;
    export let text;
    export let onConfirm;
    export let onDecline = () => {};
    export let is_html = false;
    export let confirm_icon = "check";
    export let confirm_text = "OK";

    export let closeDialog;
    
    let selected = null;

</script>

<style>
    .buttons {
        display: flex;
        gap: 5px;
    }
</style>

<svelte:body on:keydown|capture={event => {if (event.code == "Enter") {onDecline(); closeDialog()}}}/>

<h1>{title}</h1>
<p>{#if is_html}{@html text}{:else}{text}{/if}</p>

<div class="buttons">
    <LoadButton icon="close" on:clicked={async event => {selected=false; await event.detail.waitUntil(onDecline()); closeDialog()}} dialogButton={true} disabled={selected===true}>Decline</LoadButton>
    <LoadButton icon={confirm_icon} on:clicked={async event => {selected=true; await event.detail.waitUntil(onConfirm()); closeDialog()}} dialogButton={true} disabled={selected===false}>{confirm_text}</LoadButton>
</div>
