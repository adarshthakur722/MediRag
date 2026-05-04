import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency guard
    load_dotenv = None

try:
    from google import genai
except ImportError:  # pragma: no cover - handled at runtime
    genai = None


if load_dotenv:
    load_dotenv()


def _create_client():
    if genai is None:
        raise RuntimeError("Install google-genai before generating the AI report.")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file.")

    return genai.Client(api_key=api_key)


def _clean_api_error(error):
    message = str(error)

    if "API key not valid" in message or "API_KEY_INVALID" in message:
        return (
            "Gemini API key is invalid. Update GEMINI_API_KEY or GOOGLE_API_KEY "
            "in the .env file, then submit the report again."
        )

    if "quota" in message.lower():
        return "Gemini quota limit reached. Try again later or use another API key."

    if "permission" in message.lower() or "403" in message:
        return "Gemini API access is blocked for this key. Check API permissions in Google AI Studio."

    return "AI analysis failed. Check the API key and internet connection, then try again."


def generate_report(findings, context):
    if not findings.strip():
        return "No lab values detected."

    prompt = f"""
You are a medical lab report explanation assistant.

Lab Findings:
{findings}

Medical Knowledge:
{context}

Explain clearly:
- What is abnormal
- What it may indicate
- Whether it looks serious
- When to consult a doctor

If Lab Findings are empty, say "No lab values detected."

Add disclaimer that this is not medical advice.
"""

    try:
        client = _create_client()
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
        )
    except Exception as exc:
        raise RuntimeError(_clean_api_error(exc)) from exc

    return response.text


def generate_report_feedback(report_text, findings="", context=""):
    if not report_text.strip() and not findings.strip():
        return "No readable report text or lab values detected."

    prompt = f"""
You are a medical lab report explanation assistant.

Analyze the uploaded lab report and give clear patient-friendly feedback.

Extracted Lab Findings:
{findings or "No structured lab findings were detected."}

Retrieved Medical Knowledge:
{context or "No retrieved context was available."}

Raw Report Text:
{report_text[:12000]}

Give feedback in this structure:
1. Overall summary
2. Abnormal or concerning values
3. Values that look normal
4. Possible meaning in simple language
5. What to discuss with a doctor

Do not diagnose. Add a disclaimer that this is not medical advice.
"""

    try:
        client = _create_client()
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
        )
    except Exception as exc:
        raise RuntimeError(_clean_api_error(exc)) from exc

    return response.text
