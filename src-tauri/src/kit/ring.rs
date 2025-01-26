use base64::{engine::general_purpose::STANDARD_NO_PAD, Engine as _};
use ring::aead::{self, Aad, BoundKey, Nonce, OpeningKey, SealingKey, UnboundKey, AES_128_GCM};

use base64;

const AES_KEY: &str = "pphome";

struct OneNonceSequence(Option<Nonce>);

static NONCE: &[u8] = &[0; 12];

impl OneNonceSequence {
    fn new(nonce: Nonce) -> Self {
        Self(Some(nonce))
    }
}

impl aead::NonceSequence for OneNonceSequence {
    fn advance(&mut self) -> Result<aead::Nonce, ring::error::Unspecified> {
        self.0.take().ok_or(ring::error::Unspecified)
    }
}

pub(crate) fn aes_encrypt(raw: &str, key: &str) -> Result<String, String> {
    let mut secret = vec![0u8; AES_128_GCM.key_len()];
    secret[..key.len()].copy_from_slice(key.as_bytes());

    let n: Nonce = match Nonce::try_assume_unique_for_key(NONCE) {
        Ok(n) => n,
        Err(e) => {
            return Err(e.to_string());
        }
    };

    let ukey = UnboundKey::new(&AES_128_GCM, &secret)
        .map_err(|e| e.to_string())?;
    let nonce_sequence = OneNonceSequence::new(n);

    let mut s_key: SealingKey<OneNonceSequence> = SealingKey::new(ukey, nonce_sequence);

    let aes_key = &AES_KEY.as_bytes();
    let aad = Aad::from(aes_key);

    let mut in_out = raw.as_bytes().to_owned();

    let ret = s_key.seal_in_place_append_tag(aad, &mut in_out);

    match ret {
        Ok(_v) => Ok(STANDARD_NO_PAD.encode(in_out)),
        Err(e) => Err(e.to_string()),
    }
}

pub(crate) fn aes_decrypt(data: &str, key: &str) -> Result<String, String> {
    println!("aes_decrypt data: {data}, key: {key}");

    let mut in_out = match STANDARD_NO_PAD.decode(data) {
        Ok(r) => r,
        Err(e) => {
            return Err(e.to_string());
        }
    };

    let mut secret = vec![0u8; AES_128_GCM.key_len()];
    secret[..key.len()].copy_from_slice(key.as_bytes());

    let n = match Nonce::try_assume_unique_for_key(NONCE) {
        Ok(n) => n,
        Err(e) => {
            return Err(e.to_string());
        }
    };

    let ukey = UnboundKey::new(&AES_128_GCM, &secret)
        .map_err(|e| e.to_string())
        .unwrap();
    let nonce_sequence = OneNonceSequence::new(n);

    let mut o_key: OpeningKey<OneNonceSequence> = OpeningKey::new(ukey, nonce_sequence);

    let aes_key = &AES_KEY.as_bytes();
    let aad = Aad::from(aes_key);

    let ciphertext_and_tag = std::ops::RangeFrom { start: 0 };
    let ret = o_key.open_within(aad, &mut in_out, ciphertext_and_tag);
    // let ret = o_key.open_in_place(aad, &mut in_out);

    let text = match ret {
        Ok(v) => String::from_utf8_lossy(v).to_string(),
        Err(e) => {
            return Err(e.to_string());
        }
    };

    Ok(text)
}

mod test {
    use super::{aes_decrypt, aes_encrypt};

    #[test]
    fn test_encrypt_and_decrypt() {
        let raw = "abc";
        let key = "def";

        let encrypt_text = aes_encrypt(&raw, &key).unwrap();
        println!("encrypt_text: {}", encrypt_text);
        let decrypt_text = aes_decrypt(&encrypt_text, &key).unwrap();
        println!("decrypt_text: {}", decrypt_text);
        assert_eq!(decrypt_text, raw);
    }
}
