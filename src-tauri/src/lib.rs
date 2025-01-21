pub mod kit;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
pub fn test(){
        let public_key = r#"-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAst+KU0RBbJCAhYAR2kV9
...
-----END PUBLIC KEY-----"#;
    let private_key = r#"-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAst+KU0RBbJCAhYAR2kV9...
-----END RSA PRIVATE KEY-----"#;
    let data = b"Hello, Rust!";
    let encrypted_data = kit::encrypt_rsa(data, public_key);
    println!("{:?}", encrypted_data);
}