import json

with open("data/medical_knowledge.json", "r") as f:
    knowledge = json.load(f)

def check_status(test_name, value, gender="male"):
    for item in knowledge:
        if item["test_name"] == test_name:

            if "normal_range_male" in item:
                low, high = item[f"normal_range_{gender}"]
            else:
                low, high = item["normal_range"]

            if value < low:
                return "low"
            elif value > high:
                return "high"
            else:
                return "normal"

    return "unknown"