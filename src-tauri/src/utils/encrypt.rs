use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Key,
};
use anyhow::Result;
use base64::{engine::general_purpose::STANDARD, Engine};
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::path::PathBuf;
use std::{env, fs};
use std::error::Error;
use std::ops::Add;

const NONCE_LENGTH: usize = 12;
pub static PPHOME_PATH: &str = "/root/p/pphome";
pub static PPHOME_PATH_ENV_KEY: &str = "p_dir";

fn pphome_home_dir() -> Result<PathBuf> {
    // 读取环境变量中的pphome路径
    if let Ok(val) = env::var(PPHOME_PATH_ENV_KEY) {
        let path = PathBuf::from(val.add("/pphome"));
        if path.exists() {
            return Ok(path);
        }
    }
    // 读取默认路径
    let path = PathBuf::from(PPHOME_PATH);
    if path.exists() {
        return Ok(path);
    }
    Err(anyhow::anyhow!("Failed to get the pphome directory"))
}
pub fn get_encryption_key() -> Result<Vec<u8>> {
    let app_dir = pphome_home_dir()?;
    let key_path = app_dir.join(".encryption_key");

    if !key_path.exists() {
        // Generate and save new key
        let mut key = vec![0u8; 32];
        getrandom::getrandom(&mut key).map_err(|e| anyhow::anyhow!("Failed to getrandom: {}", e))?;

        // Ensure directory exists
        if let Some(parent) = key_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| anyhow::anyhow!("Failed to create key directory: {}", e))?;
        }
        // Save key
        fs::write(&key_path, &key)
            .map_err(|e| anyhow::anyhow!("Failed to save encryption key: {}", e))?;
        return Ok(key);
    }
    // Read existing key
    fs::read(&key_path).map_err(|e| anyhow::anyhow!("Failed to read encryption key: {}", e))
}


/// Encrypt data
pub fn encrypt_data(data: &str) -> Result<String, Box<dyn Error>> {
    let encryption_key = get_encryption_key()?;
    let key = Key::<Aes256Gcm>::from_slice(&encryption_key);
    let cipher = Aes256Gcm::new(key);

    // Generate random nonce
    let mut nonce = vec![0u8; NONCE_LENGTH];
    getrandom::getrandom(&mut nonce).map_err(|e| anyhow::anyhow!("Failed to getrandom: {}", e))?;

    // Encrypt data
    let ciphertext = cipher
        .encrypt(nonce.as_slice().into(), data.as_bytes())
        .map_err(|e| format!("Encryption failed: {}", e))?;

    // Concatenate nonce and ciphertext and encode them in base64
    let mut combined = nonce;
    combined.extend(ciphertext);
    Ok(STANDARD.encode(combined))
}

/// Decrypt data
pub fn decrypt_data(encrypted: &str) -> Result<String, Box<dyn Error>> {
    let encryption_key = get_encryption_key()?;
    let key = Key::<Aes256Gcm>::from_slice(&encryption_key);
    let cipher = Aes256Gcm::new(key);
    // Decode from base64
    let data = STANDARD.decode(encrypted)?;
    if data.len() < NONCE_LENGTH {
        return Err("Invalid encrypted data".into());
    }

    // Separate nonce and ciphertext
    let (nonce, ciphertext) = data.split_at(NONCE_LENGTH);

    // Decrypt data
    let plaintext = cipher
        .decrypt(nonce.into(), ciphertext)
        .map_err(|e| format!("Decryption failed: {}", e))?;

    String::from_utf8(plaintext).map_err(|e| e.into())
}

/// Serialize encrypted function
pub fn serialize_encrypted<T, S>(value: &T, serializer: S) -> Result<S::Ok, S::Error>
where
    T: Serialize,
    S: Serializer,
{
    // 如果序列化失败，返回 None
    let json = match serde_json::to_string(value) {
        Ok(j) => j,
        Err(_) => return serializer.serialize_none(),
    };

    // 如果加密失败，返回 None
    match encrypt_data(&json) {
        Ok(encrypted) => serializer.serialize_str(&encrypted),
        Err(_) => serializer.serialize_none(),
    }
}

/// Deserialize decrypted function
pub fn deserialize_encrypted<'a, T, D>(deserializer: D) -> Result<T, D::Error>
where
    T: for<'de> Deserialize<'de> + Default,
    D: Deserializer<'a>,
{
    // 如果反序列化字符串失败，返回默认值
    let encrypted = match String::deserialize(deserializer) {
        Ok(s) => s,
        Err(_) => return Ok(T::default()),
    };

    // 如果解密失败，返回默认值
    let decrypted_string = match decrypt_data(&encrypted) {
        Ok(data) => data,
        Err(_) => return Ok(T::default()),
    };
    // 如果 JSON 解析失败，返回默认值
    match serde_json::from_str(&decrypted_string) {
        Ok(value) => Ok(value),
        Err(_) => Ok(T::default()),
    }
}
