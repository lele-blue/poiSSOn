import {Writable, writable} from "svelte/store";
import {get, patch} from "../../snippets/fetch";
import {SettingType} from "./settingType";

export default class CoreSetting extends SettingType<string> {
	store: Writable<string|null>;
	constructor(readonly data: {"poisson.core_setting.key": string}) {
		super();
		this.store = writable(null);
	}
	async get(): Promise<string> {
		const val = (await get<{value: string}>(`/auth/api/manager/core_setting/${this.data["poisson.core_setting.key"]}`)).value;
		this.store.set(val);
		return val;
	}
	async set(value: string): Promise<void> {
		await patch(`/auth/api/manager/core_setting/${this.data["poisson.core_setting.key"]}`, {value});
		this.store.set(value);
	}

	get_store() {
			return this.store;
	}
	
}
