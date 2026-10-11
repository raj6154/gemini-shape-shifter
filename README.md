# 🦎 Gemini Shape-Shifter ∞ — The Universal Engine

### *An Agentic Interface that re-writes itself in real-time based on ANY data you provide.*

Powered by **Gemini 2.0 Flash**, this application is a next-gen "Generative UI" platform supporting **9 input modalities** — CSV, PDF, Excel, JSON, TXT, Images, Video, Audio, and Camera.

---

## 🚀 Live Demo
**[Click Here to Launch App](https://gemini-shape-shiftertextsettings-gemini2dshape2dshifter-public.streamlit.app/)**

---

## 🧠 Features

### 1. 🦎 Universal Shape-Shifter
Upload **any** file and the engine auto-detects the type and adapts:
- **CSV** → Full data profiling, correlation heatmaps, distribution plots, AI-generated dashboards
- **Excel** → Multi-sheet support with per-sheet analysis
- **JSON** → Auto-normalize nested structures into tables
- **TXT** → Word/line/char stats + AI text analysis
- **Images** → Multimodal vision with 5 analysis modes (general, chart, UI/UX, OCR, objects)
- **Video** → Long-context video intelligence via Gemini File API

### 2. 📄 PDF Intelligence Reader *(NEW)*
A full-featured PDF reader:
- **Page-by-page navigation** with visual previews + text extraction side-by-side
- **Table extraction** → automatically finds and exports tables to CSV
- **Full-text search** across the entire document
- **AI Analysis modes**: Executive Summary, Key Points, Q&A, Data Extraction, Structure Analysis, Translation
- **Document metadata** display
- **Page thumbnail gallery**

### 3. 🤖 SQL Agent
- Natural language → SQL with context-aware schema detection
- Import any CSV directly into the SQLite database
- View/browse all database tables
- Auto-visualizes results

### 4. 📸 Live Camera Feed
- Capture → analyze with multiple vision modes
- OCR, object detection, chart reading, custom prompts

### 5. 🎙️ Voice Command
- Record → Transcribe → Execute
- Modes: Transcribe-only, SQL generation, Q&A, Translation

### 6. 💬 AI Chat
- Free-form conversation with data context awareness
- Persistent chat history within session
- Knows about your uploaded data for contextual answers

---

## ⚡ Architecture

```
┌──────────────────────────────────────────────┐
│           Gemini 2.0 Flash API               │
│     (Vision + Text + Audio + Video)          │
└──────────────┬───────────────────────────────┘
               │
┌──────────────▼───────────────────────────────┐
│          Shape-Shifter Engine                 │
│                                              │
│  ┌─────┐ ┌─────┐ ┌──────┐ ┌──────┐ ┌─────┐ │
│  │ CSV │ │ PDF │ │Excel │ │Image │ │Video│ │
│  └──┬──┘ └──┬──┘ └──┬───┘ └──┬───┘ └──┬──┘ │
│     │       │       │        │        │     │
│  ┌──▼───────▼───────▼────────▼────────▼──┐  │
│  │     Auto-Detection & Routing          │  │
│  └──────────────┬────────────────────────┘  │
│                 │                            │
│  ┌──────────────▼───────────────────────┐   │
│  │  Adaptive UI Generation (exec)       │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack
| Component | Technology |
|---|---|
| **AI Brain** | Google Gemini 2.0 Flash |
| **Frontend** | Streamlit |
| **PDF Engine** | PyMuPDF (fitz) |
| **Data** | Pandas, NumPy, SciPy |
| **Visualization** | Matplotlib, Seaborn, Pillow |
| **Database** | SQLite3 |
| **Excel** | openpyxl |

---

## 💿 Installation

```bash
# 1. Clone
git clone https://github.com/raj6154/gemini-shape-shifter.git
cd gemini-shape-shifter

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key (choose one)
export GEMINI_API_KEY="your-key-here"
# OR create .streamlit/secrets.toml:
# GEMINI_API_KEY = "your-key-here"

# 5. Run
streamlit run app.py
```

---

## 📁 Project Structure
```
gemini-shape-shifter/
├── app.py              ← Main application (900+ lines)
├── requirements.txt    ← Dependencies
├── data.csv            ← Sample dataset
├── make_image.py       ← Test chart generator
├── test_chart.png      ← Sample chart image
├── .gitignore
└── README.md
```

---

> **Shape-Shifter ∞** — Drop data, get intelligence. The engine adapts.
