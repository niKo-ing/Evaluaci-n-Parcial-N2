from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db.database import get_db, engine, Base, setup_worm_mode
from .db.models import TransactionDB
from .db.worm import apply_postgres_worm
from .api.schemas import TransactionCreate, TransactionResponse
from .core.security import DataEncryptor, IntegrityManager
from .logger import log_audit
import datetime
import time
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import text

app = FastAPI(title="SATI - Sistema de Auditoria de Transacciones Inmutables")

def init_db():
    retries = 10
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            setup_worm_mode()
            apply_postgres_worm(engine)
            log_audit("Base de datos conectada exitosamente.")
            break
        except OperationalError:
            retries -= 1
            log_audit(f"Esperando a la base de datos... ({retries} intentos restantes)", level="WARNING")
            time.sleep(3)

encryptor = DataEncryptor()
integrity = IntegrityManager()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "SATI API is running. Fintech Audit System Active."}

@app.get("/health")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "OK", "database": "UP"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    try:
        total = db.query(TransactionDB).count()
        last = db.query(TransactionDB).order_by(TransactionDB.id.desc()).first()
        last_ts = last.timestamp.isoformat() if last else None
        return {
            "total_transactions": total,
            "last_ingest_timestamp": last_ts,
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.post("/ingest", response_model=TransactionResponse)
def ingest_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:
        log_audit(f"Recibida transaccion {transaction.id}")
        merchant_masked = integrity.mask_merchant_id(transaction.comercio_id)
        amount_enc = encryptor.encrypt_amount(transaction.monto)
        timestamp_iso = transaction.timestamp if transaction.timestamp else datetime.datetime.utcnow()

        last_record = db.query(TransactionDB).order_by(TransactionDB.id.desc()).first()
        prev_hash = last_record.current_hash if last_record else "0" * 64

        current_hash = integrity.calculate_transaction_hash(
            transaction_id=transaction.id,
            amount_encrypted=amount_enc,
            currency=transaction.moneda,
            merchant_id_masked=merchant_masked,
            timestamp_iso=timestamp_iso.isoformat(),
            previous_hash=prev_hash
        )

        db_transaction = TransactionDB(
            transaction_id=transaction.id,
            amount_encrypted=amount_enc,
            currency=transaction.moneda,
            merchant_id_masked=merchant_masked,
            timestamp=timestamp_iso,
            current_hash=current_hash,
            previous_hash=prev_hash
        )
        
        db.add(db_transaction)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            log_audit(f"Transaccion duplicada rechazada: {transaction.id}", level="WARNING")
            raise HTTPException(status_code=409, detail="Transaccion ya existe")
        except OperationalError:
            db.rollback()
            log_audit(f"DB no disponible al procesar: {transaction.id}", level="ERROR")
            raise HTTPException(status_code=503, detail="Database unavailable")

        db.refresh(db_transaction)

        log_audit(f"Transaccion {transaction.id} procesada exitosamente con hash {current_hash[:10]}...")

        return {
            "transaction_id": transaction.id,
            "status": "SUCCESS",
            "message": "Transaccion registrada e inmutable",
            "timestamp": timestamp_iso.isoformat(),
            "audit_hash": current_hash
        }
    except ValueError as ve:
        db.rollback()
        error_msg = f"Error de validacion en transaccion {transaction.id}: {str(ve)}"
        log_audit(error_msg, level="ERROR")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_msg = f"Error procesando transaccion {transaction.id}: {str(e)}"
        log_audit(error_msg, level="ERROR")
        raise HTTPException(status_code=500, detail="Error interno del sistema de auditoria")

@app.get("/audit/{transaction_id}")
def get_audit_trail(transaction_id: str, db: Session = Depends(get_db)):
    record = db.query(TransactionDB).filter(TransactionDB.transaction_id == transaction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Transaccion no encontrada")
    prev_record = db.query(TransactionDB).filter(TransactionDB.id < record.id).order_by(TransactionDB.id.desc()).first()
    chain_ok = True
    if prev_record:
        chain_ok = (record.previous_hash == prev_record.current_hash)

    record_ok = integrity.verify_record(record)
    integrity_status = "VERIFIED" if (record_ok and chain_ok) else "FAILED"
    return {
        "transaction_id": record.transaction_id,
        "merchant_masked": record.merchant_id_masked,
        "timestamp": record.timestamp.isoformat(),
        "current_hash": record.current_hash,
        "previous_hash": record.previous_hash,
        "integrity_status": integrity_status,
        "record_hash_ok": record_ok,
        "chain_ok": chain_ok
    }
