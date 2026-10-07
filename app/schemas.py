from pydantic import BaseModel, EmailStr, Field


class Recipient(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class CertificateRequest(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=200)
    issuer_name: str = Field(..., min_length=1, max_length=200)
    recipients: list[Recipient] = Field(..., min_length=1, max_length=1000)


class CertificateSummary(BaseModel):
    id: str
    recipient_name: str
    recipient_email: str
    status: str
    download_url: str | None = None
    error_message: str | None = None


class BatchResponse(BaseModel):
    request_id: str
    event_name: str
    issuer_name: str
    status: str
    total: int
    generated: int
    failed: int
    certificates: list[CertificateSummary]
