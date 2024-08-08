export async function check_redirect(url) {
    return (await fetch(`/auth/api/services/redirect_check?url=${encodeURIComponent(url)}`)).status === 204 || location.origin === new URL(url, location.origin).origin;
}
