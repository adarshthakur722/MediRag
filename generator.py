import os
import logging

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from groq import Groq
except ImportError:
    Groq = None


# =========================
# LOGGING CONFIG
# =========================

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================
# LOAD ENV
# =========================

if load_dotenv:
    load_dotenv()


# =========================
# CREATE GROQ CLIENT
# =========================

def _create_client():

    if Groq is None:
        logging.error("groq package is not installed")

        raise RuntimeError(
            "AI service is temporarily unavailable."
        )

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        logging.error("GROQ_API_KEY missing in environment")

        raise RuntimeError(
            "AI service configuration error."
        )

    return Groq(api_key=api_key)


# =========================
# CLEAN ERROR MESSAGES
# =========================

def _clean_api_error(error):

    logging.error(f"GROQ ERROR: {str(error)}")

    message = str(error).lower()

    if "invalid" in message or "authentication" in message:
        return (
            "AI service authentication failed. "
            "Please try again later."
        )

    if "quota" in message or "rate limit" in message:
        return (
            "AI service is currently busy. "
            "Please try again later."
        )

    if "permission" in message or "403" in message:
        return (
            "AI service is currently unavailable."
        )

    if "connection" in message or "network" in message:
        return (
            "Network issue detected. "
            "Please try again."
        )

    return (
        "Unable to generate AI analysis right now. "
        "Please try again later."
    )


# =========================
# COMMON RESPONSE FUNCTION
# =========================

def _generate_response(prompt):

    try:

        client = _create_client()

        response = client.chat.completions.create(
            model=os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            ),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=2500,
        )

        return response.choices[0].message.content

    except Exception as exc:

        raise RuntimeError(
            _clean_api_error(exc)
        ) from exc


# =========================
# GENERATE REPORT
# =========================

def generate_report(
    findings,
    context,
    medication_context=""
):

    if not findings.strip():
        return "No lab values detected."

    prompt = f"""
You are an advanced AI medical lab report explanation assistant.

Your goal is to explain medical reports in SIMPLE,
CLEAR, DETAILED language for normal users.

IMPORTANT RULES:
- Do NOT diagnose diseases
- Do NOT prescribe medicines
- Explain medical terms in simple language
- Explain every abnormal value separately
- Mention seriousness level if relevant
- Mention common lifestyle-related causes
- Mention healthy precautions
- Be educational and helpful
- Use clean formatting

Lab Findings:
{findings}

Medical Knowledge:
{context}

Medication Information:
{medication_context or "No medication information provided."}

Generate response in this format:

# Overall Summary

# Abnormal Findings Explained
Explain each abnormal value separately.

# Normal Findings
Briefly explain why normal results are good.

# Possible Health Meaning
Explain possible non-diagnostic meaning in simple words.

# General Health Suggestions
Provide safe lifestyle suggestions only.

# Important Disclaimer
Mention this is educational information only,
not medical advice.
"""

    return _generate_response(prompt)


# =========================
# GENERATE REPORT FEEDBACK
# =========================

def generate_report_feedback(
    report_text,
    findings="",
    context="",
    medication_context=""
):

    if not report_text.strip() and not findings.strip():
        return "No readable report text or lab values detected."

    prompt = f"""
You are an advanced AI medical lab report explanation assistant.

Your job is to explain medical lab reports in VERY SIMPLE,
DETAILED, HUMAN-FRIENDLY language.

IMPORTANT RULES:
- Do NOT diagnose diseases
- Do NOT prescribe medicines
- Do NOT scare the patient
- Explain like talking to a normal person
- Be educational and informative
- Elaborate properly
- Explain EVERY abnormal value separately
- Mention whether values are mildly, moderately, or severely abnormal
- Explain what each test means
- Explain common non-diagnostic reasons for abnormality
- Mention lifestyle-related causes when relevant
- Mention when medical attention may be important
- If something is normal, briefly explain why that's good
- Use clean formatting
- Use bullet points where needed
- Make the response comprehensive and useful

Extracted Lab Findings:
{findings or "No structured lab findings were detected."}

Retrieved Medical Knowledge:
{context or "No retrieved context was available."}

Medication Information:
{medication_context or "No medication information provided."}

Raw Report Text:
{report_text[:12000]}

Generate the response in this EXACT structure:

# Overall Health Summary
Provide a simple overview of the report.

# Detailed Test Explanation

For EACH abnormal parameter:
- What this test measures
- Whether it is high or low
- How abnormal it appears
- What it may commonly be associated with
- Common lifestyle-related causes
- Whether it usually requires urgent attention
- What symptoms people sometimes experience
- General precautions and healthy habits

For normal parameters:
- Briefly explain why the normal result is good

# Important Health Observations
Mention important overall patterns in the report.

# Lifestyle & General Health Suggestions
Give SAFE non-medication lifestyle suggestions only.

# When To Consult A Doctor
Mention situations where professional medical consultation is important.

# Final Note
Add a reassuring disclaimer that this is educational information,
not medical advice or diagnosis.
"""

    return _generate_response(prompt)


# =========================
# GENERATE DOCTOR QUESTIONS
# =========================

def generate_doctor_questions(
    findings,
    context="",
    medication_context=""
):

    if not findings.strip():
        return ""

    prompt = f"""
You are helping a patient prepare for a doctor consultation.

Based on the lab report findings,
medical knowledge, and medications,
generate useful questions.

IMPORTANT:
- Do NOT diagnose diseases
- Do NOT prescribe medicines
- Keep questions practical and helpful
- Avoid repeating questions
- Focus on abnormal findings
- Focus on medication concerns
- Use very simple language

Lab Findings:
{findings}

Medical Knowledge:
{context}

Medication Information:
{medication_context}

Generate:
- 5 to 10 useful patient-friendly questions
- Use bullet points
- Keep tone supportive and practical
"""

    return _generate_response(prompt)


# =========================
# SUMMARIZE MEDICATION INFO
# =========================

def summarize_medication_info(raw_medication_text):

    prompt = f"""
You are a medical assistant.

Summarize the medication information into concise,
patient-friendly sections.

Keep only the MOST IMPORTANT information.

Return ONLY valid JSON.

Format:
{{
    "purpose": "...",
    "usage": "...",
    "warnings": "...",
    "side_effects": "...",
    "dosage": "..."
}}

Rules:
- Keep responses concise
- Maximum 2-4 important points
- Avoid technical jargon
- Remove repetitive information
- Focus on patient safety
- Do NOT hallucinate
- Do NOT include markdown
- Do NOT include explanations outside JSON

Medication Information:
{raw_medication_text}
"""

    return _generate_response(prompt)