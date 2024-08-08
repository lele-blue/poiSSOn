<!--
<style>
    .inner {
        width: calc(100% - 10px);
        height: calc(100% - 10px);
        border-radius: 50%;
        border: solid 5px var(&#45;&#45;icon-col);
        clip-path: polygon(50% 0%, 100% 0, 100% 100%, 49% 53%, 0 100%, 0 0);
        animation: loader 1s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite;
    }

    .outer {
        width: 24px;
        height: 24px;
    }
    
    @keyframes loader {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>

<div class="outer">
    <div class="inner"></div>
</div>-->

<style>
    svg {
        margin: 0 2px;
    }

    .spinner
    {
        -webkit-animation: rotation 1.35s linear infinite;
        animation: rotation 1.35s linear infinite;
    }

    @keyframes rotation
    {
        0% {
            -webkit-transform: rotate(0deg);
            transform: rotate(0deg);
        }

        100% {
            -webkit-transform: rotate(270deg);
            transform: rotate(270deg);
        }
    }

    .circle
    {
        stroke-dasharray: 180;
        stroke-dashoffset: 0;
        -webkit-transform-origin: center;
        -ms-transform-origin: center;
        transform-origin: center;
        -webkit-animation: turn 1.35s ease-in-out infinite;
        animation: turn 1.35s ease-in-out infinite;
    }

    @keyframes turn
    {
        0% {
            stroke-dashoffset: 180;
        }

        50% {
            stroke-dashoffset: 45;
            transform: rotate(135deg);
        }

        100% {
            stroke-dashoffset: 180;
            transform: rotate(450deg);
        }
    }

    svg:nth-child(1){
        stroke: var(--icon-col);
    }

</style>
<!-- Loader by https://codepen.io/gaffareljeremie/pen/owjhF -->
<div style="height: 24px; width: 24px">
    <svg class="spinner" width="24px" height="24px" viewBox="0 0 66 66" xmlns="http://www.w3.org/2000/svg">
        <circle class="circle" fill="none" stroke-width="6" stroke-linecap="round" cx="33" cy="33" r="30"></circle>
    </svg>
</div>
