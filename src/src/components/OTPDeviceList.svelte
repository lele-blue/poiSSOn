<script context="module">
    export function get_icon(name) {
        if (name.match(/\w+ ?[0-9]+/)) return "phone";
        if (name.match(/.*key.*/i)) return "key";
        if (["manager", "warden", "lastpass", "vault"].some(e => name.includes(e))) return "safe";
        return "numeric"

    }
</script>

<script>
    import Button from "./Button.svelte";
    import Icon from "./Icon.svelte";
    export let devices;
    import {createEventDispatcher} from "svelte"

    const dispatch = createEventDispatcher();

</script>

{#if devices.length}
    <div style="background: grey; height: 1px; width: 100%"/>
{/if}
{#each devices as device}
    <div style="--material-accent-color: #5d267f;display: flex; align-items: center;justify-content: space-between;width: 100%;">
        <slot name="main" {device}>
        <Button icon={get_icon(device.name)} on:click={ev => dispatch("selected", device)} dialogButton={true}>{device.name}</Button>
        </slot>
            <slot name="buttons" {device}>
            <Icon icon="arrow-right" color="var(--material-accent-color)"/>
            </slot>
    </div>
    <div style="background: grey; height: 1px; width: 100%"/>
{:else}
    <p>No devices added yet</p>
{/each}
