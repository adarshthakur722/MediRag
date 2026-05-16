# medication_checker.py

from medication_api import MedicationAPI


class MedicationChecker:

    def __init__(self):
        self.api = MedicationAPI()

    def check_medications(
        self,
        medications,
        abnormal_labs=None
    ):

        abnormal_labs = abnormal_labs or []

        grouped_medications = {}

        for original_med in medications:

            info = self.api.fetch_medication_info(
                original_med
            )

            if not info:
                continue

            generic_name = info.get(
                "generic_name",
                original_med.lower(),
            ).lower()

            if generic_name not in grouped_medications:

                lab_warnings = self.generate_lab_warnings(
                    generic_name,
                    abnormal_labs
                )

                grouped_medications[generic_name] = {
                    "medications": [original_med],
                    "generic_name": generic_name,
                    "purpose": info.get("purpose"),
                    "usage": info.get("usage"),
                    "warnings": info.get("warnings"),
                    "side_effects": info.get("side_effects"),
                    "dosage": info.get("dosage"),
                    "lab_warnings": lab_warnings,
                }

            else:

                grouped_medications[generic_name][
                    "medications"
                ].append(original_med)

        return list(grouped_medications.values())

    def generate_lab_warnings(
        self,
        medication,
        abnormal_labs
    ):

        warnings = []

        medication = medication.lower()

        for lab in abnormal_labs:

            test = lab.get("test", "").lower()
            status = lab.get("status", "").lower()

            # Diabetes medicine warning
            if medication in ["metformin", "glycomet"]:

                if test == "creatinine" and status == "high":

                    warnings.append(
                        "High creatinine may indicate kidney dysfunction while using Metformin."
                    )

            # Statin warning
            if medication in ["atorvastatin", "rosuvastatin"]:

                if test in ["sgpt", "alt"] and status == "high":

                    warnings.append(
                        "Elevated liver enzymes may increase statin-related liver complications."
                    )

            # Insulin warning
            if medication == "insulin":

                if test == "glucose" and status == "low":

                    warnings.append(
                        "Low glucose may indicate excessive insulin effect."
                    )

        return warnings