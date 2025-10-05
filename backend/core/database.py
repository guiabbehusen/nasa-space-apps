from pymongo import MongoClient
from core.config import MONGO_URI, MONGO_DB_NAME
import logging

logger = logging.getLogger("air-api")
db = None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        logger.info("✅ MongoDB conectado: %s", db.name)
    except Exception as e:
        logger.exception("⚠️ Falha ao conectar ao MongoDB: %s", e)
else:
    logger.warning("⚠️ MongoDB não configurado - defina MONGO_URI no .env")
