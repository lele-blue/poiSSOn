export function handle_400(data: {action: string, reason: string}, goto: (url: string, parms: any) => void) {
    switch (data.action) {
        case "login": {
            location.href = "/auth?next=" + encodeURIComponent(location.href)
            break;
        }
        case "upgrade": {
            goto("/auth/go/login_state_mod/otp", {next: encodeURIComponent(location.href)});
            break;
        }
        case "fail": {
            console.error(data.reason);
            return data.reason;
        }
    }
    return null;
}
