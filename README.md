# MediRag

MediRag is a simple lab report explanation app. It extracts lab values from a PDF, checks each value against its reference range, retrieves matching medical context from a FAISS index, and optionally generates a plain-language explanation with Gemini.

## Run the frontend

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Then upload a text-based lab report PDF in the browser.

## Gemini setup

Create a `.env` file with one of these keys:

```env
GEMINI_API_KEY=your_api_key_here
```

or:

```env
GOOGLE_API_KEY=your_api_key_here
```

You can turn off AI generation in the sidebar and still use PDF extraction, range checking, and retrieval.

## Files

- `app.py`: Streamlit frontend
- `lab_pipeline.py`: Shared analysis flow used by the frontend and CLI
- `pdf_extractor.py`: Extracts lab values from PDF text
- `range_checker.py`: Checks low, normal, high, or unknown status
- `retriever.py`: Loads FAISS index and retrieves medical knowledge
- `generator.py`: Calls Gemini to generate the final explanation
- `build_index.py`: Rebuilds `faiss_index.bin` and `stored_texts.json` from `data/medical_knowledge.json`
- `medication_api.py`: Fetches and summarizes medication information using OpenFDA and Gemini
- `medication_checker.py`: Processes medications, groups duplicates, and generates lab-related medication warnings

## Notes

The current extractor works best with text-based PDFs that show rows like `Test Name 12.3 unit 10.0 - 15.0`. Scanned PDFs need OCR before this app can read them.
