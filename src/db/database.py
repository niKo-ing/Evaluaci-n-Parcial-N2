from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "sati_secure_password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "sati_db")

SQLALCHEMY_DATABASE_URL = DATABASE_URL or f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_worm_configured = False

def setup_worm_mode():
    from .models import TransactionDB

    global _worm_configured
    if _worm_configured:
        return
    
    @event.listens_for(TransactionDB, 'before_update')
    def receive_before_update(mapper, connection, target):
        raise Exception("MODO WORM ACTIVO: No se permite UPDATE.")

    @event.listens_for(TransactionDB, 'before_delete')
    def receive_before_delete(mapper, connection, target):
        raise Exception("MODO WORM ACTIVO: No se permite DELETE.")

    _worm_configured = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
