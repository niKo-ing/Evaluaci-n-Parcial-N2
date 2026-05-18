import hashlib
import json
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()

class DataEncryptor:
    """
    Clase encargada de cifrar y descifrar montos de transacciones.
    Utiliza AES-256 a traves de la libreria cryptography (Fernet).
    """
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY no configurada")
        try:
            self.cipher_suite = Fernet(key.encode())
        except Exception as e:
            raise ValueError("ENCRYPTION_KEY invalida") from e

    def encrypt_amount(self, amount: float) -> str:
        """Cifra el monto de la transaccion."""
        encrypted_data = self.cipher_suite.encrypt(str(amount).encode())
        return encrypted_data.decode()

    def decrypt_amount(self, encrypted_amount: str) -> float:
        """Descifra el monto de la transaccion."""
        decrypted_data = self.cipher_suite.decrypt(encrypted_amount.encode())
        return float(decrypted_data.decode())

class IntegrityManager:
    """
    Clase encargada de generar hashes para asegurar la inmutabilidad
    y el encadenamiento de registros (Blockchain-like).
    """
    @staticmethod
    def calculate_hash(data: dict, previous_hash: str = "0") -> str:
        """
        Calcula un hash SHA-256 de los datos del registro mas el hash anterior.
        """
        data_string = json.dumps(data, sort_keys=True)
        record_payload = f"{data_string}{previous_hash}"
        return hashlib.sha256(record_payload.encode()).hexdigest()

    @staticmethod
    def build_hash_payload(
        transaction_id: str,
        amount_encrypted: str,
        currency: str,
        merchant_id_masked: str,
        timestamp_iso: str
    ) -> dict:
        return {
            "transaction_id": transaction_id,
            "amount_encrypted": amount_encrypted,
            "currency": currency,
            "merchant_id_masked": merchant_id_masked,
            "timestamp": timestamp_iso
        }

    @staticmethod
    def calculate_transaction_hash(
        transaction_id: str,
        amount_encrypted: str,
        currency: str,
        merchant_id_masked: str,
        timestamp_iso: str,
        previous_hash: str
    ) -> str:
        payload = IntegrityManager.build_hash_payload(
            transaction_id=transaction_id,
            amount_encrypted=amount_encrypted,
            currency=currency,
            merchant_id_masked=merchant_id_masked,
            timestamp_iso=timestamp_iso
        )
        return IntegrityManager.calculate_hash(payload, previous_hash)

    @staticmethod
    def verify_record(record) -> bool:
        expected = IntegrityManager.calculate_transaction_hash(
            transaction_id=record.transaction_id,
            amount_encrypted=record.amount_encrypted,
            currency=record.currency,
            merchant_id_masked=record.merchant_id_masked,
            timestamp_iso=record.timestamp.isoformat(),
            previous_hash=record.previous_hash
        )
        return expected == record.current_hash

    @staticmethod
    def mask_merchant_id(merchant_id: str) -> str:
        """Aplica enmascaramiento al ID del comercio por privacidad."""
        if len(merchant_id) <= 4:
            return "****"
        return f"{merchant_id[:2]}****{merchant_id[-2:]}"


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-KEY")):
    expected = os.getenv("API_KEY", "sati-demo-key")
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
