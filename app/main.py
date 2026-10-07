from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .certificate import generate_certificate
from .database import Base, SessionLocal, engine
from .models import Batch, BatchStatus, Certificate, CertificateStatus
from .schemas import BatchResponse, CertificateRequest

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator",
    version="1.0.0",
    description="Generate and retrieve certificates in bulk.",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_response(batch: Batch) -> BatchResponse:
    certificates = [
        {
            "id": cert.id,
            "recipient_name": cert.recipient_name,
            "recipient_email": cert.recipient_email,
            "status": cert.status.value,
            "download_url": (
                f"/certificates/{cert.id}/download"
                if cert.status == CertificateStatus.generated
                else None
            ),
            "error_message": cert.error_message,
        }
        for cert in batch.certificates
    ]

    return BatchResponse(
        request_id=batch.id,
        event_name=batch.event_name,
        issuer_name=batch.issuer_name,
        status=batch.status.value,
        total=batch.total,
        generated=batch.generated,
        failed=batch.failed,
        certificates=certificates,
    )


def process_batch(batch_id: str):
    """
    Runs after POST /requests returns.
    A separate DB session is used because this runs outside
    the request handler.
    """
    db = SessionLocal()

    try:
        batch = db.get(Batch, batch_id)
        if not batch:
            return

        batch.status = BatchStatus.processing
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.batch_id == batch_id)
            .all()
        )

        generated = 0
        failed = 0

        for cert in certificates:
            try:
                cert.status = CertificateStatus.pending
                db.commit()

                cert.file_path = generate_certificate(
                    certificate_id=cert.id,
                    recipient_name=cert.recipient_name,
                    event_name=batch.event_name,
                    issuer_name=batch.issuer_name,
                )

                cert.status = CertificateStatus.generated
                cert.error_message = None
                generated += 1

            except Exception as exc:
                cert.status = CertificateStatus.failed
                cert.error_message = str(exc)
                failed += 1

            db.commit()

            batch.generated = generated
            batch.failed = failed
            db.commit()

        batch.status = (
            BatchStatus.completed if failed == 0 else BatchStatus.completed
        )
        db.commit()

    except Exception:
        batch = db.get(Batch, batch_id)
        if batch:
            batch.status = BatchStatus.failed
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/requests", response_model=BatchResponse, status_code=202)
def create_certificate_request(
    request: CertificateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Basic duplicate-email validation inside the same request
    emails = [str(r.email).lower() for r in request.recipients]
    if len(emails) != len(set(emails)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate recipient email found in the request.",
        )

    batch = Batch(
        event_name=request.event_name,
        issuer_name=request.issuer_name,
        total=len(request.recipients),
        status=BatchStatus.pending,
    )
    db.add(batch)
    db.flush()

    for recipient in request.recipients:
        db.add(
            Certificate(
                batch_id=batch.id,
                recipient_name=recipient.name.strip(),
                recipient_email=str(recipient.email).lower(),
                status=CertificateStatus.pending,
            )
        )

    db.commit()
    db.refresh(batch)

    # Bulk generation happens after the API accepts the request.
    background_tasks.add_task(process_batch, batch.id)

    return build_response(batch)


@app.get("/requests/{request_id}", response_model=BatchResponse)
def get_request(request_id: str, db: Session = Depends(get_db)):
    batch = db.get(Batch, request_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Request not found.")

    return build_response(batch)


@app.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    cert = db.get(Certificate, certificate_id)

    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")

    if cert.status != CertificateStatus.generated or not cert.file_path:
        raise HTTPException(
            status_code=409,
            detail="Certificate is not generated yet.",
        )

    file_path = Path(cert.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Generated certificate file not found.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{cert.recipient_name}_certificate.pdf",
    )
