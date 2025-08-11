import App from './App.svelte'

function createElementFromHTML(htmlString) {
  var div = document.createElement('div');
  div.innerHTML = htmlString.trim();

  // Change this to div.childNodes to support multiple top-level nodes.
  return div.firstChild;
}

if (import.meta.env.DEV) {
    fetch("/auth/debug/dev_inlay").then(resp => resp.text().then(text => document.body.appendChild(createElementFromHTML(text))))
}

new App({
    target: document.body,
    hydrate: false,
})

