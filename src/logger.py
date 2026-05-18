import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = os.getenv("LOG_FILE", "data_logs/audit_trail.log")

log_dir = os.path.dirname(LOG_FILE) or "."
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("SATI_Audit")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_audit(message: str, level: str = "INFO"):
    """
    Registra un evento en el trail de auditoría.
    """
    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
