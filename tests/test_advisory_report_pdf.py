import asyncio
import re

from app.api.routes_advisory_report import (
    AdvisoryReportPdfRequest,
    download_advisory_report_pdf,
)


def test_advisory_pdf_is_paginated_and_contains_complete_report():
    report = (
        "AGRICULTURAL ADVISORY\n\n"
        "Interpreted Conditions\n"
        "----------------------\n"
        "Crop: Rice\nSeason: Kharif\nState: Andhra Pradesh\n\n"
        "RECOMMENDED CROPS\n"
        "Crop | Suitability | Risk | Historical Yield | Reason\n"
        "---|---|---|---|---\n"
        "Rice | High (0.95) | Low | 4.20 t/ha | Soil and rainfall match.\n\n"
        + ("Historical evidence paragraph continues across pages.\n" * 160)
        + "FINAL_REPORT_SENTINEL"
    )
    response = download_advisory_report_pdf(AdvisoryReportPdfRequest(report_text=report))

    async def read_response():
        return b"".join([chunk async for chunk in response.body_iterator])

    pdf = asyncio.run(read_response())
    page_objects = re.findall(rb"/Type /Page\s", pdf)

    assert response.media_type == "application/pdf"
    assert "CropShield_Agricultural_Advisory_Report_" in response.headers["content-disposition"]
    assert pdf.startswith(b"%PDF-")
    assert len(page_objects) > 1
    assert b"FINAL_REPORT_SENTINEL" in pdf
    assert b"Soil and rainfall match." in pdf
