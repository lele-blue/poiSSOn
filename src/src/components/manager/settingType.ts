export abstract class SettingType<T> {
	abstract get(options?:{sort: {key: string, dir: "asc"|"desc"}, boolean?: boolean}): Promise<T>;
	abstract set(data: T): Promise<void>;
	get_store(): Readable<T> {
		throw new Error("get_store is not supported on this type");
	}
	reload() {
		throw new Error("Can't reload directly after init");
	}
}
