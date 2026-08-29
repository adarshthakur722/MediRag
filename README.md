# MediRag

MediRag is an AI-powered web application designed to help users understand medical laboratory reports in simpler language. It extracts laboratory values from PDF reports, compares them with reference ranges, retrieves relevant medical context using a Retrieval-Augmented Generation (RAG) pipeline, and generates simplified explanations using Groq-based Generative AI.

The application also provides medication awareness, manual laboratory-value entry, a Doctor Question Generator, and downloadable PDF reports.

---

## Project Structure

```text
MediRag/
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── auth.py
├── build_index.py
├── database.py
├── generator.py
├── lab_pipeline.py
├── main.py
├── medication_api.py
├── medication_checker.py
├── pdf_export.py
├── pdf_extractor.py
├── range_checker.py
├── retriever.py
│
├── faiss_index.bin
├── medical_knowledge.json
├── stored_texts.json
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── users.db
```

---

## Important Files

| File | Description |
| --- | --- |
| `app.py` | Main Streamlit application and user interface. |
| `auth.py` | Handles user authentication. |
| `database.py` | Manages database operations and user data. |
| `lab_pipeline.py` | Coordinates the laboratory analysis workflow. |
| `pdf_extractor.py` | Extracts laboratory information from PDF reports. |
| `range_checker.py` | Compares laboratory values with reference ranges. |
| `retriever.py` | Performs RAG-based medical information retrieval using FAISS. |
| `generator.py` | Generates AI-based explanations using Groq. |
| `medication_api.py` | Retrieves medication information. |
| `medication_checker.py` | Handles medication-awareness functionality. |
| `pdf_export.py` | Generates downloadable PDF reports. |
| `build_index.py` | Builds the FAISS medical knowledge index. |
| `medical_knowledge.json` | Contains the medical knowledge used for retrieval. |
| `faiss_index.bin` | Stores the FAISS vector index. |
| `requirements.txt` | Lists the required Python dependencies. |

---

## Installation

### Clone the repository:

```powershell
git clone https://github.com/adarshthakur722/MediRag.git
cd MediRag
```

### Create a Virtual Environment:

- Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

- Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Run the frontend

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Then upload a text-based lab report PDF in the browser.

### Gemini setup

Create a `.env` file with one of these keys:

```env
GROQ_API_KEY="your_api_key_here"
```

You can turn off AI generation in the sidebar and still use PDF extraction, range checking, and retrieval.

#### Important

Do not commit API keys or other secrets to the repository.

The `.env` file should remain private and should be included in `.gitignore`.

## Using MediRag

### Step 1 — Login

Create an account or log in using the authentication interface.

### Step 2 — Upload Laboratory Report

Upload one or more laboratory report PDFs.

### Step 3 — Enter Medications

Optionally enter currently used medications, separated by commas.

Example:

```text
Glycomet, Dolo 650, Atorvastatin
```

### Step 4 — Submit the Report

MediRag extracts the laboratory values and compares them with their reference ranges.

### Step 5 — View Analysis

The application displays:

- Laboratory values
- Reference ranges
- Classification status
- Relevant medical information
- AI-generated explanations

### Step 6 — Review Medication Awareness

If medications were entered, MediRag retrieves available medication information and incorporates relevant medication-related observations.

### Step 7 — Generate Doctor Questions

The application can generate questions that may be discussed with a healthcare professional.

### Step 8 — Download the Report

The completed analysis can be exported as a downloadable PDF report.

## Limitations

MediRag is a student-developed prototype and has several limitations:

- The application is intended for educational and informational purposes.
- It should not be used as a substitute for professional medical advice.
- The current PDF extraction works best with text-based laboratory reports.
- Scanned documents may require OCR before processing.
- Medical information retrieved from external sources may be incomplete or unavailable.
- AI-generated explanations may contain errors and should be verified by a qualified healthcare professional.
- Medication information depends on the availability and quality of the external medication data source.
- The system should not be used for autonomous diagnosis or treatment decisions.

## Future Enhancements

Potential future improvements include:

- OCR support for scanned laboratory reports.
- Support for additional laboratory-report formats.
- Improved laboratory test-name normalization.
- Expanded medical knowledge sources.
- More comprehensive medication interaction detection.
- Improved multilingual support.
- More advanced retrieval and ranking techniques.
- Enhanced evaluation using larger and more diverse test datasets.
- Improved deployment scalability and monitoring.
- Integration with additional trusted medical information sources.

## Team

### Team Neurals

- **Project:** MediRag
- **Project Type:** AI / Machine Learning / Generative AI
- **Core Technology:** Retrieval-Augmented Generation (RAG)

MediRag was developed as a collaborative academic project by Team Neurals.

## Disclaimer

MediRag is an educational and informational software project. It is not intended to diagnose diseases, prescribe medication, or replace consultation with a qualified healthcare professional. AI-generated explanations and retrieved information should be treated as supportive information and not as professional medical advice.
