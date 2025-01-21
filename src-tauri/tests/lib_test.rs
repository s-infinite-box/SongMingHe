/// 集成测试目录 与src同级
use song_vue_tauri_lib;
use ring::{rand};
use song_vue_tauri_lib::kit::aes::{decrypt_aes, encrypt_aes};

#[test]
fn encrypt_rsa() {
    let mut rng = rand::SystemRandom::new();
    let key = rng.generate(16); // 128位密钥
    let iv = rng.generate(16); // 初始向量
    let data = b"Hello, Rust!";
    let encrypted_data = encrypt_aes(data, key, iv);
    let decrypted_data = decrypt_aes(&encrypted_data, key, iv);
    println!("Original data: {:?}", data);
    println!("Encrypted data: {:?}", encrypted_data);
    println!("Decrypted data: {:?}", decrypted_data);
}

#[test]
fn test() {
    println!("test");
}
