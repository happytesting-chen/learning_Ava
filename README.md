# Chinese Learning Web App for Kids

A kid-friendly Flask web application designed to help children practice Chinese vocabulary from their school worksheets.

## How It Works

1. **Upload a worksheet image** (PNG/JPG) — the homepage shows an upload form plus any previously saved units.
2. **OCR extraction** — EasyOCR scans the image for Chinese text, then the app parses two specific sections from the worksheet:
   - **口语表达词汇** (Spoken/Reading vocabulary)
   - **识读词语** (Practice/Writing vocabulary)
   
   Once the worksheet is loaded you can tap the “🖼 View Worksheet” button in practice mode to see the uploaded page full‑screen for easier reading. The file thumbnail and name are automatically hidden when you enter the practice section, giving the tracing area more room.
3. **Practice page** — displays the extracted vocabulary with two distinct modes:
   - **Reading mode** — uses only spoken vocab (口语表达词汇)
   - **Practice mode** — uses only practice vocab (识读词语)
4. **Save by unit** — if the image contains a unit header (e.g. 单元一 / Unit 1), the vocabulary is saved as a JSON file so it can be reloaded later without re-running OCR.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| OCR | EasyOCR (Chinese + English) |
| Frontend | HTML/CSS (Jinja2 templates, kid-friendly theme) |
| Storage | Local filesystem (`uploads/`, `saved_vocab/*.json`) |

## Key Files

| File | Role |
|---|---|
| `app.py` | Main Flask app — routes, OCR logic, vocabulary parsing |
| `templates/index.html` | Homepage with upload form + saved units list |
| `templates/practice.html` | Practice/reading interface |
| `saved_vocab/Unit_*.json` | Saved units with spoken + practice vocab |
| `PRD.md` | Product requirements document |
| `setup.sh` / `setup.bat` | Setup scripts for Linux/Windows |

## Project Structure

```
learning_Ava/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── PRD.md              # Product requirements
├── .gitignore
├── setup.sh            # Linux/Mac setup script
├── setup.bat           # Windows setup script
├── uploads/            # Uploaded worksheet images
│   └── .gitkeep
├── saved_vocab/        # Per-unit vocabulary JSON files
│   ├── Unit_1.json
│   └── Unit_2.json
├── templates/
│   ├── index.html      # Homepage with upload form
│   └── practice.html   # Practice/reading interface
└── static/
    └── style.css       # Styles
```

## Quick Start
> A **Back to Home** link/button is available on the practice page sidebar so you can easily return to the upload screen.
>
> ⚠️ If buttons seemed completely unresponsive, it was due to a JavaScript syntax error that prevented the script from loading. The code now avoids using the global `event` variable and the sidebar buttons pass `this` to `showSection`, and all braces have been corrected. Open the browser console to see logs when you click “Start Reading Mode” – you should see the phrase count or an alert if none were found.### Prerequisites

- Python 3.8+ with `python3-venv` (Ubuntu/Debian: `sudo apt install python3 python3-venv python3-pip`)

### One command to set up and run

```bash
bash setup.sh
```

This single command will:
1. Check Python is installed
2. Create a virtual environment
3. Install all dependencies
4. Start the app

Then open your browser at `http://localhost:8080`.

To run again after initial setup:
```bash
bash setup.sh
```

## File Requirements

- **Supported formats**: PNG, JPG, JPEG
- **Maximum file size**: 5MB
- **Best results**: Clear photos of Chinese worksheet pages with visible section headers (口语表达词汇 / 识读词语)

## OCR Pipeline

The vocabulary extraction in `app.py` uses a multi-strategy approach:

1. **Direct vocabulary-line detection** — finds lines with 3+ period-separated Chinese words
2. **Section-header detection** — locates 口语表达词汇 and 识读词语 headers by position, then assigns words to the correct section
3. **Fallback pattern matching** — used when headers are not clearly recognized

A small correction table fixes known OCR misreads (e.g. `眼晴` → `眼睛`).

## Security

- File type validation (extension + size)
- Secure filename handling via Werkzeug
- UUID-prefixed filenames to prevent collisions
- Path traversal protection on all file-serving routes

## Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
- Change the port in `app.py`: `app.run(port=8081)`

**OCR takes a long time on first run:**
- EasyOCR downloads its model on first use. Subsequent runs are faster as the model is cached.

---

*Made for Ava — happy learning!*