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


# ============================================================
# TEXT / UNICODE HELPERS
# ============================================================

def _normalize_text(value, fallback="Not available"):
    """
    Convert text to characters that ReportLab's built-in
    Helvetica font can reliably render.

    This prevents Unicode characters such as non-breaking
    hyphens from appearing as black square boxes (■).
    """

    text = str(value or fallback)

    replacements = {
        # Hyphens / dashes
        "\u2010": "-",   # Hyphen
        "\u2011": "-",   # Non-breaking hyphen
        "\u2012": "-",   # Figure dash
        "\u2013": "-",   # En dash
        "\u2014": "-",   # Em dash
        "\u2015": "-",   # Horizontal bar
        "\u2212": "-",   # Mathematical minus

        # Spaces
        "\u00a0": " ",   # Non-breaking space
        "\u2007": " ",   # Figure space
        "\u202f": " ",   # Narrow no-break space

        # Quotes
        "\u2018": "'",   # Left single quotation mark
        "\u2019": "'",   # Right single quotation mark
        "\u201a": "'",   # Single low-9 quotation mark
        "\u201b": "'",   # Single high-reversed-9 quotation mark

        "\u201c": '"',   # Left double quotation mark
        "\u201d": '"',   # Right double quotation mark
        "\u201e": '"',   # Double low-9 quotation mark
        "\u201f": '"',   # Double high-reversed-9 quotation mark

        # Ellipsis
        "\u2026": "...",

        # Bullets / special symbols
        "\u2022": "-",   # Bullet
        "\u25cf": "-",   # Black circle
        "\u25aa": "-",   # Small black square
        "\u25a0": "-",   # Black square

        # Other common Unicode characters
        "\u00b7": "-",   # Middle dot
        "\u00d7": "x",   # Multiplication sign
        "\u2264": "<=",  # Less than or equal
        "\u2265": ">=",  # Greater than or equal

        # Soft hyphen
        "\u00ad": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def _text(value, fallback="Not available"):
    """
    Escape text safely for ReportLab Paragraphs.
    """
    text = _normalize_text(value, fallback)
    return escape(text).replace("\n", "<br/>")


# ============================================================
# MARKDOWN-LIKE AI TEXT RENDERING
# ============================================================

def _markdown_paragraphs(value, styles):
    """
    Render simple markdown-like AI output.

    Supported:
        # Heading
        ## Heading
        - Bullet
        * Bullet

    Unicode characters are normalized before rendering.
    """

    paragraphs = []

    for raw_line in (value or "").splitlines():

        line = raw_line.strip()

        # Empty line
        if not line:
            paragraphs.append(Spacer(1, 5))
            continue

        # Markdown heading
        if line.startswith("#"):

            heading = line.lstrip("#").strip()

            paragraphs.append(
                Paragraph(
                    _text(heading),
                    styles["section"],
                )
            )

        # Markdown bullet
        elif line.startswith(("- ", "* ")):

            bullet_text = line[2:].strip()

            paragraphs.append(
                Paragraph(
                    f"- {_text(bullet_text)}",
                    styles["body"],
                )
            )

        # Normal paragraph
        else:

            paragraphs.append(
                Paragraph(
                    _text(line),
                    styles["body"],
                )
            )

    if not paragraphs:
        paragraphs.append(
            Paragraph(
                "No AI explanation was generated.",
                styles["body"],
            )
        )

    return paragraphs


# ============================================================
# PDF FOOTER
# ============================================================

def _footer(canvas, document):
    """
    Add MediRag footer and page number.
    """

    canvas.saveState()

    canvas.setFont("Helvetica", 8)

    canvas.setFillColor(
        colors.HexColor("#667085")
    )

    canvas.drawString(
        document.leftMargin,
        0.45 * inch,
        "MediRag - Educational information only; "
        "not medical advice or diagnosis.",
    )

    canvas.drawRightString(
        A4[0] - document.rightMargin,
        0.45 * inch,
        f"Page {document.page}",
    )

    canvas.restoreState()


# ============================================================
# MAIN PDF GENERATOR
# ============================================================

def build_analysis_pdf(
    report_name,
    result,
    medications=None,
):
    """
    Create a detailed downloadable PDF from an
    already-calculated MediRag analysis result.

    The function does not modify the analysis itself.
    It only formats the existing result into a PDF.
    """

    buffer = BytesIO()

    # --------------------------------------------------------
    # DOCUMENT SETTINGS
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,

        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,

        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,

        title="MediRag Lab Report Analysis",
        author="MediRag",
    )

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    base = getSampleStyleSheet()

    styles = {

        # Main title
        "title": ParagraphStyle(
            "MediRagTitle",
            parent=base["Title"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#12355B"),
            spaceAfter=8,
        ),

        # Report metadata
        "meta": ParagraphStyle(
            "MediRagMeta",
            parent=base["Normal"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#667085"),
            fontSize=9,
            leading=12,
            spaceAfter=14,
        ),

        # Section headings
        "section": ParagraphStyle(
            "MediRagSection",
            parent=base["Heading2"],
            textColor=colors.HexColor("#12355B"),
            spaceBefore=12,
            spaceAfter=6,
        ),

        # Normal body text
        "body": ParagraphStyle(
            "MediRagBody",
            parent=base["BodyText"],
            leading=14,
            spaceAfter=5,
        ),

        # Small table text
        "small": ParagraphStyle(
            "MediRagSmall",
            parent=base["BodyText"],
            fontSize=8.5,
            leading=11,
        ),
    }

    # --------------------------------------------------------
    # STORY
    # --------------------------------------------------------

    story = [

        Paragraph(
            "MediRag Lab Report Analysis",
            styles["title"],
        ),

        Paragraph(
            f"Report: {_text(report_name)}"
            f"<br/>"
            f"Generated: "
            f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}",
            styles["meta"],
        ),

        Paragraph(
            "Extracted Lab Values",
            styles["section"],
        ),
    ]

    # ========================================================
    # LAB VALUES TABLE
    # ========================================================

    rows = result.get("rows", [])

    table_data = [
        [
            "Test",
            "Value",
            "Reference range",
            "Status",
        ]
    ]

    for row in rows:

        test_name = _text(
            row.get("test")
        )

        value = row.get("value", "")
        unit = row.get("unit", "")

        value_text = _text(
            f"{value} {unit}".strip()
        )

        reference_range = _text(
            row.get("reference_range")
        )

        status = _text(
            str(
                row.get(
                    "status",
                    "unknown",
                )
            ).upper()
        )

        table_data.append(
            [
                Paragraph(
                    test_name,
                    styles["small"],
                ),

                Paragraph(
                    value_text,
                    styles["small"],
                ),

                Paragraph(
                    reference_range,
                    styles["small"],
                ),

                Paragraph(
                    status,
                    styles["small"],
                ),
            ]
        )

    # No structured values
    if len(table_data) == 1:

        story.append(
            Paragraph(
                "No structured lab values were detected.",
                styles["body"],
            )
        )

    # Structured values available
    else:

        table = Table(
            table_data,

            colWidths=[
                2.1 * inch,
                1.15 * inch,
                1.55 * inch,
                1.15 * inch,
            ],

            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [

                    # Header
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#12355B"),
                    ),

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),

                    # Grid
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor("#D0D5DD"),
                    ),

                    # Alignment
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),

                    # Background
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.HexColor("#F8FAFC"),
                    ),

                    # Alternating rows
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F8FAFC"),
                        ],
                    ),

                    # Padding
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(table)

    # ========================================================
    # AI EXPLANATION
    # ========================================================

    story.extend(
        [
            Paragraph(
                "AI Explanation",
                styles["section"],
            ),

            *_markdown_paragraphs(
                result.get("report"),
                styles,
            ),
        ]
    )

    # ========================================================
    # DOCTOR QUESTIONS
    # ========================================================

    questions = result.get(
        "doctor_questions",
        "",
    )

    if questions and questions.strip():

        story.extend(
            [
                Paragraph(
                    "Questions You May Want To Ask Your Doctor",
                    styles["section"],
                ),

                *_markdown_paragraphs(
                    questions,
                    styles,
                ),
            ]
        )

    # ========================================================
    # MEDICATION AWARENESS
    # ========================================================

    medication_results = result.get(
        "medication_results",
        [],
    )

    story.append(
        Paragraph(
            "Medication Awareness",
            styles["section"],
        )
    )

    if medication_results:

        for medication in medication_results:

            medication_name = ", ".join(
                medication.get(
                    "medications",
                    [],
                )
            )

            if not medication_name:

                medication_name = medication.get(
                    "generic_name",
                    "Medication",
                )

            details = [

                Paragraph(
                    f"<b>{_text(medication_name)}</b>",
                    styles["body"],
                ),

                Paragraph(
                    f"<b>Purpose:</b> "
                    f"{_text(medication.get('purpose'))}",
                    styles["body"],
                ),

                Paragraph(
                    f"<b>Usage:</b> "
                    f"{_text(medication.get('usage'))}",
                    styles["body"],
                ),

                Paragraph(
                    f"<b>Warnings:</b> "
                    f"{_text(medication.get('warnings'))}",
                    styles["body"],
                ),

                Paragraph(
                    f"<b>Side effects:</b> "
                    f"{_text(medication.get('side_effects'))}",
                    styles["body"],
                ),
            ]

            # Lab warnings
            lab_warnings = medication.get(
                "lab_warnings",
                [],
            )

            if lab_warnings:

                details.append(
                    Paragraph(
                        f"<b>Lab-related warnings:</b> "
                        f"{_text(' '.join(lab_warnings))}",
                        styles["body"],
                    )
                )

            story.append(
                KeepTogether(details)
            )

    elif medications:

        story.append(
            Paragraph(
                "Medication information could not be retrieved.",
                styles["body"],
            )
        )

    else:

        story.append(
            Paragraph(
                "No medications were provided.",
                styles["body"],
            )
        )

    # ========================================================
    # RETRIEVED MEDICAL CONTEXT
    # ========================================================

    context = result.get(
        "context_text",
        "",
    )

    if context and context.strip():

        story.extend(
            [
                PageBreak(),

                Paragraph(
                    "Retrieved Medical Context",
                    styles["section"],
                ),

                Paragraph(
                    _text(context),
                    styles["body"],
                ),
            ]
        )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    story.extend(
        [

            Paragraph(
                "Important Disclaimer",
                styles["section"],
            ),

            Paragraph(
                "This document is for educational purposes only. "
                "It does not provide medical advice, diagnosis, or treatment."
                "<br/>"
                "Please discuss your results with a qualified healthcare professional.",
                styles["body"],
            ),
        ]
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story,
        onFirstPage=_footer,
        onLaterPages=_footer,
    )

    return buffer.getvalue()