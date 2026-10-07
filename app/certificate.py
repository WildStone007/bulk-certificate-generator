from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_certificate(
    certificate_id: str,
    recipient_name: str,
    event_name: str,
    issuer_name: str,
) -> str:
    file_path = OUTPUT_DIR / f"{certificate_id}.pdf"

    width, height = landscape(A4)
    c = canvas.Canvas(str(file_path), pagesize=(width, height))

    # Simple predefined certificate template
    c.setLineWidth(3)
    c.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm)

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 55 * mm, "CERTIFICATE OF PARTICIPATION")

    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 78 * mm, "This certificate is proudly presented to")

    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 105 * mm, recipient_name)

    c.setFont("Helvetica", 15)
    c.drawCentredString(
        width / 2,
        height - 128 * mm,
        f"for participating in {event_name}",
    )

    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        45 * mm,
        f"Issued by {issuer_name}",
    )

    c.setFont("Helvetica", 9)
    c.drawCentredString(
        width / 2,
        30 * mm,
        f"Certificate ID: {certificate_id}",
    )

    c.save()
    return str(file_path)
