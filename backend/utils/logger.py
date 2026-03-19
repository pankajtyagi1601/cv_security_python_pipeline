# utils/logger.py
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Log filename includes date — one file per day
log_filename = f"logs/cv_security_{datetime.now().strftime('%Y-%m-%d')}.log"

# Single logger instance shared across the whole app
logger = logging.getLogger("cv_security")
logger.setLevel(logging.DEBUG)

# ── File handler — persists logs to disk ────────────────────
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# ── Console handler — still prints to terminal ──────────────
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # terminal shows INFO and above only

# ── Format ──────────────────────────────────────────────────
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)