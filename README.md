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

### Security

Do not commit API keys or other secrets to the repository.

The `.env` file should remain private and should be included in `.gitignore`.

## Team

### Team Neurals

- **Project:** MediRag
- **Project Type:** AI / Machine Learning / Generative AI
- **Core Technology:** Retrieval-Augmented Generation (RAG)

MediRag was developed as a collaborative academic project by Team Neurals.

## Disclaimer

MediRag is an educational and informational software project. It is not intended to diagnose diseases, prescribe medication, or replace consultation with a qualified healthcare professional. AI-generated explanations and retrieved information should be treated as supportive information and not as professional medical advice.
