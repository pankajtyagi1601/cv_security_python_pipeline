# enrollment/enrollment_pending_recover.py

from utils.logger import logger

from storage.database import db
from enrollment.enrollment_processor import process_enrollment

def recover_pending_enrollments():
    """Process any jobs that were pending when Python last crashed"""

    pending = list(db["enrollment_jobs"].find({"status": "pending"}))

    if not pending:
        return

    logger.info(f"[Recovery] Found {len(pending)} unprocessed enrollment(s) — processing now...")

    for job in pending:
        name      = job["name"]
        image_url = job["image_url"]
        success, msg = process_enrollment(name, image_url)

        if success:
            db["enrollment_jobs"].update_one(
                {"_id": job["_id"]},
                {"$set": {"status": "completed"}}
            )
            logger.info(f"[Recovery] Completed: {msg}")
        else:
            db["enrollment_jobs"].update_one(
                {"_id": job["_id"]},
                {"$set": {"status": "failed", "error": msg}}
            )
            logger.error(f"[Recovery] Failed: {msg}")
