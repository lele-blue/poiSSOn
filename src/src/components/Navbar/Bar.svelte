<script>
    import Navigation from './Navigation.svelte'
    import { url } from '@roxi/routify'
    export let children
</script>

<nav>
    <a href={$url('/go')}>
        <h3>My App</h3>
    </a>
    <Navigation {children} />
</nav>
