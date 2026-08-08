"""Presentation-only PDF export for completed MediRag analyses."""

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _text(value, fallback="Not available"):
    """Return safely escaped text that ReportLab can render."""
    return escape(str(value or fallback)).replace("\n", "<br/>")


def _markdown_paragraphs(value, styles):
    """Render simple markdown-like AI output without changing its content."""
    paragraphs = []
    for raw_line in (value or "").splitlines():
        line = raw_line.strip()
        if not line:
            paragraphs.append(Spacer(1, 5))
            continue
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            paragraphs.append(Paragraph(_text(heading), styles["section"]))
        elif line.startswith(("- ", "* ")):
            paragraphs.append(Paragraph(f"• {_text(line[2:])}", styles["body"]))
        else:
            paragraphs.append(Paragraph(_text(line), styles["body"]))
    return paragraphs or [Paragraph("No AI explanation was generated.", styles["body"])]


def _footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(document.leftMargin, 0.45 * inch, "MediRag - Educational information only; not medical advice or diagnosis.")
    canvas.drawRightString(A4[0] - document.rightMargin, 0.45 * inch, f"Page {document.page}")
    canvas.restoreState()


def build_analysis_pdf(report_name, result, medications=None):
    """Create a detailed downloadable PDF from an already-calculated result."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,
        title="MediRag Lab Report Analysis",
    )
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("MediRagTitle", parent=base["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#12355B"), spaceAfter=8),
        "meta": ParagraphStyle("MediRagMeta", parent=base["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#667085"), fontSize=9, spaceAfter=14),
        "section": ParagraphStyle("MediRagSection", parent=base["Heading2"], textColor=colors.HexColor("#12355B"), spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("MediRagBody", parent=base["BodyText"], leading=14, spaceAfter=5),
        "small": ParagraphStyle("MediRagSmall", parent=base["BodyText"], fontSize=8.5, leading=11),
    }
    story = [
        Paragraph("MediRag Lab Report Analysis", styles["title"]),
        Paragraph(f"Report: {_text(report_name)}<br/>Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}", styles["meta"]),
        Paragraph("Extracted Lab Values", styles["section"]),
    ]

    rows = result.get("rows", [])
    table_data = [["Test", "Value", "Reference range", "Status"]]
    for row in rows:
        table_data.append([
            Paragraph(_text(row.get("test")), styles["small"]),
            Paragraph(_text(f"{row.get('value', '')} {row.get('unit', '')}".strip()), styles["small"]),
            Paragraph(_text(row.get("reference_range")), styles["small"]),
            Paragraph(_text(str(row.get("status", "unknown")).upper()), styles["small"]),
        ])
    if len(table_data) == 1:
        story.append(Paragraph("No structured lab values were detected.", styles["body"]))
    else:
        table = Table(table_data, colWidths=[2.1 * inch, 1.15 * inch, 1.55 * inch, 1.15 * inch], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D0D5DD")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)

    story.extend([Paragraph("AI Explanation", styles["section"]), *_markdown_paragraphs(result.get("report"), styles)])

    questions = result.get("doctor_questions", "")
    if questions.strip():
        story.extend([Paragraph("Questions You May Want To Ask Your Doctor", styles["section"]), *_markdown_paragraphs(questions, styles)])

    medication_results = result.get("medication_results", [])
    story.append(Paragraph("Medication Awareness", styles["section"]))
    if medication_results:
        for medication in medication_results:
            medication_name = ", ".join(medication.get("medications", [])) or medication.get("generic_name", "Medication")
            details = [
                Paragraph(f"<b>{_text(medication_name)}</b>", styles["body"]),
                Paragraph(f"<b>Purpose:</b> {_text(medication.get('purpose'))}", styles["body"]),
                Paragraph(f"<b>Usage:</b> {_text(medication.get('usage'))}", styles["body"]),
                Paragraph(f"<b>Warnings:</b> {_text(medication.get('warnings'))}", styles["body"]),
                Paragraph(f"<b>Side effects:</b> {_text(medication.get('side_effects'))}", styles["body"]),
            ]
            lab_warnings = medication.get("lab_warnings", [])
            if lab_warnings:
                details.append(Paragraph(f"<b>Lab-related warnings:</b> {_text(' '.join(lab_warnings))}", styles["body"]))
            story.append(KeepTogether(details))
    elif medications:
        story.append(Paragraph("Medication information could not be retrieved.", styles["body"]))
    else:
        story.append(Paragraph("No medications were provided.", styles["body"]))

    context = result.get("context_text", "")
    if context.strip():
        story.extend([PageBreak(), Paragraph("Retrieved Medical Context", styles["section"]), Paragraph(_text(context), styles["body"])])

    story.extend([
        Paragraph("Important Disclaimer", styles["section"]),
        Paragraph("This document is for educational purposes only. It does not provide medical advice, diagnosis, or treatment.<br/>Please discuss your results with a qualified healthcare professional.", styles["body"]),
    ])
    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
