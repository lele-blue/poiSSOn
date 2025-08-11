import {get} from "../../snippets/fetch";
import {UserManagerBase} from "./user_common";

export type user = {username: string, email: string, uid: string, full_name: string}

export default class UserManager extends UserManagerBase<user[]> {
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

	get_uid(user: user) {
		return user.uid;
	}
}
