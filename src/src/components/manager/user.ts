import {get as http_get, post} from "../../snippets/fetch";
import {contextStore} from "../../state/globalContextStore";
import {UserManagerBase} from "./user_common";
import ShareBox from "@components/ShareBox.svelte"
import {showDialog} from "../../state/dialogs"
import {currentUser} from "../../state/currentUser";
import {get} from "svelte/store";

export type user = {username: string, email: string, uid: string, full_name: string}

export default class UserManager extends UserManagerBase<user> {
	id: string;
	user: user;

	constructor(readonly data: {}, readonly extra: string[]) {
		super();
		this.id = extra[0];
	}

	async context_group_init() {
		 this.user = await http_get<user>(`/auth/api/manager/users/${this.id}`)
		 contextStore.update(val => {return {...val, user_title: `Edit ${this.user.username}`}})
	}

	async get(options: {key: string}, add_params?: Record<string, any>): Promise<user> {
		return this.user[options.key]
	}
	async set(data: user[]): Promise<void> {

	}

	async create_password_link(): Promise<void> {
		if (!this.user) await this.context_group_init()
		showDialog(ShareBox, {
			title: `Password reset link for ${this.user.username}`,
			text: `Share this link with ${this.user.username} so they can set their password`,
			link: (await post<{link: string}>("/auth/api/manager/login_links", {
				user: get(currentUser)!.uid,
				purpose: "poisson.loginlink.purpose.password_reset",
			})).link,
		});
	}

	async warn_email_direct(email: string) {
		if (email?.length == 0) {
			return "User has no email!"
		}
	}
}
