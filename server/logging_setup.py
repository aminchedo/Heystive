import os, json, logging, sys
from logging.handlers import RotatingFileHandler
LOG_DIR = os.environ.get("LOG_DIR", ".logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {"level": record.levelname, "name": record.name, "message": record.getMessage()}
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)
logger = logging.getLogger("heystive")
logger.setLevel(logging.INFO)
stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(JsonFormatter())
fileh = RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=3, encoding="utf-8")
fileh.setFormatter(JsonFormatter())
logger.handlers.clear()
logger.addHandler(stream)
logger.addHandler(fileh)
def get_logger():
    return logger