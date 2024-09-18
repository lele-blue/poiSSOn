import {csrftoken} from "./csrf";
// assumes redirect was already checked!!!
export async function do_redirect(url) {
    const url_obj = new URL(url, url.startsWith('/') ? location.origin : undefined);
    if (url_obj.origin !== location.origin) {
        let body = new FormData();
        body.append('for', url);
        const resp = await fetch('/auth/api/crossorigin/create_migration_token', {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken()
            },
            body
        });
        if (resp.status !== 201) throw new Error("Could not authenticate");
        const {token} = (await resp.json());
        location.href = `${url_obj.origin}/_sso?token=${token}&next=${encodeURIComponent(url)}`
    } else {
        location.href = url;
    }
}
