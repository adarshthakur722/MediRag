import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "data" / "medical_knowledge.json"


def _load_knowledge():
    if not KNOWLEDGE_PATH.exists():
        return []

    with KNOWLEDGE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


knowledge = _load_knowledge()


def check_reference_range(value, reference_range):
    if not reference_range:
        return "unknown"

    cleaned = reference_range.strip().replace(" ", "")

    try:
        if "-" in cleaned:
            low, high = cleaned.split("-", 1)
            low = float(low)
            high = float(high)
            if value < low:
                return "low"
            if value > high:
                return "high"
            return "normal"

        if cleaned.startswith("<"):
            high = float(cleaned[1:])
            return "normal" if value < high else "high"

        if cleaned.startswith(">"):
            low = float(cleaned[1:])
            return "normal" if value > low else "low"
    except ValueError:
        return "unknown"

    return "unknown"


def check_status(test_name, value, gender="male"):
    for item in knowledge:
        if item["test_name"].lower() == test_name.lower():
            if "normal_range_male" in item:
                low, high = item.get(f"normal_range_{gender}", item["normal_range_male"])
            else:
                low, high = item["normal_range"]

            if value < low:
                return "low"
            if value > high:
                return "high"
            return "normal"

    return "unknown"
