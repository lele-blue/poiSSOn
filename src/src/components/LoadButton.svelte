<script>
    import {createEventDispatcher} from "svelte";
    import Button from "./Button.svelte";

    const dispatch = createEventDispatcher();

    export let icon = null;
    export let icon_color = "var(--icon-col)";
    export let positive = false;
    export let destroy = false;
    export let vertical = false;
    export let passive = false;
    export let grow = false;
    export let margin = false;
    export let noNewLine = false;
    export let smallLink = false;
    let loading = false;
    export let label = null;

    function click() {
        if (loading) return;
        dispatch('clicked', {waitUntil: s => {
            loading = true;
            s.then(() => {
                loading = false
            }).catch(e => {
                loading = false;
                icon = "alert";
                icon_color = 'red';
                setTimeout(() => {
                    //#!debug
                    throw e;
                }, 10)
            }
            )
        }})
    }
</script>

<Button on:click={click} smallLink={smallLink} icon={icon} icon_color={icon_color} positive={positive} destroy={destroy} vertical={vertical} passive={passive} grow={grow} margin={margin} noNewLine={noNewLine} loading={loading} label={label}>
    <slot/>
</Button>