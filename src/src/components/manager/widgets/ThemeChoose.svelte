<script>
    import Input from "@components/Input.svelte"
    import Loader from "@components/Loader.svelte"
    import Button from "@components/Button.svelte"

    export let setting;

    let loading = true;

    let themes = [
        {name: "PoiSSOn", thumbnail: "/auth/go/static/resolve/login_bg.jpg", key: "poisson.theme.default"},
        {name: "Crimson", thumbnail: "/auth/go/static/resolve/crimson.png", key: "poisson.theme.crimson"},
        {name: "Dream", thumbnail: "/auth/go/static/resolve/dream.jpg", key: "poisson.theme.dream"},
        {name: "Damp", thumbnail: "/auth/go/static/resolve/damp.jpg", key: "poisson.theme.damp"},
        {name: "Ember", thumbnail: "/auth/go/static/resolve/ember.jpg", key: "poisson.theme.ember"},
        {name: "Plain", thumbnail: "/auth/go/static/resolve/plain.jpg", key: "poisson.theme.plain"},
    ]

    export let value = "";
    let last_saved_value;
    function load(setting) {
        setting.get().then(val => {
            last_saved_value=val;
            value=val; 
            loading = false
        })
    };
    $: load(setting);
    function save() {
        if (value && last_saved_value && last_saved_value != value) {
            last_saved_value = value;
            loading = true;
            setting.set(value).then(() => location.reload());
        }
    }
</script>

<style>
 .theme-switcher {
    display: flex;
    flex-wrap: wrap;
    gap:15px;
 }

 .theme {
    display: flex;
    flex-direction: column;
    gap: 5px;
    align-items: center;
    cursor: pointer;
 }

 .theme_thumb {
    border-radius: 5px;
    border: 3px solid var(--material-background-color);
    background-image: var(--bg);
    background-size: cover;
    width: 100px;
    height: 50px;
  }

  .theme_thumb.current {
    border-color: var(--material-accent-color);
    }

  span.current {
    font-weight: bold;
  }
</style>


{#if loading}
    <Loader/>
{:else}
    <div class="theme-switcher">
        {#each themes as {name, thumbnail, key}}
            <div class="theme" on:click={() => {value = key; save()}} role="button" on:keydown={event => ["Space", "Return"].includes(event.code) && event.target.click() } tabindex=0>
                <div class="theme_thumb" class:current={value === key} style="--bg: url('{ thumbnail }')" aria-hidden="true"/>
                <span class:current={value === key}>{name}</span>
            </div>
        {/each}
    </div>
{/if}
