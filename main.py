from pdf_extractor import extract_values
from range_checker import check_status
from retriever import retrieve
from generator import generate_report

pdf_path = "data/report.pdf"

values = extract_values(pdf_path)

findings_text = ""
context_text = ""

for test, data in values.items():

    value = data["value"]
    ref_range = data["reference_range"]

    # Determine status using reference range directly
    status = "unknown"

    if "-" in ref_range:
        low, high = ref_range.split("-")
        low = float(low.strip())
        high = float(high.strip())

        if value < low:
            status = "low"
        elif value > high:
            status = "high"
        else:
            status = "normal"

    findings_text += (
        f"{test}: {value} "
        f"(Reference Range: {ref_range}) "
        f"→ Status: {status}\n"
    )

    retrieved = retrieve(f"{test} {status} meaning")
    context_text += "\n".join(retrieved) + "\n"

final_output = generate_report(findings_text, context_text)

print("\n📊 LAB REPORT EXPLANATION\n")
print(final_output)