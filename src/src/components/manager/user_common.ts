import ConfirmBox from "@components/ConfirmBox.svelte"
import {SettingType} from "./settingType";
import {tick} from "svelte";
import {currentUser} from "../../state/currentUser";
import {showDialog} from "../../state/dialogs"
import {del} from "../../snippets/fetch"

export type user = {username: string, email: string, uid: string, full_name: string}

export abstract class UserManagerBase<T> extends SettingType<T> {
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
										await del(`/auth/api/manager/users/${user.uid}`, {});
										resolve();
										this.reload();
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
