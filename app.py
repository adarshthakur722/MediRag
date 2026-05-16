import tempfile
from pathlib import Path

import streamlit as st

from lab_pipeline import analyze_pdf, analyze_values
from pdf_extractor import parse_lab_text


st.set_page_config(
    page_title="MediRag Lab Report Assistant",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    .status-normal { color: #137333; font-weight: 700; }
    .status-low { color: #b06000; font-weight: 700; }
    .status-high { color: #b3261e; font-weight: 700; }
    .status-unknown { color: #5f6368; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def status_badge(status):
    safe_status = status if status in {"normal", "low", "high", "unknown"} else "unknown"
    return f'<span class="status-{safe_status}">{safe_status.upper()}</span>'


st.title("MediRag Lab Report Assistant")
st.caption(
    "Upload a text-based lab report PDF to extract values, compare ranges, "
    "retrieve medical context, and generate a patient-friendly explanation."
)

uploaded_pdfs = st.file_uploader(
    "Upload lab report PDFs",
    type=["pdf"],
    accept_multiple_files=True,
)

st.subheader("💊 Current Medications")

medication_input = st.text_area(
    "If you are currently taking any medications, enter them separated by commas. Leave blank if none.",
    placeholder="Example: Glycomet, Dolo 650, Atorvastatin",
    height=100,
)

if not uploaded_pdfs:
    st.info("Choose one or more PDF reports to begin.")
    st.stop()

submitted = st.button("Submit", type="primary")

medications = [
    med.strip()
    for med in medication_input.split(",")
    if med.strip()
]

if not submitted:
    st.info("Click Submit to analyze the uploaded reports.")
    st.stop()


def analyze_uploaded_pdf(uploaded_pdf, medications=None):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_pdf.getbuffer())
        temp_pdf_path = Path(temp_pdf.name)

    try:
        return analyze_pdf(
            temp_pdf_path,
            use_ai=True,
            medications=medications,
        )
    finally:
        temp_pdf_path.unlink(missing_ok=True)


def render_empty_result(result, label):
    if result["report_error"]:
        st.warning(result["report_error"])
    elif result["report"]:
        st.subheader("Report Analysis")
        st.markdown(result["report"])
    else:
        st.warning("No readable report text was found. Try a text-based PDF.")

    with st.expander("Paste lab values manually"):
        manual_text = st.text_area(
            "Lab values",
            placeholder="Hemoglobin 11.2 g/dL 13.0 - 17.0\nWBC 12000 cells/uL 4000 - 11000",
            height=140,
            key=f"manual-values-{label}",
        )

        if manual_text.strip():
            manual_values = parse_lab_text(manual_text)

            if not manual_values:
                st.error("Please enter values like: Hemoglobin 11.2 g/dL 13.0 - 17.0")

            else:
                with st.spinner("Preparing analysis..."):

                    manual_result = analyze_values(
                        manual_values,
                        use_ai=True,
                        medications=medications,
                    )

                if manual_result["report_error"]:
                    st.warning(manual_result["report_error"])
                else:
                    st.markdown(manual_result["report"])


def render_report_result(result, key_prefix):
    rows = result["rows"]

    (
        tab_results,
        tab_medications,
        tab_context,
        tab_report,
        tab_questions,
    ) = st.tabs(
        [
            "Results",
            "Medication Awareness",
            "Retrieved Context",
            "AI Explanation",
            "Questions For Doctor",
        ]
    )

    with tab_results:
        st.subheader("Extracted Lab Values")

        for row in rows:
            with st.container(border=True):
                left, middle, right = st.columns([2, 1, 1])

                left.markdown(f"**{row['test']}**")
                middle.write(f"{row['value']} {row['unit']}".strip())

                right.markdown(
                    status_badge(row["status"]),
                    unsafe_allow_html=True,
                )

                st.caption(f"Reference range: {row['reference_range']}")

                if row["retrieval_error"]:
                    st.warning(
                        f"Context retrieval issue: {row['retrieval_error']}"
                    )

        with st.expander("Raw findings text"):
            st.code(
                result["findings_text"] or "No findings.",
                language="text",
            )

    with tab_medications:

        st.subheader("Medication Awareness")

        medication_results = result.get(
            "medication_results",
            [],
        )

        if not medications:

            st.info(
                "No medications were provided."
            )

        elif not medication_results:

            st.warning(
                "Medication information could not be retrieved."
            )

        else:

            for med in medication_results:

                with st.container(border=True):

                    st.markdown(
                        f"### 💊 {', '.join(med.get('medications', []))}"
                    )
                    st.caption(f"Generic Name: {med.get('generic_name', 'Unknown').title()}")

                    st.markdown(
                        f"**Purpose:**\n\n{med.get('purpose', 'Not available')}"
                    )

                    st.markdown(
                        f"**Usage Information:**\n\n{med.get('usage', 'Not available')}"
                    )

                    st.markdown(
                        f"**Side Effects:**\n\n{med.get('side_effects', 'Not available')}"
                    )

                    st.markdown(
                        f"**Warnings:**\n\n{med.get('warnings', 'Not available')}"
                    )

                    st.markdown(
                        f"**Dosage Information:**\n\n{med.get('dosage', 'Not available')}"
                    )

                    lab_warnings = med.get(
                        "lab_warnings",
                        [],
                    )

                    if lab_warnings:

                        st.markdown(
                            "#### ⚠ Lab-Related Warnings"
                        )

                        for warning in lab_warnings:
                            st.error(warning)

    with tab_context:
        st.subheader("Medical Knowledge Used")

        if result["context_text"].strip():

            st.text_area(
                "Retrieved context",
                result["context_text"],
                height=360,
                key=f"context-{key_prefix}",
            )

        else:

            st.warning(
                "No context was retrieved. Make sure faiss_index.bin and stored_texts.json are present."
            )

    with tab_report:
        st.subheader("Generated Explanation")

        if result["report_error"]:

            st.warning(result["report_error"])
            st.caption("The extraction and retrieval steps still ran.")

        elif result["report"]:

            st.markdown(result["report"])

        else:

            st.info("No AI explanation was generated.")

    with tab_questions:

        st.subheader(
            "Questions You May Want To Ask Your Doctor"
        )

        questions = result.get(
            "doctor_questions",
            "",
        )

        if questions.strip():

            st.markdown(questions)

        else:

            st.info(
                "No doctor questions were generated."
            )


analysis_results = []

with st.spinner("Reading reports and preparing analysis..."):

    for uploaded_pdf in uploaded_pdfs:

        try:

            analysis_results.append(
                {
                    "name": uploaded_pdf.name,
                    "result": analyze_uploaded_pdf(
                        uploaded_pdf,
                        medications=medications,
                    ),
                    "error": None,
                }
            )

        except Exception as exc:

            analysis_results.append(
                {
                    "name": uploaded_pdf.name,
                    "result": None,
                    "error": str(exc),
                }
            )

all_rows = [
    row
    for item in analysis_results
    if item["result"]
    for row in item["result"]["rows"]
]

normal_count = sum(
    1
    for row in all_rows
    if row["status"] == "normal"
)

abnormal_count = sum(
    1
    for row in all_rows
    if row["status"] in {"low", "high"}
)

unknown_count = sum(
    1
    for row in all_rows
    if row["status"] == "unknown"
)

summary_cols = st.columns(5)

summary_cols[0].metric(
    "Files uploaded",
    len(uploaded_pdfs),
)

summary_cols[1].metric(
    "Tests found",
    len(all_rows),
)

summary_cols[2].metric(
    "Normal",
    normal_count,
)

summary_cols[3].metric(
    "Abnormal",
    abnormal_count,
)

summary_cols[4].metric(
    "Unknown",
    unknown_count,
)

for index, item in enumerate(analysis_results, start=1):

    report_name = item["name"]
    result = item["result"]

    with st.expander(
        f"{index}. {report_name}",
        expanded=len(analysis_results) == 1,
    ):

        if item["error"]:

            st.error(
                f"Could not analyze this file: {item['error']}"
            )

        elif not result["rows"]:

            render_empty_result(
                result,
                f"{index}-{report_name}",
            )

        else:

            render_report_result(
                result,
                f"{index}-{report_name}",
            )