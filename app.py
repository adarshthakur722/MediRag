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

if not uploaded_pdfs:
    st.info("Choose one or more PDF reports to begin.")
    st.stop()

submitted = st.button("Submit", type="primary")
if not submitted:
    st.info("Click Submit to analyze the uploaded reports.")
    st.stop()


def analyze_uploaded_pdf(uploaded_pdf):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_pdf.getbuffer())
        temp_pdf_path = Path(temp_pdf.name)

    try:
        return analyze_pdf(temp_pdf_path, use_ai=True)
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
                    manual_result = analyze_values(manual_values, use_ai=True)
                if manual_result["report_error"]:
                    st.warning(manual_result["report_error"])
                else:
                    st.markdown(manual_result["report"])


def render_report_result(result, key_prefix):
    rows = result["rows"]

    tab_results, tab_context, tab_report = st.tabs(
        ["Results", "Retrieved Context", "AI Explanation"]
    )

    with tab_results:
        st.subheader("Extracted Lab Values")
        for row in rows:
            with st.container(border=True):
                left, middle, right = st.columns([2, 1, 1])
                left.markdown(f"**{row['test']}**")
                middle.write(f"{row['value']} {row['unit']}".strip())
                right.markdown(status_badge(row["status"]), unsafe_allow_html=True)
                st.caption(f"Reference range: {row['reference_range']}")
                if row["retrieval_error"]:
                    st.warning(f"Context retrieval issue: {row['retrieval_error']}")

        with st.expander("Raw findings text"):
            st.code(result["findings_text"] or "No findings.", language="text")

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


analysis_results = []
with st.spinner("Reading reports and preparing analysis..."):
    for uploaded_pdf in uploaded_pdfs:
        try:
            analysis_results.append(
                {
                    "name": uploaded_pdf.name,
                    "result": analyze_uploaded_pdf(uploaded_pdf),
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
normal_count = sum(1 for row in all_rows if row["status"] == "normal")
abnormal_count = sum(1 for row in all_rows if row["status"] in {"low", "high"})
unknown_count = sum(1 for row in all_rows if row["status"] == "unknown")

summary_cols = st.columns(5)
summary_cols[0].metric("Files uploaded", len(uploaded_pdfs))
summary_cols[1].metric("Tests found", len(all_rows))
summary_cols[2].metric("Normal", normal_count)
summary_cols[3].metric("Abnormal", abnormal_count)
summary_cols[4].metric("Unknown", unknown_count)

for index, item in enumerate(analysis_results, start=1):
    report_name = item["name"]
    result = item["result"]

    with st.expander(f"{index}. {report_name}", expanded=len(analysis_results) == 1):
        if item["error"]:
            st.error(f"Could not analyze this file: {item['error']}")
        elif not result["rows"]:
            render_empty_result(result, f"{index}-{report_name}")
        else:
            render_report_result(result, f"{index}-{report_name}")
