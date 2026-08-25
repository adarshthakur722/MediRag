from generator import (
    generate_report,
    generate_report_feedback,
    generate_doctor_questions,
)
from pdf_extractor import extract_text, parse_lab_text
from range_checker import check_reference_range, check_status
from retriever import retrieve, retrieve_many
from medication_checker import MedicationChecker

med_checker = MedicationChecker()


def analyze_pdf(
    pdf_path,
    use_ai=True,
    medications=None,
):
    report_text = extract_text(pdf_path)
    values = parse_lab_text(report_text)

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
    medications = medications or []

    for test, data in values.items():
        value = data["value"]
        unit = data.get("unit") or ""
        reference_range = data.get("reference_range") or ""

        status = check_reference_range(value, reference_range)

        if status == "unknown":
            status = check_status(test, value)

        rows.append(
            {
                "test": test,
                "value": value,
                "unit": unit,
                "reference_range": reference_range,
                "status": status,
                "context": "",
                "retrieval_error": None,
            }
        )

    queries = [f"{row['test']} {row['status']} meaning" for row in rows]

    try:
        retrieved_contexts = retrieve_many(queries)
    except Exception:
        # Preserve the previous per-test error handling if a batch cannot run.
        retrieved_contexts = []
        for query in queries:
            try:
                retrieved_contexts.append(retrieve(query))
            except Exception as exc:
                retrieved_contexts.append([])
                rows[len(retrieved_contexts) - 1]["retrieval_error"] = str(exc)

    context_parts = []
    for row, retrieved in zip(rows, retrieved_contexts):
        row["context"] = "\n".join(retrieved)
        context_parts.extend(retrieved)

    abnormal_labs = [
        row
        for row in rows
        if row["status"].lower() != "normal"
    ]

    medication_results = med_checker.check_medications(
        medications,
        abnormal_labs,
    )

    medication_context = "".join(
        f"""
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
        for med in medication_results
    )

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
