import {get} from "svelte/store";
export function handle_400(data, goto) {
    switch (data.action) {
        case "login": {
            location.href = "/auth?next=" + encodeURIComponent(location.href)
            break;
        }
        case "upgrade": {
            goto("/auth/go/login_state_mod/otp?next=" + encodeURIComponent(location.href));
            break;
        }
        case "fail": {
            console.error(data.reason);
            return data.reason;
        }
    }
    return null;
}
