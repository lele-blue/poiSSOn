<script>
    export let value = "";
		let checkbox;
</script>

<style>
		/**
    input {
        border: none;
        border-bottom: var(--icon-secondary-col) 2px solid;
        transition: 0.4s ease;
        background: var(--material-background-important);
        width: calc(100% - 10px - var(--left-padding));
        margin: 0;
        border-radius: 4px;
        padding: 11px 10px 4px var(--left-padding);
    }
		**/
input[role="switch"] {
  opacity: 0;
}

input[role="switch"] ~ .state {
  display: inline-block;
  user-select: none;
}

input[role="switch"] ~ .state > .container {
  position: relative;
  top: 2px;
  display: inline-block;
	border: 2px solid var(--material-accent-color-light-transparent);
  width: 42px;
  height: 22px;
  border-radius: 14px;
	transition: border-color .1s ease background .1s ease;
	background: var(--material-background-important);
}

.position {
	transition: transform .1s ease;
}

input[role="switch"] ~ .state > .container > .position {
  position: relative;
  top: 2px;
  left: 3px;
  display: inline-block;
  border-radius: 9px;
  width: 16px;
  height: 16px;
  background: black;
  opacity: 0.6;
  transform: translateX(0) translateY(0px);
}

input[role="switch"]:checked ~ .state > .container > .position {
  transform: translateX(18px) scale(120%) translateY(0px);
  background: var(--material-accent-color-text);
  opacity: 1;
}

input[role="switch"]:checked ~ .state > .container {
		border-color: var(--material-accent-color);
	  background: var(--material-accent-color);
}


</style>

<label>
		<input bind:checked={value} bind:this={checkbox} type="checkbox" role="switch"/>
		<span class="state">
				<span class="container">
						<span class="position"> </span>
				</span>
		</span>
</label>
