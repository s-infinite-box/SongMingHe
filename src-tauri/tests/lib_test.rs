/// 集成测试目录 与src同级
use song_vue_tauri_lib;
use song_vue_tauri_lib::utils::encrypt;


#[test]
fn get_encryption_key() {
    let encryption_key = encrypt::get_encryption_key();
    assert!(encryption_key.is_ok());
    log::info!("{:?}", encryption_key)
}

// 测试加密
#[test]
fn encrypt_data() {
    let data = "hello world";
    let encrypted = encrypt::encrypt_data(data);
    assert!(encrypted.is_ok());
    log::info!("{:?}", encrypted)
}

// 测试解密
#[test]
fn decrypt_data() {
    let data = "hello world";
    let encrypted = encrypt::encrypt_data(data);
    assert!(encrypted.is_ok());
    let encrypted = encrypted.unwrap();
    println!("Encrypted data: {:?}", encrypted);
    let decrypted = encrypt::decrypt_data(&encrypted);
    assert!(decrypted.is_ok());
    println!("Decrypted data: {:?}", decrypted.unwrap());
}

