<script>
    import NavBar from '../../components/Navbar/Bar.svelte'
    
</script>

<div id="app">
    <aside>
        
        <NavBar />
        
    </aside>
    <section>
        <header></header>
        <main class="container">
            
            <slot />
        </main>
        <footer></footer>
    </section>
</div>

<style>
    #app {
        display: grid;
        grid-template-columns: 196px auto;
        height: 100%;
        width: 100%;
        position: absolute;
    }
    main {
        padding-top: 64px;
    }
    aside {
        padding: 16px;
        box-shadow: 0 0 16px rgba(0, 0, 0, 0.2);
        height: 100%;
    }
</style>
