import {get as http_get, post, put} from "../../snippets/fetch";
import {contextStore} from "../../state/globalContextStore";
import {UserManagerBase} from "./user_common";
import ShareBox from "@components/ShareBox.svelte"
import ConfirmBox from "@components/ConfirmBox.svelte"
import ServiceConnectionBox from "@components/ServiceConnectionBox.svelte"
import {showDialog} from "../../state/dialogs"
import {currentUser} from "../../state/currentUser";
import {get, writable, Writable} from "svelte/store";
import {goto} from "@roxi/routify"

export type user = {username: string, email: string, uid?: string, full_name: string}

export default class UserManager extends UserManagerBase<user> {
		id: string;
		user: user;
		new_password: string;
		new_password_confirm: string;
		errors: Writable<Record<string, string>>

		constructor(readonly data: {}, readonly extra: string[]) {
				super();
				this.id = extra[0];
				this.errors = writable({});
				if (this.id === "new") {
						this.user = {"username": "", "full_name": "", "email": "", "uid": "new"}
				}
		}

		async context_group_init() {
				if (this.id === "new") {
						contextStore.update(val => {return {...val, user_title: `Create new User`}})
				} else {
						this.user = await http_get<user>(`/auth/api/manager/users/${this.id}`)
						contextStore.update(val => {return {...val, user_title: `Edit ${this.user.username}`}})
				}
		}

		async get_available_services() {
				return await http_get("/api/manager/services");
		}

		async get_user_service_uids() {
				return await http_get(`/api/manager/users/${this.user.uid}/service_connections`)
		}

		async set_user_service_connections(services: string[]) {
				return await post(`/api/manager/users/${this.user.uid}/set_service_connections`, {services})
		}

		async get(options: {key: string}, add_params?: Record<string, any>): Promise<user> {
				return this.user[options.key]
		}
		async set(data: string, options: {key: string}): Promise<void> {
				if (options.key === "password") this.new_password = data;
				if (options.key === "password_confirm") this.new_password_confirm = data;
				if (options.key === "is_superuser" && data) await new Promise<void>((res, rej) => showDialog(ConfirmBox, {
						title: "Warning",
						text: "This will grant ALL rights, are you sure?",
						onConfirm: async () => {res(); this.user[options.key] = data},
						onDecline: async () => rej()
				}));
				else this.user[options.key] = data;
		}

		async open_service_connection_wizard() {
				showDialog(ServiceConnectionBox, {
						title: `Services for user ${this.user.username}`,
						text: "",
						setting: this
				})
		}

		save_error_handler(data) {
				this.errors.set(data);
				// showDialog(AlertBox, {title: "Error", text: data});
		}

		async save() {
				let resp: user;
				if (await this.is_existing_user()) {
						resp = await put<user>(`/auth/api/manager/users/${this.id}`, this.user, this.save_error_handler.bind(this));
				} else {
						this.user.uid = undefined;
						resp = await post<user>(`/auth/api/manager/users`, this.user, this.save_error_handler.bind(this));
				}
				if (resp) {
						this.user = resp;
						return true;
				}
				else throw new Error("cant create user");
		}

		async set_password() {
				if (this.new_password !== this.new_password_confirm) {
						this.errors.set({password_confirm: "Passwords do not match"})
						return;
				}
				if (await post<user>(`/api/manager/users/${this.id}/set_password`, {password: this.new_password}, this.save_error_handler.bind(this))) {
						history.pushState({}, "", new URL(location.href + "/..").href)
				}
		}

		async create_session_login_link(): Promise<void> {
				const link = await this.create_login_link(1, "poisson.loginlink.purpose.session_login");
				showDialog(ShareBox, {
						title: `Login Link for ${this.user.username}`,
						text: `Share this link with ${this.user.username}`,
						link,
				});
		}

		async create_password_link(): Promise<void> {
				const link = await this.create_login_link(1, "poisson.loginlink.purpose.password_reset");
				showDialog(ShareBox, {
						title: `Password reset link for ${this.user.username}`,
						text: `Share this link with ${this.user.username} so they can set their password`,
						link,
				});
		}


		async create_login_link(days_valid: number, purpose: "poisson.loginlink.purpose.password_reset"|"poisson.loginlink.purpose.session_login"): Promise<string> {
				if (!this.user) await this.context_group_init()
				const valid_until = new Date();
				valid_until.setTime(valid_until.getTime() + days_valid * 24 * 60 * 60 * 1000);
				return (await post<{link: string}>("/auth/api/manager/login_links", {
						user: this.user.uid,
						purpose,
						valid_until,
				})).link
		}

		async warn_email_direct(email: string) {
				if (email?.length == 0) {
						return "User has no email!";
				}
		}

		async is_existing_user() {
				return this.id !== "new";
		}
}
