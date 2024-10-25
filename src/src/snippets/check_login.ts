import {currentUser} from "../state/currentUser";

export async function check_login() {
    const res = await fetch("/auth/api/alt_ping");
    if (res.status !== 200) {
        location.href = "/auth";
    }
    currentUser.set(await res.text())
}

