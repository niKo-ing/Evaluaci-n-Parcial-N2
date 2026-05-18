from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class TransactionDB(Base):
    """
    Representacion en base de datos de una transaccion inmutable.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    amount_encrypted = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    merchant_id_masked = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    current_hash = Column(String, nullable=False)
    previous_hash = Column(String, nullable=False)
