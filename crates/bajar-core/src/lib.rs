//! Bajar Core experimental ledger primitives.
//! NOT a consensus implementation or production cryptocurrency.
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

pub const BAJAR_DECIMALS: u32 = 9;
pub const GENESIS_SUPPLY: u128 = 13_000_000_000u128 * 10u128.pow(BAJAR_DECIMALS);

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct Transfer {
    pub from: [u8; 32],
    pub to: [u8; 32],
    pub amount: u128,
    pub nonce: u64,
    pub chain_id: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SignedTransfer {
    pub transfer: Transfer,
    pub signature: [u8; 64],
}

impl Transfer {
    pub fn signing_bytes(&self) -> Vec<u8> {
        let mut bytes = b"BAJAR_TRANSFER_V1".to_vec();
        bytes.extend(bincode::serialize(self).expect("transfer serialization"));
        bytes
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Account {
    pub balance: u128,
    pub nonce: u64,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Ledger {
    pub accounts: BTreeMap<[u8; 32], Account>,
}

#[derive(Debug, PartialEq, Eq)]
pub enum TransferError {
    InvalidSignature,
    WrongChain,
    InvalidNonce,
    InsufficientBalance,
    Overflow,
    ZeroAmount,
}

impl Ledger {
    pub fn genesis(treasury: [u8; 32]) -> Self {
        let mut ledger = Self::default();
        ledger.accounts.insert(treasury, Account { balance: GENESIS_SUPPLY, nonce: 0 });
        ledger
    }

    pub fn apply(&mut self, signed: &SignedTransfer, chain_id: &str) -> Result<(), TransferError> {
        let tx = &signed.transfer;
        if tx.chain_id != chain_id { return Err(TransferError::WrongChain); }
        if tx.amount == 0 { return Err(TransferError::ZeroAmount); }
        let key = VerifyingKey::from_bytes(&tx.from).map_err(|_| TransferError::InvalidSignature)?;
        let signature = Signature::from_bytes(&signed.signature);
        key.verify(&tx.signing_bytes(), &signature).map_err(|_| TransferError::InvalidSignature)?;
        let sender = self.accounts.get(&tx.from).cloned().unwrap_or_default();
        if tx.nonce != sender.nonce { return Err(TransferError::InvalidNonce); }
        if sender.balance < tx.amount { return Err(TransferError::InsufficientBalance); }
        let receiver = self.accounts.get(&tx.to).cloned().unwrap_or_default();
        if tx.from == tx.to {
            let account = self.accounts.get_mut(&tx.from).expect("sender funded");
            account.nonce = account.nonce.checked_add(1).ok_or(TransferError::Overflow)?;
            return Ok(());
        }
        let new_receiver_balance = receiver.balance.checked_add(tx.amount).ok_or(TransferError::Overflow)?;
        let new_nonce = sender.nonce.checked_add(1).ok_or(TransferError::Overflow)?;
        self.accounts.insert(tx.from, Account { balance: sender.balance - tx.amount, nonce: new_nonce });
        self.accounts.insert(tx.to, Account { balance: new_receiver_balance, nonce: receiver.nonce });
        Ok(())
    }

    pub fn state_hash(&self) -> [u8; 32] {
        Sha256::digest(bincode::serialize(&self.accounts).expect("state serialization")).into()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ed25519_dalek::{Signer, SigningKey};

    #[test]
    fn genesis_supply_is_fixed() {
        let ledger = Ledger::genesis([7; 32]);
        assert_eq!(BAJAR_DECIMALS, 9);
        assert_eq!(GENESIS_SUPPLY, 13_000_000_000_000_000_000u128);
        assert_eq!(ledger.accounts[&[7; 32]].balance, GENESIS_SUPPLY);
    }

    #[test]
    fn signed_transfer_and_replay_rejection() {
        let key = SigningKey::from_bytes(&[9; 32]);
        let from = key.verifying_key().to_bytes();
        let mut ledger = Ledger::genesis(from);
        let transfer = Transfer { from, to: [8; 32], amount: 42, nonce: 0, chain_id: "bajar-devnet-1".into() };
        let signature = key.sign(&transfer.signing_bytes()).to_bytes();
        let signed = SignedTransfer { transfer, signature };
        ledger.apply(&signed, "bajar-devnet-1").unwrap();
        assert_eq!(ledger.accounts[&[8; 32]].balance, 42);
        assert_eq!(ledger.apply(&signed, "bajar-devnet-1"), Err(TransferError::InvalidNonce));
    }

    #[test]
    fn reject_wrong_chain() {
        let key = SigningKey::from_bytes(&[4; 32]);
        let from = key.verifying_key().to_bytes();
        let mut ledger = Ledger::genesis(from);
        let transfer = Transfer { from, to: [5; 32], amount: 1, nonce: 0, chain_id: "other".into() };
        let signed = SignedTransfer { signature: key.sign(&transfer.signing_bytes()).to_bytes(), transfer };
        assert_eq!(ledger.apply(&signed, "bajar-devnet-1"), Err(TransferError::WrongChain));
    }
}
