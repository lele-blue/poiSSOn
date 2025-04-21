import {currentUser} from "../state/currentUser";

export async function check_login() {
    const res = await fetch("/auth/api/alt_ping");
    if (res.status !== 200) {
        if (location.pathname !== "/auth") location.href = "/auth";
    }
    else {
        currentUser.set(await res.json())
    }
}

