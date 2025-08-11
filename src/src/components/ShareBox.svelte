<script>
    import Button from "@components/Button.svelte"
    import Input from "@components/Input.svelte"
    import LoadButton from "@components/LoadButton.svelte"

    export let title;
    export let text;
    export let link;
    export let is_html = false;
    export let confirm_icon = "check";
    export let confirm_text = "OK";
    export let placeholder = "Link";

    export let closeDialog;
</script>

<style>
    .buttons {
        display: flex;
        gap: 5px;
    }

    .share_row {
        display: flex;
        align-items: center;
    }
</style>

<svelte:body on:keydown|capture={event => {if (event.code == "Enter") {closeDialog()}}}/>
<h1>{title}</h1>
<p>{#if is_html}{@html text}{:else}{text}{/if}</p>


<div class="share_row">
    <Input disabled={true} value={link} {placeholder}/>
    {#if navigator.share && navigator.canShare({url: link})}
        <LoadButton icon="share" on:clicked={event => event.detail.waitUntil(navigator.share({url: link}))}/>
    {/if}
</div>

<div class="buttons">
    <LoadButton icon={confirm_icon} on:clicked={async event => {closeDialog()}} dialogButton={true}>{confirm_text}</LoadButton>
</div>
