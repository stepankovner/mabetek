"""Durable at-least-once email outbox. Run with python -m app.notifications."""
import logging
import smtplib
import ssl
import time
from email.message import EmailMessage
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from .config import Settings
from .models import Lead, Notification

logger = logging.getLogger(__name__)

def smtp_send(settings, lead):
    if not all([settings.smtp_host, settings.smtp_from, settings.notification_to]):
        raise RuntimeError("SMTP not configured")
    message = EmailMessage()
    message["Subject"] = f"Мабетэк: новая заявка {lead.id}"
    message["From"] = settings.smtp_from
    message["To"] = settings.notification_to
    message["Message-ID"] = f"<{lead.id}@mabetek-notifications>"
    # Plain text only; no contact data is interpolated into mail headers.
    message.set_content(f"Направление: {lead.service}\nИмя: {lead.name}\nКонтакт: {lead.contact}\n\n{lead.message}")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_starttls:
            smtp.starttls(context=ssl.create_default_context())
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)

def deliver_pending(sessions, settings, send_email=smtp_send):
    # A row lock is held through delivery so concurrent workers do not send the same job.
    # A crash after SMTP acceptance may still duplicate delivery: stable Message-ID helps tracing.
    with sessions.begin() as db:
        jobs = db.scalars(select(Notification).where(Notification.sent_at.is_(None),
            Notification.next_attempt_at <= time.time()).order_by(Notification.id)
            .limit(10).with_for_update(skip_locked=True)).all()
        for job in jobs:
            lead = db.get(Lead, job.lead_id)
            if lead is None:
                db.delete(job)
                continue
            job.attempts += 1
            try:
                send_email(settings, lead)
            except Exception as error:
                # Never persist credentials, recipient details, or full SMTP response text.
                job.last_error = type(error).__name__
                job.next_attempt_at = time.time() + min(3600, 30 * 2 ** min(job.attempts, 7))
                logger.warning("Notification %s failed (%s)", job.id, job.last_error)
            else:
                job.sent_at = time.time()
                job.last_error = ""

def main():
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    sessions = sessionmaker(create_engine(settings.database_url, pool_pre_ping=True))
    while True:
        try:
            deliver_pending(sessions, settings)
        except Exception:
            logger.error("Notification worker cycle failed")
        time.sleep(10)

if __name__ == "__main__":
    main()
