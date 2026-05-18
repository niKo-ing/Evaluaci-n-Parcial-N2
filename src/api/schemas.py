from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
from typing import Optional
import re

class TransactionCreate(BaseModel):
    """
    Esquema de validacion para la creacion de una transaccion.
    """
    id: str = Field(..., description="ID unico de la transaccion")
    monto: float = Field(..., description="Monto de la transaccion (debe ser > 0)")
    moneda: str = Field(..., min_length=3, max_length=3, description="Codigo de moneda (ISO 4217)")
    comercio_id: str = Field(..., description="ID del comercio que origina la transaccion")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("id")
    @classmethod
    def id_valido(cls, v: str) -> str:
        value = v.strip()
        if len(value) < 3 or len(value) > 64:
            raise ValueError("El id debe tener entre 3 y 64 caracteres")
        if not re.match(r"^[A-Za-z0-9_-]+$", value):
            raise ValueError("El id solo puede contener letras, numeros, guion y guion bajo")
        return value

    @field_validator('monto')
    @classmethod
    def monto_positivo(cls, v):
        """Validacion semantica: El monto debe ser mayor a 0."""
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return v

    @field_validator("moneda")
    @classmethod
    def moneda_valida(cls, v: str) -> str:
        value = v.strip().upper()
        if not re.match(r"^[A-Z]{3}$", value):
            raise ValueError("La moneda debe ser un codigo ISO 4217 de 3 letras (ej: USD)")
        return value

    @field_validator("comercio_id")
    @classmethod
    def comercio_id_valido(cls, v: str) -> str:
        value = v.strip()
        if len(value) < 3 or len(value) > 64:
            raise ValueError("El comercio_id debe tener entre 3 y 64 caracteres")
        if not re.match(r"^[A-Za-z0-9_-]+$", value):
            raise ValueError("El comercio_id solo puede contener letras, numeros, guion y guion bajo")
        return value

    @field_validator("timestamp")
    @classmethod
    def timestamp_valido(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        now = datetime.utcnow()
        if v > now + timedelta(minutes=5):
            raise ValueError("El timestamp no puede estar en el futuro")
        return v

class TransactionResponse(BaseModel):
    """
    Esquema de respuesta para una transaccion procesada.
    """
    transaction_id: str
    status: str
    message: str
    timestamp: str
    audit_hash: str

    class Config:
        from_attributes = True
