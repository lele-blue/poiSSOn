export abstract class SettingType<T> {
	abstract get(): Promise<T>;
	abstract set(data: T): Promise<void>;
}
