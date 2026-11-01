import time
import uuid
from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Rental(Base):
    __tablename__ = "rentals"
    __table_args__ = (
        CheckConstraint("kind IN ('office', 'warehouse')"),
        CheckConstraint("area IS NULL OR area > 0"),
        CheckConstraint("monthly_price IS NULL OR monthly_price >= 0"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(150))
    kind: Mapped[str] = mapped_column(String(20))
    building: Mapped[str] = mapped_column(String(150), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    area: Mapped[float | None] = mapped_column(Float)
    floor: Mapped[int | None] = mapped_column(Integer)
    monthly_price: Mapped[int | None] = mapped_column(Integer)
    image_path: Mapped[str] = mapped_column(String(500), default="")
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    available: Mapped[bool] = mapped_column(Boolean, default=False)

class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (CheckConstraint("status IN ('new', 'in_progress', 'closed')"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key: Mapped[str] = mapped_column(String(36), unique=True)
    payload_hash: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(100))
    contact: Mapped[str] = mapped_column(String(254))
    service: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    privacy_version: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    status: Mapped[str] = mapped_column(String(20), default="new")
    internal_note: Mapped[str] = mapped_column(Text, default="")

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), unique=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[float] = mapped_column(Float, default=time.time, index=True)
    sent_at: Mapped[float | None] = mapped_column(Float)
    last_error: Mapped[str] = mapped_column(String(200), default="")

class RateBucket(Base):
    __tablename__ = "rate_buckets"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[float] = mapped_column(Float, index=True)
