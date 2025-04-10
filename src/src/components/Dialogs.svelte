<script>
    import {dialogs} from "@/state/dialogs";
    import {tick} from "svelte"

    let windows = {}
</script>

<style>
    .dialog_wrapper {
        position: absolute;
        display: flex;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: #00000088;
        align-items: center;
        justify-content: center;
        z-index: 100;
    }

    .dialog_inner {
        padding: 5px;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(8px);
        flex-direction: column;
        align-items: center;
        font-family: sans-serif;
        gap: 10px;
        border-radius: 3px;
    }
</style>


{#each $dialogs as dialog}
    <div class="dialog_wrapper" >
        <div class="dialog_inner" bind:this={windows[dialog]} data-workaround={tick().then(windows[dialog]?.focus())}>
            <svelte:component this={dialog.component} {...dialog.data} closeDialog={() => {dialogs.update(prev => prev.filter(elem => elem != dialog))}}/>
        </div>
    </div>
{/each}
