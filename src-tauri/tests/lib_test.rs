/// 集成测试目录 与src同级
use song_vue_tauri_lib;
use song_vue_tauri_lib::utils::encrypt;

#[test]
fn get_encryption_key() {
    let encryption_key = encrypt::get_encryption_key();
    assert!(encryption_key.is_ok());
    log::info!("{:?}", encryption_key)
}

// 测试
#[test]
fn test() {
    let data = "d9nL7iuLnzEzXtTWdhE_";
    let encrypted = encrypt::encrypt_data(data);
    assert!(encrypted.is_ok());
    let encrypted = encrypted.unwrap();
    println!("Encrypted data: {:?}", encrypted);
    let decrypted = encrypt::decrypt_data(&encrypted);
    assert!(decrypted.is_ok());
    println!("Decrypted data: {:?}", decrypted.unwrap());
}


// 测试加密
#[test]
fn encrypt_data() {
    let data = "xzmDScjheYMgk8F1NV9wJrMN7CRTaKQ6rnFg3sSZA/mzyjpn9lMVKODyQozn0ON8Arxkeo/yZO/TB6k=";
    let encrypted = encrypt::encrypt_data(data);
    assert!(encrypted.is_ok());
    let encrypted = encrypted.unwrap();
    println!("Encrypted data: {:?}", encrypted);
}


// 测试解密
#[test]
fn decrypt_data() {
    let encrypted = "6ornGx2L0oryOT5iSp09eAd0aMn5h9GN5RnkrsFpE6CpFpwPaUzjCCQEXQtN3Vf5xE6iSYnUSBjJWvp7ViC13PveGKocWAvau4mK6U1pwfxiCIoSVx7FzUzIUk+gcQsv5sSVi8wV2GxI4m6f";
    println!("Encrypted data: {:?}", encrypted);
    let decrypted = encrypt::decrypt_data(&encrypted);
    assert!(decrypted.is_ok());
    println!("Decrypted data: {:?}", decrypted.unwrap());
}
