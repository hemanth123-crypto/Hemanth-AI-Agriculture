"""Download the currently displayed advisory as a selectable, paginated PDF."""

from datetime import datetime
from io import BytesIO
from typing import List
from xml.sax.saxutils import escape

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    LongTable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    TableStyle,
)

router = APIRouter(prefix="/api", tags=["Advisory Reports"])


class AdvisoryReportPdfRequest(BaseModel):
    report_text: str = Field(min_length=1, max_length=100_000)


def _paragraph_text(value: str) -> str:
    """Escape report text for ReportLab Paragraph's small XML dialect."""
    return escape(value).replace("\n", "<br/>")


def _build_story(report_text: str, generated_at: datetime) -> List[object]:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CropShieldTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=19, leading=24, textColor=colors.HexColor("#0C5635"),
        alignment=TA_LEFT, spaceAfter=3 * mm,
    )
    date_style = ParagraphStyle(
        "CropShieldDate", parent=styles["Normal"], fontName="Helvetica",
        fontSize=9, leading=12, textColor=colors.HexColor("#557466"),
        spaceAfter=8 * mm,
    )
    section_style = ParagraphStyle(
        "CropShieldSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, leading=15, textColor=colors.HexColor("#0C5635"),
        spaceBefore=5 * mm, spaceAfter=2 * mm, keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "CropShieldBody", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9, leading=13, textColor=colors.HexColor("#202B25"),
        spaceAfter=1.5 * mm, splitLongWords=1,
    )
    table_style = ParagraphStyle(
        "CropShieldTableCell", parent=body_style, fontSize=8, leading=10,
        spaceAfter=0,
    )
    table_header_style = ParagraphStyle(
        "CropShieldTableHeader", parent=table_style, fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story: List[object] = [
        Paragraph("CropShield AI", title_style),
        Paragraph("Official Agronomic Advisory Report", section_style),
        Paragraph(f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M %Z')}", date_style),
    ]
    lines = report_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            story.append(Spacer(1, 1.3 * mm))
            index += 1
            continue

        # Convert the generated pipe-delimited crop recommendations to a real table.
        if "|" in line and index + 1 < len(lines) and "---|" in lines[index + 1].replace(" ", ""):
            header = [cell.strip() for cell in line.strip("|").split("|")]
            rows = [[Paragraph(_paragraph_text(cell), table_header_style) for cell in header]]
            index += 2  # Skip the markdown table separator.
            while index < len(lines) and "|" in lines[index]:
                cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if len(cells) < len(header):
                    cells.extend([""] * (len(header) - len(cells)))
                rows.append([Paragraph(_paragraph_text(cell), table_style) for cell in cells[:len(header)]])
                index += 1
            story.append(LongTable(rows, colWidths=[23 * mm, 27 * mm, 17 * mm, 27 * mm, 80 * mm], repeatRows=1, hAlign="LEFT"))
            story[-1].setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B45")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F7F2")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B9D5C5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(Spacer(1, 2.5 * mm))
            continue

        # Treat section labels (uppercase titles and the mixed-case conditions heading)
        # as headings; retain all other report lines verbatim as selectable text.
        is_heading = line.isupper() and len(line) <= 64
        is_heading = is_heading or line.lower() == "interpreted conditions"
        if line and all(char == "-" for char in line):
            index += 1
            continue
        if is_heading:
            story.append(Paragraph(_paragraph_text(line), section_style))
        else:
            story.append(Paragraph(_paragraph_text(line), body_style))
        index += 1
    return story


def build_advisory_pdf(report_text: str, generated_at: datetime | None = None) -> bytes:
    """Create a fresh multi-page PDF from the complete report text sent by the UI."""
    generated_at = generated_at or datetime.now().astimezone()
    output = BytesIO()
    document = SimpleDocTemplate(
        output, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=20 * mm, bottomMargin=18 * mm,
        pageCompression=0,
        title="CropShield AI Agricultural Advisory Report",
        author="CropShield AI",
        subject="Official Agronomic Advisory Report",
    )

    def draw_page(canvas, doc):
        canvas.saveState()
        page_width, page_height = A4
        canvas.setStrokeColor(colors.HexColor("#45A675"))
        canvas.setLineWidth(0.7)
        canvas.line(16 * mm, page_height - 13 * mm, page_width - 16 * mm, page_height - 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64786C"))
        canvas.drawString(16 * mm, 10 * mm, "CropShield AI · Agricultural decision support")
        canvas.drawRightString(page_width - 16 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(_build_story(report_text, generated_at), onFirstPage=draw_page, onLaterPages=draw_page)
    return output.getvalue()


@router.post("/advisory-report/pdf")
def download_advisory_report_pdf(request: AdvisoryReportPdfRequest):
    report_text = request.report_text.strip()
    if not report_text:
        raise HTTPException(status_code=422, detail="The advisory report is empty.")
    generated_at = datetime.now().astimezone()
    filename = f"CropShield_Agricultural_Advisory_Report_{generated_at:%Y-%m-%d}.pdf"
    try:
        pdf_bytes = build_advisory_pdf(report_text, generated_at)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="PDF generation failed. Please try again.") from exc
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
