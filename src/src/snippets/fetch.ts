import {handle_400} from "./handle_2fa_400";
import {csrftoken} from "./csrf";

export async function do_fetch(url: string, options?: RequestInit) {
    const resp = await fetch(url, options);
    const json = await resp.json();
    if (resp.status >= 400 || resp.status < 500) {
        handle_400(json, (url, parms) => location.href=`${url}?${new URLSearchParams(parms)}`);
    }
    return json;
}

export async function get<T>(url: string) {
    return await do_fetch(url) as T;
}


function build_request(body: any) {
    return {
    
        headers: {
            "X-CSRFToken": csrftoken(),
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body),
    }
}


export async function patch<T>(url: string, body: any) {
    return await do_fetch(url, {
        method: "PATCH", 
        ...build_request(body),
    }) as T;
}
export async function post<T>(url: string, body: any) {
    return await do_fetch(url, {
        method: "POST", 
        ...build_request(body),
    }) as T;
}
