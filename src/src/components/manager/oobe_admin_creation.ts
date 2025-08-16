import {get as http_get, post} from "../../snippets/fetch";
import {currentUser} from "../../state/currentUser";
import {get} from "svelte/store";
import {showDialog} from "../../state/dialogs";
import AlertBox from "../../components/AlertBox.svelte";
import {check_login} from "../../snippets/check_login";

export type user = {username: string, email: string, uid: string, full_name: string}

export default class AdminOOBECreator {
		id: string;
		password = "";
		username = "";
		password2 = "";

		constructor(readonly data: {}, readonly extra: string[]) {
				this.id = extra[0];
		}

		async context_group_init() {
				await check_login()
		}

		async get(options: {key: string}, add_params?: Record<string, any>): Promise<string> {
				const user = get(currentUser)
				if (user?.uid === "user_oobe") {
						return "";
				}

				return user?.[options.key]
		}
		async set(data: string, options: {key: string}): Promise<void> {
				console.log(arguments)
				if (options.key === "password") {
						this.password = data;
				}
				else if (options.key === "password2") {
						this.password2 = data;
				}
				else if (options.key === "username") {
						this.username = data;
				}
		}

		async warn_username_empty(username: string) {
				if (username.length == 1) {
						return "Username too short"
				}
				else if (username.length == 0) {
						return "This field is required"
				}
		}

		async verify_data_and_create() {
				if (get(currentUser)?.uid != "user_oobe") return true;
				let username_warn = await this.warn_username_empty(this.username);
				if (username_warn !== undefined) {
						showDialog(AlertBox, {
								"text": username_warn,
								"title": "Error in Username"
						});
						return false;
				}
				let password_warn = await this.warn_password(this.password);
				if (password_warn !== undefined) {
						showDialog(AlertBox, {
								"text": password_warn,
								"title": "Error in Password"
						});
						return false;
				}
				let password_warn2 = await this.warn_password2(this.password2);
				if (password_warn2 !== undefined) {
						showDialog(AlertBox, {
								"text": password_warn2,
								"title": "Error in Password"
						});
						return false;
				}
				try {
						const resp = await post<void>("/auth/api/oobe/create_admin_and_finish_oobe", {
								username: this.username,
								password: this.password,
						});
				} catch (e) {
						showDialog(AlertBox, {
								"title": "Security Error in OOBE",
								"text": "An Admin user has already been created. If you did not do this, reset the DB using `docker exec -it poisson-web python manage.py flush`",
						})
						setTimeout(() => {throw e}, 1);
						return false;
				}
				await check_login();
				return true
		}

		async disabled() {
				return get(currentUser)?.uid != "user_oobe";
		}

		async warn_password(password: string) {
				if (password.length == 0) return "This field is required"
				if (password.length < 8) {
						return "Password too short"
				}
				if (!password.match(/[0-9]/)) return "Password requires at least one number";
				if (!password.match(/[a-z]/)) return "Password requires at least one lowercase character";
				if (!password.match(/[A-Z]/)) return "Password requires at least one uppercase character";
				if (password.match(/^[0-9a-zA-Z]+$/)) return "Password requires at least one special character";
		}

		async warn_password2(password2: string) {
				if (password2.length == 0) return "This field is required"
						if (this.password !== password2) {
						return "Passwords do not match";
				}
		}

		async warn_user_exists() {
				if (get(currentUser)?.uid != "user_oobe") {
						return "An Admin was already created! If this is unexpected, please reset your Database"
				}
		}
}
