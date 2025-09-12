import {showDialog} from "../state/dialogs";
import AlertBox from "@components/AlertBox.svelte";

export function handle_400(data: {action?: string, reason?: string, detail?: string}, goto: (url: string, parms: any) => void, handle_detail = true) {
		if (data.detail?.startsWith("Request was throttled")) {
				showDialog(AlertBox, {"title": "Not so fast", "text": data.detail});
		}
    if (data.detail && handle_detail) {
        return data.detail
    }
    switch (data.action) {
        case "login": {
            location.href = "/auth?next=" + encodeURIComponent(location.href)
            break;
        }
        case "upgrade": {
            goto("/auth/go/login_state_mod/otp", {next: location.href});
            break;
        }
        case "fail": {
            console.error(data.reason);
            return data.reason;
        }
				case "alert": {
						showDialog(AlertBox, {"title": "Alert", "text": data.reason});
						break;
				}
    }
    return null;
}
