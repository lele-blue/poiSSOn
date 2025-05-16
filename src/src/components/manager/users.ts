import {tick} from "svelte";
import {get, patch} from "../../snippets/fetch";
import {currentUser} from "../../state/currentUser";
import {SettingType} from "./settingType";
import {showDialog} from "../../state/dialogs"
import ConfirmBox from "@components/ConfirmBox.svelte"

export type user = {username: string, email: string, uid: string, full_name: string}

export default class UserManager extends SettingType<user[]> {
	constructor(readonly data: {}) {
		super();
	}
	async get(options?: {sort?: {key: string, dir: "asc"|"desc"}, add_params?: Record<string, any>}): Promise<user[]> {
		let params = new URLSearchParams();
		if (options?.sort) {
			params.append("sort", options.sort.key);
			params.append("dir", options.sort.dir);
		}
		for (const [name, val] of Object.entries(options?.add_params ?? {})) {
			params.append(name, val);
		}
		return (await get<user[]>(`/auth/api/manager/users?${params}`))
	}
	async set(_: user[]): Promise<void> {
		throw new Error("setting is read-only")
	}

	delete(user: user) {
		return new Promise<void>(resolve => {
			showDialog(ConfirmBox, {
				title: "Confirm User deletion", 
				text: `User ${user.username} will be deleted`, 
				confirm_icon: "delete", 
				onDecline: async () => {
					resolve();
				},
				onConfirm: async () => {
					resolve();
				},
				confirm_text: `Delete ${user.username}`,
			});
		});
	}

	can_delete(user: user) {
		return new Promise(resolve => {
			const unsub = currentUser.subscribe(async val => {
				if (val) {
					await tick();
					unsub();
					resolve(val.uid != user.uid);
				}
			})
		})
	}

	async warn_email(user: user) {
		if (user.email?.length == 0) {
			return "User has no email!"
		}
	}
	
}
