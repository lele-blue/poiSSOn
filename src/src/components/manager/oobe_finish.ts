import {patch} from "../../snippets/fetch";

export default class OOBEFinish {

		constructor(readonly data: {}, readonly extra: string[]) {
		}

		async get(options: {key: string}, add_params?: Record<string, any>): Promise<void> {
		}
		async set(data: string, options: {key: string}): Promise<void> {
		}

		async finish() {
				await patch(`/auth/api/manager/core_setting/poisson.core.oobe.state`, {value: "poisson.oobe.finished"});
				location.href = "/auth/go/manager"
				return false;
		}
}
