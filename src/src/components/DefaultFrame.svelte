
<style>
    .login_root {
        background-image: url("/auth/go/static/resolve/login_bg.jpg");
        height: 100vh;
        width: 100vw;
        background-size: cover;
    }

    .login_wrapper {
        height: 100vh;
        width: 100vw;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .login_box {
        display: flex;
        width: 500px;
        max-width: 100vw;
        padding: 10px;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(8px);
        border-radius: 3px;
        flex-direction: column;
        align-items: center;
        font-family: sans-serif;
        gap: 10px;
    }

</style>

<div class="login_root">
    <div class="login_wrapper">
        <div class="login_box">
            <slot/>
        </div>
    </div>
</div>
