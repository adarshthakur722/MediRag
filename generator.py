from google import genai
import os

# Use environment variable (recommended)
# client = genai.Client(api_key="")

def generate_report(findings, context):

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )


    return response.text
