from lab_pipeline import analyze_pdf


pdf_path = "data/report.pdf"
result = analyze_pdf(pdf_path, use_ai=True)

print("\nLAB FINDINGS\n")
print(result["findings_text"] or "No lab values detected.")

print("\nLAB REPORT EXPLANATION\n")
if result["report_error"]:
    print(f"Could not generate AI explanation: {result['report_error']}")
else:
    print(result["report"])
