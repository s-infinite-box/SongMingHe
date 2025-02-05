use crate::utils::{
    encrypt,
    help,
};
use crate::{
    wrap_err
};
type CmdResult<T = ()> = Result<T, String>;

#[tauri::command]
pub fn encrypt_data(data: &str) -> CmdResult<String> {
    wrap_err!(encrypt::encrypt_data(data))
}

#[tauri::command]
pub fn decrypt_data(data: &str) -> CmdResult<String> {
    wrap_err!(encrypt::decrypt_data(data))
}
