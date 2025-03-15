<script>

    import LoadButton from "../../../components/LoadButton.svelte";
    import {goto} from "@roxi/routify";
    import DefaultFrame from "../../../components/DefaultFrame.svelte";

</script>


<DefaultFrame>

    <h1>Not Allowed</h1>

    <p>Your account lacks permission to access this</p>
    <div style="width: 80%">
        <LoadButton vertical={true} on:clicked={() => $goto('/auth/go/dash')} icon="arrow-right">To overview</LoadButton>
    </div>
</DefaultFrame>
