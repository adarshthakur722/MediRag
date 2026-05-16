from generator import (
    generate_report,
    generate_report_feedback,
    generate_doctor_questions,
)
from pdf_extractor import extract_text, extract_values
from range_checker import check_reference_range, check_status
from retriever import retrieve
from medication_checker import MedicationChecker

med_checker = MedicationChecker()


def analyze_pdf(
    pdf_path,
    use_ai=True,
    medications=None,
):
    values = extract_values(pdf_path)
    report_text = extract_text(pdf_path)

    return analyze_values(
        values,
        use_ai=use_ai,
        report_text=report_text,
        medications=medications,
    )


def analyze_values(
    values,
    use_ai=True,
    report_text="",
    medications=None,
):
    rows = []
    context_parts = []
    medications = medications or []

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

    abnormal_labs = [
        row
        for row in rows
        if row["status"].lower() != "normal"
    ]

    medication_results = med_checker.check_medications(
        medications,
        abnormal_labs,
    )

    medication_context = ""

    for med in medication_results:

        medication_context += f"""
Medication: {med.get('medication')}

Purpose:
{med.get('purpose')}

Usage:
{med.get('usage')}

Warnings:
{med.get('warnings')}

Side Effects:
{med.get('side_effects')}

Lab Warnings:
{', '.join(med.get('lab_warnings', [])) if med.get('lab_warnings') else 'None'}

"""

    findings_text = format_findings(rows)
    context_text = "\n".join(context_parts)

    report = ""
    report_error = ""

    if use_ai:

        try:

            if report_text:
                report = generate_report_feedback(
                    report_text,
                    findings_text,
                    context_text,
                    medication_context,
                )

            else:
                report = generate_report(
                    findings_text,
                    context_text,
                    medication_context,
                )

        except Exception as exc:
            report_error = str(exc)

    doctor_questions = ""

    if use_ai:

        try:

            doctor_questions = generate_doctor_questions(
                findings_text,
                context_text,
                medication_context,
            )

        except Exception:
            doctor_questions = ""

    return {
        "values": values,
        "rows": rows,
        "findings_text": findings_text,
        "context_text": context_text,
        "report_text": report_text,
        "medication_results": medication_results,
        "report": report,
        "doctor_questions": doctor_questions,
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