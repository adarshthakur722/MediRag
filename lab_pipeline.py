from generator import generate_report, generate_report_feedback
from pdf_extractor import extract_text, extract_values
from range_checker import check_reference_range, check_status
from retriever import retrieve


def analyze_pdf(pdf_path, use_ai=True):
    values = extract_values(pdf_path)
    report_text = extract_text(pdf_path)
    return analyze_values(values, use_ai=use_ai, report_text=report_text)


def analyze_values(values, use_ai=True, report_text=""):
    rows = []
    context_parts = []

    for test, data in values.items():
        value = data["value"]
        unit = data.get("unit") or ""
        reference_range = data.get("reference_range") or ""

        status = check_reference_range(value, reference_range)
        if status == "unknown":
            status = check_status(test, value)

        retrieved = []
        retrieval_error = None
        try:
            retrieved = retrieve(f"{test} {status} meaning")
            context_parts.extend(retrieved)
        except Exception as exc:
            retrieval_error = str(exc)

        rows.append(
            {
                "test": test,
                "value": value,
                "unit": unit,
                "reference_range": reference_range,
                "status": status,
                "context": "\n".join(retrieved),
                "retrieval_error": retrieval_error,
            }
        )

    findings_text = format_findings(rows)
    context_text = "\n".join(context_parts)

    report = ""
    report_error = None
    if use_ai:
        try:
            if report_text:
                report = generate_report_feedback(report_text, findings_text, context_text)
            else:
                report = generate_report(findings_text, context_text)
        except Exception as exc:
            report_error = str(exc)

    return {
        "values": values,
        "rows": rows,
        "findings_text": findings_text,
        "context_text": context_text,
        "report_text": report_text,
        "report": report,
        "report_error": report_error,
    }


def format_findings(rows):
    lines = []
    for row in rows:
        unit = f" {row['unit']}" if row["unit"] else ""
        lines.append(
            f"{row['test']}: {row['value']}{unit} "
            f"(Reference Range: {row['reference_range']}) "
            f"-> Status: {row['status']}"
        )
    return "\n".join(lines)
