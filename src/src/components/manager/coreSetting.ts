import {Writable, writable} from "svelte/store";
import {get, patch} from "../../snippets/fetch";
import {SettingType} from "./settingType";

export default class CoreSetting extends SettingType<string|boolean> {
		store: Writable<string|null|boolean>;
		constructor(readonly data: {"poisson.core_setting.key": string}) {
				super();
				this.store = writable(null);
		}
		async get(options: any): Promise<string|boolean> {
				let val: string|boolean = (await get<{value: string}>(`/auth/api/manager/core_setting/${this.data["poisson.core_setting.key"]}`)).value;
				if (options && options.boolean) {
						val = (val === "true");
				}
				this.store.set(val);
				return val;
		}
		async set(value: string): Promise<void> {
				if (typeof value === "boolean") {
						value = value ? "true" : "false";
				}
				await patch(`/auth/api/manager/core_setting/${this.data["poisson.core_setting.key"]}`, {value});
				this.store.set(value);
		}

		get_store() {
				return this.store;
		}

}
