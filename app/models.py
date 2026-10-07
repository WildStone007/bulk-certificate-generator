import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class BatchStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class CertificateStatus(str, enum.Enum):
    pending = "pending"
    generated = "generated"
    failed = "failed"


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    event_name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[BatchStatus] = mapped_column(
        Enum(BatchStatus), default=BatchStatus.pending, nullable=False
    )
    total: Mapped[int] = mapped_column(Integer, default=0)
    generated: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    certificates = relationship(
        "Certificate",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    batch_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("batches.id"), nullable=False
    )
    recipient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[CertificateStatus] = mapped_column(
        Enum(CertificateStatus), default=CertificateStatus.pending, nullable=False
    )
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    batch = relationship("Batch", back_populates="certificates")
