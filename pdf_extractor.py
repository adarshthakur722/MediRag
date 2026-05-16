import re

import pdfplumber


def extract_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

            for table in page.extract_tables() or []:
                for row in table:
                    cells = [cell.strip() for cell in row if cell and cell.strip()]
                    if cells:
                        text += " ".join(cells) + "\n"

    return text.strip()


def parse_lab_text(text):
    results = {}

    if not text:
        return results

    patterns = [
        r"""
            (?P<test>[A-Za-z][A-Za-z\s\(\):/%#.-]{1,60}?)
            \s+
            (?P<value>[<>]?\d+(?:\.\d+)?)
            \s*
            (?P<unit>[A-Za-z/%]+)?
            \s+
            (?P<range>\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?|[<>]\s*\d+(?:\.\d+)?)
        """,
        r"""
            (?P<test>[A-Za-z][A-Za-z\s\(\):/%#.-]{1,60}?)
            \s*[:|-]\s*
            (?P<value>[<>]?\d+(?:\.\d+)?)
            \s*
            (?P<unit>[A-Za-z/%]+)?
            .*?
            (?P<range>\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?|[<>]\s*\d+(?:\.\d+)?)
        """,
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.VERBOSE | re.IGNORECASE):
            _add_result(
                results,
                match.group("test"),
                match.group("value"),
                match.group("unit"),
                match.group("range"),
            )

    return results


def _add_result(results, test_name, raw_value, unit, ref_range):
    test_name = re.sub(r"\s+", " ", test_name).strip(" :-")
    clean_value = raw_value.replace("<", "").replace(">", "").strip()

    if len(test_name) < 2:
        return

    try:
        value = float(clean_value)
    except ValueError:
        return

    results[test_name] = {
        "value": value,
        "unit": (unit or "").strip(),
        "reference_range": re.sub(r"\s+", " ", ref_range).strip(),
    }


def extract_values(pdf_path):
    text = extract_text(pdf_path)

    if not text:
        print("No text extracted from PDF.")
        return {}

    results = parse_lab_text(text)
    print("Extracted structured results:", results)
    return results
