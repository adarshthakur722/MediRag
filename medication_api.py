# medication_api.py

import json
from functools import lru_cache

import requests

from generator import summarize_medication_info


class MedicationAPI:

    def __init__(self):

        self.openfda_url = "https://api.fda.gov/drug/label.json"

        self.generic_mappings = {
            "paracetamol": "acetaminophen",
            "dolo 650": "acetaminophen",
            "crocin": "acetaminophen",
            "calpol": "acetaminophen",
            "glycomet": "metformin",
            "telma": "telmisartan",
            "ecosprin": "aspirin",
        }

    def normalize_medication_name(
        self,
        medication_name,
    ):

        normalized = medication_name.lower().strip()

        return self.generic_mappings.get(
            normalized,
            medication_name,
        )

    @lru_cache(maxsize=128)
    def fetch_medication_info(
        self,
        medication_name,
    ):

        original_name = medication_name.strip()

        medication_name = self.normalize_medication_name(
            original_name
        )

        return self.fetch_from_openfda(
            medication_name,
            original_name,
        )

    def summarize_openfda_data(
        self,
        medication_info,
    ):

        raw_text = f"""
Purpose:
{medication_info.get('purpose', '')}

Usage:
{medication_info.get('usage', '')}

Warnings:
{medication_info.get('warnings', '')}

Side Effects:
{medication_info.get('side_effects', '')}

Dosage:
{medication_info.get('dosage', '')}
"""

        try:

            response = summarize_medication_info(
                raw_text
            )

            if not response:
                return medication_info
            cleaned = response.strip()

            if cleaned.startswith("```json"):

                cleaned = cleaned.replace(
                    "```json",
                    ""
                ).replace(
                    "```",
                    ""
                ).strip()

            summarized = json.loads(cleaned)

            medication_info["purpose"] = summarized.get(
                "purpose",
                medication_info["purpose"],
            )

            medication_info["usage"] = summarized.get(
                "usage",
                medication_info["usage"],
            )

            medication_info["warnings"] = summarized.get(
                "warnings",
                medication_info["warnings"],
            )

            medication_info["side_effects"] = summarized.get(
                "side_effects",
                medication_info["side_effects"],
            )

            medication_info["dosage"] = summarized.get(
                "dosage",
                medication_info["dosage"],
            )

            return medication_info

        except Exception:

            return medication_info

    def fetch_from_openfda(
        self,
        medication_name,
        original_name=None,
    ):

        try:

            query = (
                f'{self.openfda_url}?search=openfda.generic_name:"{medication_name}"&limit=1'
            )

            response = requests.get(query)

            if response.status_code != 200:
                return None

            data = response.json()

            if "results" not in data:
                return None

            result = data["results"][0]

            medication_info = {
                "medication": original_name or medication_name,
                "generic_name": medication_name,
                "purpose": self.extract_text(
                    result,
                    "purpose"
                ),
                "usage": self.extract_text(
                    result,
                    "indications_and_usage"
                ),
                "warnings": self.extract_text(
                    result,
                    "warnings"
                ),
                "side_effects": self.extract_text(
                    result,
                    "adverse_reactions"
                ),
                "dosage": self.extract_text(
                    result,
                    "dosage_and_administration"
                ),
            }

            return self.summarize_openfda_data(
                medication_info
            )

        except Exception as e:

            print("OpenFDA Error:", e)

            return None

    def extract_text(
        self,
        result,
        key,
    ):

        value = result.get(key)

        if not value:
            return "Not available"

        if isinstance(value, list):
            return value[0]

        return str(value)