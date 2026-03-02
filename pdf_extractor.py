import pdfplumber
import re

def extract_values(pdf_path):
    results = {}

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    if not text:
        print("⚠ No text extracted from PDF.")
        return results

    # Pattern captures:
    # Test name | value | unit | reference range
    pattern = r"""
        ([A-Za-z\s\(\):]+?)      # Test name
        \s+
        ([<>]?\d+\.?\d*)         # Result value
        \s+
        ([a-zA-Z\/%]+)?          # Units (optional)
        \s+
        (\d+\.?\d*\s*-\s*\d+\.?\d*|<\d+\.?\d*)   # Reference range
    """

    matches = re.findall(pattern, text, re.VERBOSE)

    for match in matches:
        test_name = match[0].strip()
        raw_value = match[1]
        unit = match[2]
        ref_range = match[3]

        clean_value = raw_value.replace("<", "").replace(">", "")

        try:
            value = float(clean_value)
        except:
            continue

        results[test_name] = {
            "value": value,
            "unit": unit,
            "reference_range": ref_range
        }

    print("Extracted structured results:", results)
    return results