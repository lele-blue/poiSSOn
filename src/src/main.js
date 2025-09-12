import App from './App.svelte'

function createElementFromHTML(htmlString) {
  var div = document.createElement('div');
  div.innerHTML = htmlString.trim();
    return Array.from(div.childNodes).filter(elem => {
        if (elem.tagName === "SCRIPT") {
            eval(elem.innerText);
            return false;
        }
        return true;
    });
}

if (import.meta.env.DEV) {
    fetch("/auth/debug/dev_inlay").then(resp => resp.text().then(text => {

        createElementFromHTML(text).forEach(el => document.body.appendChild(el))
    new App({
        target: document.body,
        hydrate: false,
    })
    }));
} else {

    new App({
        target: document.body,
        hydrate: false,
    })

}
