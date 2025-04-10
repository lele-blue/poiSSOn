import {get, patch} from "../../snippets/fetch";
import {SettingType} from "./settingType";

export default class CoreSetting extends SettingType<string> {
	constructor(readonly data: {"poisson.core_setting.key": string}) {
		super();
	}
	async get(): Promise<string> {
		return (await get<{value: string}>(`/auth/api/manager/core_setting/${this.data["poisson.core_setting.key"]}`)).value
	}
	async set(value: string): Promise<void> {
		await patch(`/auth/api/manager/core_setting/${this.data["poisson.core_setting.key"]}`, {value})
	}
	
}
