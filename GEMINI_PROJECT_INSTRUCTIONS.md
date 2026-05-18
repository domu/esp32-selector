# Gemini AI Project Instructions

## 1) Project Purpose
This repository contains a **Streamlit web app** used to help users select the most suitable ESP32 chip/board family based on technical filters.

Main user goals:
- Compare ESP32 variants by features (CPU, wireless, peripherals, security, etc.).
- Get recommended boards by project type.
- Browse links/resources managed through JSON content.

---

## 2) Tech Stack
- Python
- Streamlit
- Pandas

Dependencies are listed in `requirements.txt`:
- `streamlit`
- `pandas`

---

## 3) Key Files
- `main.py`: Main Streamlit app (active entrypoint).
- `mainv11.py`: Older alternative version (reference only unless explicitly requested).
- `ESP32_Feature_Matrix_2026.csv`: Core feature matrix used for filtering and specs display.
- `ESP32-Feature-Matrix-2026.xlsx`: Spreadsheet source/version of the same dataset.
- `ESP32_Notes.csv`: Supplemental notes and context.
- `links_resources.json`: Data-driven content for the "Link & Risorse" page.

---

## 4) How the App Is Structured (`main.py`)
The app has 3 pages controlled by `st.session_state.current_page`:

1. `Selezione`
- Shows filter pills grouped by feature categories.
- Computes compatible boards from selected filters.
- Includes `RESET FILTRI` behavior.

2. `Consigli`
- Shows recommendation presets by project type.
- For each recommended board, expands technical specs pulled from CSV.

3. `Links`
- Reads sections/items from `links_resources.json`.
- Renders title/text/link entries.
- Detects YouTube URLs and shows a small thumbnail preview.

---

## 5) Data Model Expectations
### CSV (`ESP32_Feature_Matrix_2026.csv`)
Expected columns:
- `Feature Category`
- `Feature`
- One column per ESP32 model (e.g., `ESP32-S3`, `ESP32-C6`, etc.)

Normalization performed:
- Column names are cleaned (`\n` removed/trimmed).
- `Feature Category` forward-filled and trimmed.
- `Feature` trimmed.

### JSON (`links_resources.json`)
Expected format:
```json
{
  "sections": [
    {
      "title": "Section title",
      "items": [
        {
          "title": "Item title",
          "text": "Description",
          "url": "https://..."
        }
      ]
    }
  ]
}
```

---

## 6) Important Runtime Behaviors
- Filter widget keys include a reset counter to force full visual reset of pills.
- `perform_reset()` clears pill-related session keys and increments `reset_counter`.
- Compatibility check matches selected feature value against board column value.

---

## 7) How to Run Locally
From repository root:

```bash
pip install -r requirements.txt
streamlit run main.py
```

---

## 8) Safe Edit Zones
If asked to extend functionality, prefer these areas:
- Data loading functions (`load_data`, `load_links_data`).
- `Consigli` section for recommendation logic/spec rendering.
- `Links` section for JSON-driven presentation behavior.

Avoid breaking:
- CSV column cleaning logic.
- Session state keys for filters/reset.
- JSON schema expected by `links_resources.json`.

---

## 9) Suggested Improvement Backlog (Optional)
- Add schema validation for `links_resources.json`.
- Add caching (`@st.cache_data`) for CSV/JSON loading.
- Add unit tests for YouTube URL parsing and reset behavior.
- Move recommendation presets from code to JSON for non-code editing.

---

## 10) Quick Summary for Gemini
This is a **data-driven ESP32 selector app** in Streamlit:
- CSV powers technical comparison and specs.
- UI pages are Selezione / Consigli / Links.
- Links page content is editable via JSON.
- Main logic is centralized in `main.py`.
