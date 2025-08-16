import {handle_400} from "./handle_2fa_400";
import {csrftoken} from "./csrf";

export async function do_fetch(url: string, options?: RequestInit, error_handler?: (data: any) => void) {
    const resp = await fetch(url, options);
		if (resp.status == 204) return;
    const json = await resp.json();
    if (resp.status >= 400) {
        const error = handle_400(json, (url, parms) => location.href = `${url}?${new URLSearchParams(parms)}`);
				if (!error && error_handler) {
						error_handler(json);
						return null;
				}
				else if (error) {
            throw new Error(error)
        }
    }
    return json;
}

export async function get<T>(url: string, error_handler?: (data: any) => void) {
    return await do_fetch(url, undefined, error_handler) as T;
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


export async function del<T>(url: string, body: any, error_handler?: (data: any) => void) {
    return await do_fetch(url, {
        method: "DELETE", 
        ...build_request(body),
    }, error_handler) as T;
}

export async function patch<T>(url: string, body: any, error_handler?: (data: any) => void) {
    return await do_fetch(url, {
        method: "PATCH", 
        ...build_request(body),
    }, error_handler) as T;
}
export async function put<T>(url: string, body: any, error_handler?: (data: any) => void) {
    return await do_fetch(url, {
        method: "PUT", 
        ...build_request(body),
    }, error_handler) as T;
}
export async function post<T>(url: string, body: any, error_handler?: (data: any) => void) {
    return await do_fetch(url, {
        method: "POST", 
        ...build_request(body),
    }, error_handler) as T;
}
