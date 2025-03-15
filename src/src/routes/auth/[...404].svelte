<script>
    import DefaultFrame from "../../components/DefaultFrame.svelte";
    import Login from "../../components/Login.svelte";
    import Button from "../../components/Button.svelte";
    import {goto} from "@roxi/routify";

</script>

<DefaultFrame>
    <h1>Not Found</h1>
    <p>PoiSSOn does not know this path</p>
    <Button on:click={() => {$goto('/auth/go/dash')}}>Open Dashboard</Button>
</DefaultFrame>
