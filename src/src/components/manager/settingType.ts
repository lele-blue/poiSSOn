export abstract class SettingType<T> {
	abstract get(options?:{sort: {key: string, dir: "asc"|"desc"}}): Promise<T>;
	abstract set(data: T): Promise<void>;
}
