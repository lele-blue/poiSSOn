<script>
    import { Router } from '@roxi/routify'
    import { routes } from '../.routify/routes'

    

    
</script>


<Router {routes}  />

<style global>
    body {
        margin: 0;
    }

    :root {
        --material-accent-color: /*#9600f1*/ #b045f2 /*#AD88AB*/;
        --icon-secondary-col: darkslategrey;
        --material-background-important: rgba(255, 255, 255, 0.5);
        --material-error-color: red;
        color: darkslategrey;
        --icon-col: darkslategrey;
        --material-ambient-color: darkslategrey;
        --material-accent-color-light-transparent: #f6befe /*rgba(173, 136, 171, 0.5)*/;
        --material-accent-color-text: white;
        --material-accent-color-light: /*#ad9bac*/#ad00f4;
        --material-text: darkslategrey;
				--material-background-color: #fff;
    }

    .ripple {
        position: absolute;
        transform: scale(0);
        pointer-events: none;
        width: 50px;
        height: 50px;
        transition: transform 1000ms, opacity 1000ms;
        background: var(--material-accent-color-light-transparent);
        border-radius: 50%;
    }

    .material-ripple-active {
        transform: scale(2);
        opacity: 0.5;
    }
</style>
