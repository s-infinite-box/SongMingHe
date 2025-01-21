use ring;
use ring::aead::quic;

pub fn encrypt_aes(data: &[u8], key: &[u8], iv: &[u8]) -> Vec<u8> {
    let header_protection_key = quic::HeaderProtectionKey::new(&quic::AES_128, &key).unwrap();
    header_protection_key.algorithm().init("","")

    let key = aes::Key::from_slice(key).unwrap();
    let mut cipher = aes::Cipher::new(key, iv);
    let mut encrypted = vec![0; data.len()];
    cipher.encrypt(&mut encrypted, data).unwrap();
    encrypted
}
pub fn decrypt_aes(data: &[u8], key: &[u8], iv: &[u8]) -> Vec<u8> {
    let key = aes::Key::from_slice(key).unwrap();
    let mut cipher = aes::Cipher::new(key, iv);
    let mut decrypted = vec![0; data.len()];
    cipher.decrypt(&mut decrypted, data).unwrap();
    decrypted
}

