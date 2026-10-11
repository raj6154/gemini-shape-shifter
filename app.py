import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io
import sqlite3
import time
import numpy as np
import os
import requests
import json
import base64
import hashlib
from datetime import datetime

# --- PDF support ---
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Gemini Shape-Shifter ∞",
    page_icon="🦎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# ═══════════════════════════════════════════════════════════════════════════════
# 2. CYBERPUNK STYLING — GLASSMORPHISM + ANIMATED GRADIENTS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* === IMPORTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* === HIDE DEFAULTS === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent;
        backdrop-filter: none;
    }

    /* === ROOT VARIABLES === */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: rgba(18, 18, 26, 0.7);
        --accent-cyan: #00f0ff;
        --accent-magenta: #ff00e5;
        --accent-purple: #8b5cf6;
        --accent-green: #00ff88;
        --accent-orange: #ff6b35;
        --text-primary: #e8e8f0;
        --text-muted: #8888aa;
        --glass-bg: rgba(255, 255, 255, 0.04);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glow-cyan: 0 0 20px rgba(0, 240, 255, 0.3);
        --glow-magenta: 0 0 20px rgba(255, 0, 229, 0.3);
    }

    /* === MAIN BACKGROUND === */
    .stApp {
        background: var(--bg-primary);
        background-image:
            radial-gradient(ellipse at 10% 20%, rgba(0, 240, 255, 0.05) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 80%, rgba(255, 0, 229, 0.05) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(139, 92, 246, 0.03) 0%, transparent 50%);
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d15 0%, #0a0a12 100%);
        border-right: 1px solid var(--glass-border);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }

    /* === GLASSMORPHISM CARDS === */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        border-color: rgba(0, 240, 255, 0.2);
        box-shadow: var(--glow-cyan);
        transform: translateY(-2px);
    }

    /* === HERO TITLE === */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-magenta), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
        animation: gradient-shift 4s ease infinite;
        background-size: 200% 200%;
        margin-bottom: 0;
        line-height: 1.1;
    }
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: var(--text-muted);
        font-weight: 400;
        margin-top: 8px;
        letter-spacing: 0.02em;
    }

    /* === STATUS BADGE === */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.05em;
    }
    .status-online {
        background: rgba(0, 255, 136, 0.12);
        color: var(--accent-green);
        border: 1px solid rgba(0, 255, 136, 0.2);
    }
    .status-offline {
        background: rgba(255, 70, 70, 0.12);
        color: #ff4646;
        border: 1px solid rgba(255, 70, 70, 0.2);
    }

    /* === METRIC CARDS === */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }
    .metric-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.15);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
    }

    /* === FEATURE TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid var(--glass-border);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--text-muted);
        font-weight: 500;
        font-size: 0.85rem;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(139, 92, 246, 0.15));
        color: var(--accent-cyan) !important;
        border-bottom: none !important;
    }

    /* === BUTTONS === */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(139, 92, 246, 0.15));
        color: var(--accent-cyan);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-radius: 10px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        padding: 10px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.02em;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.25), rgba(139, 92, 246, 0.25));
        border-color: var(--accent-cyan);
        box-shadow: var(--glow-cyan);
        transform: translateY(-1px);
    }

    /* === FILE UPLOADER === */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(0, 240, 255, 0.15);
        border-radius: 16px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 240, 255, 0.3);
        background: rgba(0, 240, 255, 0.02);
    }

    /* === DATA TABLES === */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--glass-border);
    }

    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 10px;
        font-weight: 500;
    }

    /* === CODE BLOCKS === */
    .stCode {
        border-radius: 12px;
        border: 1px solid var(--glass-border);
    }

    /* === DIVIDER === */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.2), rgba(255, 0, 229, 0.2), transparent);
        margin: 32px 0;
    }

    /* === PULSE ANIMATION === */
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    .pulse { animation: pulse-glow 2s ease-in-out infinite; }

    /* === FEATURE HEADER === */
    .feature-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    .feature-icon {
        font-size: 1.8rem;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .feature-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* === SYSTEM STATUS PANEL === */
    .sys-panel {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 240, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        line-height: 1.8;
        margin: 12px 0;
    }
    .sys-panel .label {
        color: var(--text-muted);
    }
    .sys-panel .value {
        color: var(--accent-cyan);
        font-weight: 600;
    }

    /* === PDF PAGE GRID === */
    .pdf-page-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
        margin: 16px 0;
    }

    /* === CHAT BUBBLE === */
    .chat-user {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(0, 240, 255, 0.1));
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-ai {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px 16px 16px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 240, 255, 0.2);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 240, 255, 0.4);
    }

    /* === INPUT FIELDS === */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: rgba(0, 240, 255, 0.3) !important;
        box-shadow: 0 0 0 1px rgba(0, 240, 255, 0.1) !important;
    }

    /* === SELECT BOX === */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_gemini_model():
    """Return configured Gemini model."""
    return genai.GenerativeModel("gemini-2.0-flash")


def safe_exec_code(code: str, local_vars: dict) -> bool:
    """Safely execute Gemini-generated code."""
    code = code.replace("```python", "").replace("```", "").strip()
    # Remove common problematic imports that are already available
    lines = code.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("import streamlit") or stripped.startswith("from streamlit"):
            continue
        if stripped.startswith("import pandas") or stripped.startswith("from pandas"):
            continue
        if stripped.startswith("df = pd.read_csv") or stripped.startswith("df = pd.read"):
            continue
        cleaned.append(line)
    code = "\n".join(cleaned)
    try:
        exec(code, local_vars)
        return True
    except Exception as e:
        st.error(f"⚠️ Code Execution Error: {e}")
        st.code(code, language="python")
        return False


def extract_pdf_text(pdf_file) -> tuple:
    """Extract text and metadata from a PDF file. Returns (pages_text, num_pages, metadata)."""
    if not PDF_AVAILABLE:
        return [], 0, {}
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages_text.append(text)
    metadata = doc.metadata
    num_pages = len(doc)
    doc.close()
    return pages_text, num_pages, metadata


def extract_pdf_tables(pdf_file) -> list:
    """Extract tables from PDF using PyMuPDF's built-in table finder."""
    if not PDF_AVAILABLE:
        return []
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_tables = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        try:
            tabs = page.find_tables()
            for tab in tabs:
                table_data = tab.extract()
                if table_data and len(table_data) > 1:
                    headers = table_data[0]
                    rows = table_data[1:]
                    # Clean None values
                    headers = [h if h else f"Col_{i}" for i, h in enumerate(headers)]
                    df = pd.DataFrame(rows, columns=headers)
                    all_tables.append({"page": page_num + 1, "dataframe": df})
        except Exception:
            pass
    doc.close()
    return all_tables


def render_pdf_page_preview(pdf_file, page_num: int, zoom: float = 2.0):
    """Render a single PDF page as an image."""
    if not PDF_AVAILABLE:
        return None
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if page_num >= len(doc):
        doc.close()
        return None
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def generate_data_profile(df: pd.DataFrame) -> dict:
    """Generate a comprehensive data profile for a DataFrame."""
    profile = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "null_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3),
    }
    # Numeric stats
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        profile["numeric_stats"] = df[numeric_cols].describe().round(2).to_dict()
    # Categorical stats
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        profile["categorical_stats"] = {
            col: {
                "unique": df[col].nunique(),
                "top": df[col].mode().iloc[0] if not df[col].mode().empty else "N/A",
                "freq": df[col].value_counts().iloc[0] if not df[col].value_counts().empty else 0,
            }
            for col in cat_cols
        }
    return profile


def render_correlation_heatmap(df: pd.DataFrame):
    """Render a correlation heatmap for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        st.info("Need at least 2 numeric columns for correlation analysis.")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#0a0a0f")
    ax.set_facecolor("#0a0a0f")
    corr = numeric_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(
        corr, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
        square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
        annot=True, fmt=".2f", ax=ax,
        annot_kws={"color": "white", "fontsize": 8}
    )
    ax.tick_params(colors="white", labelsize=8)
    ax.set_title("Correlation Matrix", color="white", fontsize=14, pad=16)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def render_distribution_plots(df: pd.DataFrame):
    """Render distribution plots for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        st.info("No numeric columns found for distribution analysis.")
        return
    cols_to_plot = numeric_cols[:6]  # Max 6 plots
    n_cols = min(3, len(cols_to_plot))
    n_rows = (len(cols_to_plot) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    fig.patch.set_facecolor("#0a0a0f")
    if n_rows * n_cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    colors = ["#00f0ff", "#ff00e5", "#8b5cf6", "#00ff88", "#ff6b35", "#ffd700"]
    for i, col in enumerate(cols_to_plot):
        ax = axes[i]
        ax.set_facecolor("#12121a")
        ax.hist(df[col].dropna(), bins=20, color=colors[i % len(colors)], alpha=0.7, edgecolor="#1a1a2e")
        ax.set_title(col, color="white", fontsize=10, pad=8)
        ax.tick_params(colors="white", labelsize=7)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#333")
        ax.spines["bottom"].set_color("#333")
    # Hide unused axes
    for j in range(len(cols_to_plot), len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("Column Distributions", color="white", fontsize=14, y=1.02)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. API KEY & SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

# Safe Key Retrieval
try:
    DEFAULT_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center; padding: 12px 0;">
        <div style="font-size: 2.4rem; font-weight: 900;
             background: linear-gradient(135deg, #00f0ff, #ff00e5);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🦎 SHAPE-SHIFTER
        </div>
        <div style="font-size: 0.7rem; color: #8888aa; letter-spacing: 0.15em; margin-top: 4px;">
            GEMINI-POWERED UNIVERSAL ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API Key
    api_key = st.text_input(
        "🔐 API Key", value=DEFAULT_API_KEY, type="password",
        help="Enter your Google Gemini API key"
    )

    # Configure Gemini
    api_status = "OFFLINE"
    api_status_class = "status-offline"
    try:
        if api_key:
            genai.configure(api_key=api_key)
            api_status = "ONLINE"
            api_status_class = "status-online"
    except Exception:
        pass

    # System Status
    st.markdown(f"""
    <div class="sys-panel">
        <span class="label">STATUS</span>
        <span class="{api_status_class} status-badge" style="float:right">{api_status}</span><br>
        <span class="label">MODEL &nbsp;</span>
        <span class="value">Gemini 2.0 Flash</span><br>
        <span class="label">ENGINE</span>
        <span class="value">Shape-Shifter ∞</span><br>
        <span class="label">PDF &nbsp;&nbsp;</span>
        <span class="value">{"READY ✓" if PDF_AVAILABLE else "INSTALL PyMuPDF"}</span><br>
        <span class="label">EXCEL </span>
        <span class="value">{"READY ✓" if EXCEL_AVAILABLE else "INSTALL openpyxl"}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # === JUDGE'S TOOLKIT ===
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 700; color: #8b5cf6;
         letter-spacing: 0.08em; margin-bottom: 8px;">
        🛠️ JUDGE'S TOOLKIT
    </div>
    """, unsafe_allow_html=True)

    # Sample CSV
    sample_data = pd.DataFrame({
        "Date": pd.date_range("2025-01-01", periods=20, freq="D").strftime("%Y-%m-%d"),
        "Region": ["North", "South", "East", "West"] * 5,
        "Product": ["Gemini Pro", "Cloud Storage", "AI Consulting", "Hardware", "Software"] * 4,
        "Sales": np.random.randint(500, 6000, 20),
        "Profit": np.random.randint(100, 1600, 20),
        "Rating": np.round(np.random.uniform(3.5, 5.0, 20), 1),
    })
    csv_bytes = sample_data.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Test CSV", csv_bytes, "sample_data.csv", "text/csv")

    # Sample Chart Image
    img_chart = Image.new("RGB", (400, 300), color=(10, 10, 15))
    d = ImageDraw.Draw(img_chart)
    d.rectangle([50, 100, 100, 250], fill="#00f0ff")
    d.rectangle([120, 130, 170, 250], fill="#8b5cf6")
    d.rectangle([190, 80, 240, 250], fill="#ff00e5")
    d.rectangle([260, 150, 310, 250], fill="#00ff88")
    d.text((100, 30), "QUARTERLY REVENUE", fill="white")
    buf_chart = io.BytesIO()
    img_chart.save(buf_chart, format="PNG")
    st.download_button("📊 Download Test Chart", buf_chart.getvalue(), "test_chart.png", "image/png")

    # Sample UI Sketch
    img_ui = Image.new("RGB", (400, 300), color=(255, 255, 255))
    d_ui = ImageDraw.Draw(img_ui)
    d_ui.rectangle([0, 0, 400, 50], fill="#1a1a2e")
    d_ui.text((16, 16), "LOGO", fill="white")
    d_ui.text((300, 16), "NAV | LINKS", fill="#aaa")
    d_ui.rectangle([10, 60, 120, 290], outline="#ccc", width=2)
    d_ui.text((20, 80), "Dashboard", fill="#333")
    d_ui.text((20, 110), "Analytics", fill="#333")
    d_ui.text((20, 140), "Settings", fill="#333")
    d_ui.rectangle([130, 60, 390, 170], outline="#00f0ff", width=2)
    d_ui.text((140, 70), "Hero Section / KPI Cards", fill="#333")
    d_ui.rectangle([130, 180, 255, 290], outline="#8b5cf6", width=2)
    d_ui.text((140, 190), "Chart Area", fill="#333")
    d_ui.rectangle([265, 180, 390, 290], outline="#ff00e5", width=2)
    d_ui.text((275, 190), "Data Table", fill="#333")
    buf_ui = io.BytesIO()
    img_ui.save(buf_ui, format="PNG")
    st.download_button("📝 Download UI Sketch", buf_ui.getvalue(), "ui_sketch.png", "image/png")

    # Video Download
    st.markdown("---")
    if st.button("🎬 Fetch Test Video"):
        with st.spinner("Downloading..."):
            try:
                url = "https://www.w3schools.com/html/mov_bbb.mp4"
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    st.download_button("📥 Download MP4", resp.content, "test_video.mp4", "video/mp4")
                    st.success("Ready!")
                else:
                    st.error("Fetch failed.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Session Info
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 0.65rem; color: #555; font-family: 'JetBrains Mono', monospace;">
        SESSION {hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()}<br>
        ANALYSES: {len(st.session_state.analysis_results)}<br>
        CHAT MSGS: {len(st.session_state.chat_history)}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. HERO HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="padding: 20px 0 8px 0;">
    <div class="hero-title">Shape-Shifter ∞</div>
    <div class="hero-subtitle">
        Drop any file — CSV, PDF, Excel, JSON, images, or video — and the engine adapts.
        Powered by Gemini 2.0 Flash.
    </div>
</div>
""", unsafe_allow_html=True)

# Feature count badges
supported = ["CSV", "PDF", "Excel", "JSON", "TXT", "Images", "Video", "Audio", "Camera"]
st.markdown(f"""
<div style="display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 24px 0;">
    {"".join(f'<span style="background: rgba(0,240,255,0.08); border: 1px solid rgba(0,240,255,0.15); border-radius: 6px; padding: 3px 10px; font-size: 0.7rem; color: #00f0ff; font-weight: 500;">{s}</span>' for s in supported)}
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MAIN FEATURE TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab_shifter, tab_pdf, tab_sql, tab_camera, tab_voice, tab_chat = st.tabs([
    "🦎 Shape-Shifter",
    "📄 PDF Reader",
    "🤖 SQL Agent",
    "📸 Live Feed",
    "🎙️ Voice",
    "💬 Chat"
])


# ──────────────────────────────────────────────────────────────────────────────
# TAB 1: UNIVERSAL SHAPE-SHIFTER
# ──────────────────────────────────────────────────────────────────────────────
with tab_shifter:
    st.markdown("""
    <div class="feature-header">
        <div class="feature-icon">🦎</div>
        <div>
            <div class="feature-title">Universal Shape-Shifter</div>
            <div class="feature-desc">Upload CSV, Excel, JSON, TXT, Images, or Video — the engine auto-detects and adapts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    file_types = ["csv", "xlsx", "xls", "json", "txt", "png", "jpg", "jpeg", "webp", "mp4", "mov", "avi"]
    universal_file = st.file_uploader(
        "Drop your file here", type=file_types,
        help="Supports: CSV, Excel, JSON, TXT, Images (PNG/JPG/WEBP), Video (MP4/MOV/AVI)",
        key="universal_uploader"
    )

    if universal_file:
        fname = universal_file.name.lower()

        # ── DATA MODE: CSV ──
        if fname.endswith(".csv"):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**📂 Data File:** `{universal_file.name}`")
            df = pd.read_csv(universal_file)
            st.session_state.uploaded_data = df

            # Quick metrics
            profile = generate_data_profile(df)
            rows, cols = profile["shape"]
            null_total = sum(profile["null_counts"].values())
            numeric_count = len(df.select_dtypes(include=[np.number]).columns)

            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">{rows:,}</div>
                    <div class="metric-label">Rows</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cols}</div>
                    <div class="metric-label">Columns</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{numeric_count}</div>
                    <div class="metric-label">Numeric</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{null_total}</div>
                    <div class="metric-label">Nulls</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{profile['memory_mb']}</div>
                    <div class="metric-label">MB</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Data preview tabs
            data_tab1, data_tab2, data_tab3, data_tab4, data_tab5 = st.tabs([
                "📋 Preview", "📊 Statistics", "🔗 Correlations", "📈 Distributions", "🧮 Profile"
            ])

            with data_tab1:
                n_preview = st.slider("Preview rows", 5, min(100, len(df)), 10, key="csv_preview_rows")
                st.dataframe(df.head(n_preview), use_container_width=True)

            with data_tab2:
                st.dataframe(df.describe().round(2), use_container_width=True)
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                if cat_cols:
                    st.markdown("**Categorical Columns:**")
                    for col in cat_cols:
                        with st.expander(f"📂 {col} — {df[col].nunique()} unique values"):
                            st.dataframe(
                                df[col].value_counts().reset_index().rename(
                                    columns={"index": col, col: "Count"}
                                ).head(20),
                                use_container_width=True
                            )

            with data_tab3:
                render_correlation_heatmap(df)

            with data_tab4:
                render_distribution_plots(df)

            with data_tab5:
                st.json(profile)

            # AI Dashboard Generation
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            col_gen1, col_gen2 = st.columns([3, 1])
            with col_gen1:
                custom_prompt = st.text_input(
                    "Custom instruction (optional)",
                    placeholder="e.g., 'Focus on regional trends' or 'Show top products by profit'",
                    key="csv_custom_prompt"
                )
            with col_gen2:
                st.markdown("<br>", unsafe_allow_html=True)
                generate_btn = st.button("🚀 Generate AI Dashboard", key="btn_csv_gen", use_container_width=True)

            if generate_btn:
                with st.spinner("🧠 Gemini is analyzing your data and writing code..."):
                    model = get_gemini_model()
                    extra = f"\nUser's custom instruction: {custom_prompt}" if custom_prompt else ""
                    prompt = f"""You are a Python Data Visualization Expert.
The dataframe 'df' is already loaded with columns: {list(df.columns)}.
Column types: {df.dtypes.astype(str).to_dict()}.
Sample data (first 3 rows): {df.head(3).to_dict()}

Write Python code using Streamlit (st) and Seaborn/Matplotlib to create a BEAUTIFUL dashboard with:
1. At least 3 different visualizations (bar, line, pie, scatter, heatmap, etc.)
2. Use dark theme: fig.patch.set_facecolor('#0a0a0f'), ax.set_facecolor('#12121a')
3. Use these colors: #00f0ff, #ff00e5, #8b5cf6, #00ff88, #ff6b35
4. Add st.columns() for layout
5. Add st.metric() cards for key insights

DO NOT import pandas or streamlit. Assume 'df', 'st', 'sns', 'plt', 'np' are available.
Return ONLY executable Python code. No markdown, no explanations.{extra}"""
                    try:
                        response = model.generate_content(prompt)
                        code = response.text
                        st.session_state.analysis_results.append({
                            "type": "csv_dashboard",
                            "file": universal_file.name,
                            "time": datetime.now().isoformat(),
                        })
                        with st.expander("📜 View Generated Code", expanded=False):
                            st.code(code.replace("```python", "").replace("```", ""), language="python")
                        safe_exec_code(code, {
                            "df": df, "st": st, "pd": pd, "sns": sns,
                            "plt": plt, "np": np, "io": io
                        })
                    except Exception as e:
                        st.error(f"Generation Error: {e}")

        # ── DATA MODE: EXCEL ──
        elif fname.endswith((".xlsx", ".xls")):
            if not EXCEL_AVAILABLE:
                st.error("⚠️ Install `openpyxl` for Excel support: `pip install openpyxl`")
            else:
                st.markdown(f"**📗 Excel File:** `{universal_file.name}`")
                xls = pd.ExcelFile(universal_file)
                sheet_names = xls.sheet_names
                st.info(f"Found {len(sheet_names)} sheet(s): {', '.join(sheet_names)}")

                selected_sheet = st.selectbox("Select Sheet", sheet_names)
                df = pd.read_excel(universal_file, sheet_name=selected_sheet)
                st.session_state.uploaded_data = df

                profile = generate_data_profile(df)
                rows, cols = profile["shape"]
                st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-card"><div class="metric-value">{rows:,}</div><div class="metric-label">Rows</div></div>
                    <div class="metric-card"><div class="metric-value">{cols}</div><div class="metric-label">Columns</div></div>
                    <div class="metric-card"><div class="metric-value">{len(sheet_names)}</div><div class="metric-label">Sheets</div></div>
                </div>
                """, unsafe_allow_html=True)

                st.dataframe(df.head(20), use_container_width=True)

                if st.button("🚀 Generate Dashboard from Excel", key="btn_excel"):
                    with st.spinner("Generating..."):
                        model = get_gemini_model()
                        prompt = f"""You are a Python Data Visualization Expert.
The dataframe 'df' has columns: {list(df.columns)}, dtypes: {df.dtypes.astype(str).to_dict()}.
Sample: {df.head(3).to_dict()}
Create a beautiful dark-themed dashboard with 3+ charts.
Use colors: #00f0ff, #ff00e5, #8b5cf6, #00ff88.
DO NOT import pandas or streamlit. Return ONLY code."""
                        try:
                            response = model.generate_content(prompt)
                            safe_exec_code(response.text, {
                                "df": df, "st": st, "pd": pd, "sns": sns,
                                "plt": plt, "np": np
                            })
                        except Exception as e:
                            st.error(f"Error: {e}")

        # ── DATA MODE: JSON ──
        elif fname.endswith(".json"):
            st.markdown(f"**📦 JSON File:** `{universal_file.name}`")
            try:
                raw = json.load(universal_file)
                if isinstance(raw, list):
                    df = pd.json_normalize(raw)
                    st.session_state.uploaded_data = df
                    st.dataframe(df.head(20), use_container_width=True)
                    st.info(f"Parsed {len(df)} records with {len(df.columns)} fields.")
                    if st.button("🚀 Analyze JSON Data", key="btn_json"):
                        with st.spinner("Generating..."):
                            model = get_gemini_model()
                            prompt = f"""Analyze this JSON data loaded into a dataframe 'df'.
Columns: {list(df.columns)}, Sample: {df.head(3).to_dict()}.
Create visualizations. DO NOT import pandas/streamlit. Return ONLY code."""
                            try:
                                response = model.generate_content(prompt)
                                safe_exec_code(response.text, {
                                    "df": df, "st": st, "pd": pd, "sns": sns,
                                    "plt": plt, "np": np
                                })
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.json(raw)
                    if st.button("🧠 Analyze JSON Structure", key="btn_json_struct"):
                        with st.spinner("Analyzing..."):
                            model = get_gemini_model()
                            truncated = json.dumps(raw)[:4000]
                            response = model.generate_content(
                                f"Analyze this JSON structure and provide insights:\n{truncated}"
                            )
                            st.markdown(response.text)
            except Exception as e:
                st.error(f"JSON Parse Error: {e}")

        # ── DATA MODE: TXT ──
        elif fname.endswith(".txt"):
            st.markdown(f"**📝 Text File:** `{universal_file.name}`")
            text_content = universal_file.read().decode("utf-8", errors="replace")
            word_count = len(text_content.split())
            line_count = text_content.count("\n") + 1
            char_count = len(text_content)

            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-card"><div class="metric-value">{word_count:,}</div><div class="metric-label">Words</div></div>
                <div class="metric-card"><div class="metric-value">{line_count:,}</div><div class="metric-label">Lines</div></div>
                <div class="metric-card"><div class="metric-value">{char_count:,}</div><div class="metric-label">Characters</div></div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📄 View Content", expanded=True):
                st.text(text_content[:5000])
                if len(text_content) > 5000:
                    st.caption(f"Showing first 5000 of {len(text_content)} characters...")

            if st.button("🧠 Analyze Text with Gemini", key="btn_txt"):
                with st.spinner("Analyzing..."):
                    model = get_gemini_model()
                    truncated = text_content[:8000]
                    response = model.generate_content(
                        f"Analyze this text. Provide: 1) Summary 2) Key themes 3) Sentiment 4) Notable entities:\n\n{truncated}"
                    )
                    st.markdown(response.text)

        # ── VISION MODE: Images ──
        elif fname.endswith((".png", ".jpg", ".jpeg", ".webp")):
            st.markdown(f"**👁️ Image File:** `{universal_file.name}`")
            image = Image.open(universal_file)
            col_img1, col_img2 = st.columns([2, 1])
            with col_img1:
                st.image(image, caption="Visual Data Acquired", use_container_width=True)
            with col_img2:
                st.markdown(f"""
                <div class="glass-card">
                    <strong>Image Info</strong><br><br>
                    <span style="color: #8888aa;">Size:</span> {image.size[0]} × {image.size[1]}<br>
                    <span style="color: #8888aa;">Mode:</span> {image.mode}<br>
                    <span style="color: #8888aa;">Format:</span> {image.format or 'N/A'}<br>
                </div>
                """, unsafe_allow_html=True)

            analysis_type = st.selectbox("Analysis Type", [
                "🔍 General Analysis",
                "📊 Chart/Data Extraction",
                "🎨 UI/UX Review",
                "📝 OCR — Extract Text",
                "🏷️ Object Detection",
                "💡 Custom Prompt",
            ], key="img_analysis_type")

            prompts_map = {
                "🔍 General Analysis": "Analyze this image comprehensively. Describe what you see, identify key elements, and provide insights.",
                "📊 Chart/Data Extraction": "This is a chart or data visualization. Extract all data points, identify trends, and explain the visualization in detail.",
                "🎨 UI/UX Review": "This is a UI design or wireframe. Review the layout, identify components, suggest improvements, and describe the HTML/CSS/JS needed to build it.",
                "📝 OCR — Extract Text": "Extract ALL text visible in this image. Preserve formatting and structure as much as possible.",
                "🏷️ Object Detection": "Identify and list every object, person, text, and element visible in this image with their approximate locations.",
            }

            custom_img_prompt = ""
            if analysis_type == "💡 Custom Prompt":
                custom_img_prompt = st.text_area("Enter your analysis prompt", key="custom_img_prompt")

            if st.button("⚡ Run Vision Analysis", key="btn_vis"):
                with st.spinner("Gemini Vision is scanning..."):
                    model = get_gemini_model()
                    prompt = custom_img_prompt if analysis_type == "💡 Custom Prompt" else prompts_map[analysis_type]
                    try:
                        response = model.generate_content([prompt, image])
                        st.markdown(response.text)
                        st.session_state.analysis_results.append({
                            "type": "vision",
                            "file": universal_file.name,
                            "analysis": analysis_type,
                            "time": datetime.now().isoformat(),
                        })
                    except Exception as e:
                        st.error(f"Vision Error: {e}")

        # ── VIDEO MODE ──
        elif fname.endswith((".mp4", ".mov", ".avi")):
            st.markdown(f"**🎥 Video File:** `{universal_file.name}`")
            st.video(universal_file)

            video_prompt = st.text_input(
                "Custom video analysis prompt (optional)",
                placeholder="e.g., 'Count the number of people' or 'Describe the action sequence'",
                key="video_prompt"
            )

            if st.button("🎬 Analyze Video Intelligence", key="btn_video"):
                with st.spinner("Uploading & processing video via Gemini long context..."):
                    try:
                        with open("temp_video.mp4", "wb") as f:
                            f.write(universal_file.read())
                        video_file = genai.upload_file(path="temp_video.mp4")
                        progress = st.progress(0, text="Processing video...")
                        elapsed = 0
                        while video_file.state.name == "PROCESSING":
                            time.sleep(2)
                            elapsed += 2
                            progress.progress(min(elapsed * 5, 95), text=f"Processing... ({elapsed}s)")
                            video_file = genai.get_file(video_file.name)

                        if video_file.state.name == "FAILED":
                            st.error("❌ Video processing failed.")
                        else:
                            progress.progress(100, text="Video processed! ✅")
                            model = get_gemini_model()
                            prompt = video_prompt or (
                                "Watch this video carefully. Provide:\n"
                                "1. Detailed scene-by-scene summary\n"
                                "2. Key events and timestamps\n"
                                "3. Objects, people, and text identified\n"
                                "4. Overall analysis and insights"
                            )
                            response = model.generate_content([prompt, video_file])
                            st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Video Error: {e}")
                    finally:
                        if os.path.exists("temp_video.mp4"):
                            os.remove("temp_video.mp4")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: PDF READER
# ──────────────────────────────────────────────────────────────────────────────
with tab_pdf:
    st.markdown("""
    <div class="feature-header">
        <div class="feature-icon">📄</div>
        <div>
            <div class="feature-title">PDF Intelligence Reader</div>
            <div class="feature-desc">Upload PDFs — extract text, tables, images, and get AI-powered analysis page by page</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not PDF_AVAILABLE:
        st.warning("""
        ⚠️ **PyMuPDF is required for PDF support.**

        Install it with:
        ```bash
        pip install PyMuPDF
        ```
        Then restart the app.
        """)
    else:
        pdf_file = st.file_uploader(
            "Upload PDF Document", type=["pdf"],
            help="Supports any PDF — text, scanned, tables, multi-page",
            key="pdf_uploader"
        )

        if pdf_file:
            # Extract everything
            with st.spinner("🔍 Parsing PDF..."):
                pages_text, num_pages, metadata = extract_pdf_text(pdf_file)
                tables = extract_pdf_tables(pdf_file)

            # PDF Metrics
            total_chars = sum(len(p) for p in pages_text)
            total_words = sum(len(p.split()) for p in pages_text)
            table_count = len(tables)

            st.markdown(f"""
            <div class="glass-card">
                <strong style="font-size: 1.1rem;">📄 {pdf_file.name}</strong>
                <div class="metric-grid" style="margin-top: 12px;">
                    <div class="metric-card">
                        <div class="metric-value">{num_pages}</div>
                        <div class="metric-label">Pages</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_words:,}</div>
                        <div class="metric-label">Words</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_chars:,}</div>
                        <div class="metric-label">Characters</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{table_count}</div>
                        <div class="metric-label">Tables Found</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Metadata
            if metadata and any(metadata.values()):
                with st.expander("📋 Document Metadata"):
                    meta_items = {k: v for k, v in metadata.items() if v}
                    for key, val in meta_items.items():
                        st.markdown(f"**{key}:** {val}")

            # PDF Sub-tabs
            pdf_tab1, pdf_tab2, pdf_tab3, pdf_tab4, pdf_tab5 = st.tabs([
                "📖 Page Reader", "📑 Full Text", "📊 Extracted Tables", "🖼️ Page Previews", "🧠 AI Analysis"
            ])

            # ── Page-by-Page Reader ──
            with pdf_tab1:
                if num_pages > 0:
                    page_num = st.slider(
                        "Select Page", 1, num_pages, 1,
                        key="pdf_page_slider"
                    )
                    col_page1, col_page2 = st.columns([1, 1])

                    with col_page1:
                        # Page preview
                        page_img = render_pdf_page_preview(pdf_file, page_num - 1)
                        if page_img:
                            st.image(page_img, caption=f"Page {page_num}", use_container_width=True)

                    with col_page2:
                        st.markdown(f"**Page {page_num} Text:**")
                        page_text = pages_text[page_num - 1]
                        if page_text.strip():
                            st.text_area(
                                "Extracted Text",
                                value=page_text,
                                height=500,
                                key=f"page_text_{page_num}",
                                disabled=True
                            )
                            word_count_page = len(page_text.split())
                            st.caption(f"{word_count_page} words on this page")
                        else:
                            st.info("No text found on this page (may be a scanned image).")

                    # Per-page AI analysis
                    if st.button(f"🧠 Analyze Page {page_num}", key=f"btn_pdf_page_{page_num}"):
                        with st.spinner(f"Analyzing page {page_num}..."):
                            model = get_gemini_model()
                            content_parts = [
                                f"Analyze page {page_num} of this PDF document. Provide a detailed summary, key points, and any important data or figures mentioned.\n\nPage text:\n{pages_text[page_num - 1][:6000]}"
                            ]
                            # Also send page image for multimodal analysis
                            if page_img:
                                content_parts.append(page_img)
                            try:
                                response = model.generate_content(content_parts)
                                st.markdown(response.text)
                            except Exception as e:
                                st.error(f"Analysis Error: {e}")

            # ── Full Text ──
            with pdf_tab2:
                full_text = "\n\n".join(
                    [f"{'═' * 60}\n PAGE {i+1} \n{'═' * 60}\n{text}"
                     for i, text in enumerate(pages_text)]
                )
                st.text_area("Full Document Text", value=full_text, height=600, key="pdf_full_text", disabled=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "📥 Download as TXT",
                        full_text.encode("utf-8"),
                        f"{pdf_file.name.replace('.pdf', '')}_text.txt",
                        "text/plain",
                        key="pdf_dl_txt"
                    )
                with col_dl2:
                    # Search in PDF
                    search_term = st.text_input("🔍 Search in document", key="pdf_search")
                    if search_term:
                        occurrences = []
                        for i, text in enumerate(pages_text):
                            if search_term.lower() in text.lower():
                                idx = text.lower().index(search_term.lower())
                                snippet = text[max(0, idx - 80):idx + len(search_term) + 80]
                                occurrences.append((i + 1, snippet))
                        if occurrences:
                            st.success(f"Found {len(occurrences)} occurrence(s)")
                            for page, snippet in occurrences:
                                st.markdown(f"**Page {page}:** ...{snippet}...")
                        else:
                            st.warning("No matches found.")

            # ── Tables ──
            with pdf_tab3:
                if tables:
                    for i, table_info in enumerate(tables):
                        st.markdown(f"**Table {i + 1}** (Page {table_info['page']})")
                        tdf = table_info["dataframe"]
                        st.dataframe(tdf, use_container_width=True)
                        csv_dl = tdf.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            f"📥 Download Table {i + 1} as CSV",
                            csv_dl,
                            f"table_{i+1}_page_{table_info['page']}.csv",
                            "text/csv",
                            key=f"pdf_table_dl_{i}"
                        )
                        st.markdown("---")
                else:
                    st.info("No tables detected in this PDF.")

            # ── Page Previews ──
            with pdf_tab4:
                st.markdown("**Page Thumbnails:**")
                pages_per_row = st.slider("Pages per row", 2, 6, 3, key="pdf_thumbs_per_row")
                cols = st.columns(pages_per_row)
                for i in range(min(num_pages, 30)):  # Max 30 previews
                    with cols[i % pages_per_row]:
                        img = render_pdf_page_preview(pdf_file, i, zoom=1.0)
                        if img:
                            st.image(img, caption=f"Page {i + 1}", use_container_width=True)

            # ── AI Analysis ──
            with pdf_tab5:
                st.markdown("**🧠 Full Document AI Analysis**")

                analysis_mode = st.selectbox("Analysis Mode", [
                    "📝 Executive Summary",
                    "🔑 Key Points & Takeaways",
                    "❓ Question Answering",
                    "📊 Data & Statistics Extraction",
                    "🏗️ Structure Analysis",
                    "🌐 Translation",
                    "💡 Custom Analysis",
                ], key="pdf_analysis_mode")

                custom_pdf_prompt = ""
                if analysis_mode == "💡 Custom Analysis":
                    custom_pdf_prompt = st.text_area("Enter your analysis prompt", key="pdf_custom_prompt")
                elif analysis_mode == "❓ Question Answering":
                    custom_pdf_prompt = st.text_input("Ask a question about this document", key="pdf_question")
                elif analysis_mode == "🌐 Translation":
                    target_lang = st.selectbox("Target Language", [
                        "Hindi", "Spanish", "French", "German", "Japanese",
                        "Chinese", "Korean", "Arabic", "Portuguese", "Russian"
                    ], key="pdf_lang")
                    custom_pdf_prompt = f"Translate the key content of this document to {target_lang}."

                mode_prompts = {
                    "📝 Executive Summary": "Provide a comprehensive executive summary of this document. Include: 1) Main topic 2) Key arguments 3) Conclusions 4) Important data points.",
                    "🔑 Key Points & Takeaways": "Extract ALL key points, takeaways, and actionable items from this document. Format as a structured list.",
                    "📊 Data & Statistics Extraction": "Extract ALL numerical data, statistics, percentages, dates, and quantitative information from this document. Present in a structured format.",
                    "🏗️ Structure Analysis": "Analyze the structure and organization of this document. Identify: sections, hierarchy, flow, references, and how arguments are constructed.",
                }

                if st.button("🚀 Run Analysis", key="btn_pdf_ai"):
                    with st.spinner("Gemini is reading the document..."):
                        model = get_gemini_model()
                        combined_text = "\n".join(pages_text)[:30000]  # Gemini context limit safety

                        if analysis_mode in mode_prompts:
                            prompt = mode_prompts[analysis_mode]
                        else:
                            prompt = custom_pdf_prompt

                        full_prompt = f"{prompt}\n\n--- DOCUMENT START ---\n{combined_text}\n--- DOCUMENT END ---"

                        try:
                            response = model.generate_content(full_prompt)
                            st.markdown(response.text)
                            st.session_state.analysis_results.append({
                                "type": "pdf_analysis",
                                "file": pdf_file.name,
                                "mode": analysis_mode,
                                "time": datetime.now().isoformat(),
                            })
                        except Exception as e:
                            st.error(f"Analysis Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3: SQL AGENT
# ──────────────────────────────────────────────────────────────────────────────
with tab_sql:
    st.markdown("""
    <div class="feature-header">
        <div class="feature-icon">🤖</div>
        <div>
            <div class="feature-title">SQL Agent</div>
            <div class="feature-desc">Ask questions in plain English — AI generates and executes SQL queries automatically</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Database setup
    conn = sqlite3.connect("shape_shifter.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product TEXT, category TEXT, amount INTEGER,
        date TEXT, region TEXT, rating REAL
    )""")

    # Seed with sample data if empty
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        sample_records = [
            ("Gemini Pro", "AI", 1500, "2025-01-01", "North", 4.8),
            ("Cloud Basic", "Cloud", 800, "2025-01-02", "South", 4.2),
            ("AI Consulting", "Services", 5000, "2025-01-03", "East", 4.9),
            ("Server Rack", "Hardware", 3000, "2025-01-04", "West", 4.5),
            ("Dev Tools", "Software", 1200, "2025-01-05", "North", 4.7),
            ("Cloud Premium", "Cloud", 3200, "2025-01-06", "South", 4.9),
            ("AI Training", "AI", 4500, "2025-01-07", "East", 5.0),
            ("Firewall Pro", "Hardware", 2800, "2025-01-08", "West", 4.6),
            ("Analytics Suite", "Software", 2000, "2025-01-09", "North", 4.8),
            ("Gemini Enterprise", "AI", 8000, "2025-01-10", "South", 5.0),
        ]
        cursor.executemany(
            "INSERT INTO sales (product, category, amount, date, region, rating) VALUES (?, ?, ?, ?, ?, ?)",
            sample_records
        )
        conn.commit()

    # Upload CSV to DB
    with st.expander("📤 Import CSV into Database"):
        csv_for_db = st.file_uploader("Upload CSV to populate database", type=["csv"], key="sql_csv_upload")
        if csv_for_db:
            df_import = pd.read_csv(csv_for_db)
            st.dataframe(df_import.head(), use_container_width=True)
            table_name = st.text_input("Table name", value="imported_data", key="sql_table_name")
            if st.button("📥 Import to Database", key="btn_import_db"):
                try:
                    df_import.to_sql(table_name, conn, if_exists="replace", index=False)
                    st.success(f"✅ Imported {len(df_import)} rows into `{table_name}`!")
                except Exception as e:
                    st.error(f"Import Error: {e}")

    # Show tables
    with st.expander("📋 View Database Tables"):
        tables_list = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )
        for _, row in tables_list.iterrows():
            tname = row["name"]
            tcount = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {tname}", conn).iloc[0]["cnt"]
            st.markdown(f"**{tname}** — {tcount} rows")
            if st.checkbox(f"Preview `{tname}`", key=f"preview_{tname}"):
                st.dataframe(pd.read_sql_query(f"SELECT * FROM {tname} LIMIT 10", conn), use_container_width=True)

    # Query input
    user_query = st.text_input(
        "Ask the database anything",
        placeholder="e.g., 'What's the total sales by category?' or 'Show top 5 products by rating'",
        key="sql_query"
    )

    if user_query and st.button("⚡ Execute Agent", key="btn_sql"):
        with st.spinner("🧠 Gemini is writing SQL..."):
            model = get_gemini_model()
            # Get available tables info
            tables_info = ""
            for _, row in tables_list.iterrows():
                tname = row["name"]
                cols = pd.read_sql_query(f"PRAGMA table_info({tname})", conn)
                cols_str = ", ".join([f"{r['name']} ({r['type']})" for _, r in cols.iterrows()])
                tables_info += f"Table `{tname}`: {cols_str}\n"

            prompt = f"""You are a SQL Expert. I have a SQLite database with these tables:
{tables_info}
Write a valid SQL query to answer: "{user_query}"
IMPORTANT: Return ONLY the SQL code. No markdown, no explanations, no ```."""

            try:
                response = model.generate_content(prompt)
                sql_query = response.text.strip().replace("```sql", "").replace("```", "").strip()
                st.code(sql_query, language="sql")
                df_result = pd.read_sql_query(sql_query, conn)
                st.dataframe(df_result, use_container_width=True)
                if len(df_result) > 0 and len(df_result.columns) >= 2:
                    try:
                        st.bar_chart(df_result.set_index(df_result.columns[0]))
                    except Exception:
                        pass
            except Exception as e:
                st.error(f"Agent Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4: LIVE CAMERA FEED
# ──────────────────────────────────────────────────────────────────────────────
with tab_camera:
    st.markdown("""
    <div class="feature-header">
        <div class="feature-icon">📸</div>
        <div>
            <div class="feature-title">Live Visual Feed</div>
            <div class="feature-desc">Capture and analyze live camera input with Gemini Vision</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    camera_file = st.camera_input("Capture Live Data", key="camera_input")

    if camera_file:
        st.success("✅ Live Feed Captured")
        image = Image.open(camera_file)

        col_cam1, col_cam2 = st.columns([2, 1])
        with col_cam1:
            st.image(image, use_container_width=True)
        with col_cam2:
            cam_mode = st.selectbox("Analysis Mode", [
                "🔍 What do you see?",
                "📝 Extract text (OCR)",
                "🏷️ Identify objects",
                "📊 Read data/charts",
                "💡 Custom prompt",
            ], key="cam_mode")

            if cam_mode == "💡 Custom prompt":
                cam_prompt = st.text_input("Your prompt", key="cam_custom")
            else:
                cam_prompt = {
                    "🔍 What do you see?": "Describe everything you see in this live camera feed in detail.",
                    "📝 Extract text (OCR)": "Extract all text visible in this image.",
                    "🏷️ Identify objects": "List every object, person, and element visible.",
                    "📊 Read data/charts": "If there's any data, charts, or numbers visible, extract and analyze them.",
                }[cam_mode]

        if st.button("🔴 Analyze Live Feed", key="btn_cam"):
            with st.spinner("Scanning..."):
                model = get_gemini_model()
                try:
                    response = model.generate_content([cam_prompt, image])
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 5: VOICE COMMAND
# ──────────────────────────────────────────────────────────────────────────────
with tab_voice:
    st.markdown("""
    <div class="feature-header">
        <div class="feature-icon">🎙️</div>
        <div>
            <div class="feature-title">Voice Command</div>
            <div class="feature-desc">Speak your query — Gemini transcribes and executes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    audio_value = st.audio_input("Record a command", key="voice_input")

    if audio_value:
        st.success("🎤 Audio Captured")

        voice_mode = st.selectbox("Voice Mode", [
            "📝 Transcribe Only",
            "🤖 Transcribe + SQL Query",
            "🧠 Transcribe + Answer",
            "🌐 Transcribe + Translate",
        ], key="voice_mode")

        if st.button("⚡ Process Voice", key="btn_voice"):
            with st.spinner("Gemini is listening..."):
                model = get_gemini_model()

                mode_prompts = {
                    "📝 Transcribe Only": "Listen to this audio and provide an exact transcription.",
                    "🤖 Transcribe + SQL Query": """Listen to this audio.
1. Transcribe it exactly.
2. If it's a data query, convert to SQL for a table named 'sales' with columns: id, product, category, amount, date, region, rating.
Return JSON: {"transcription": "...", "sql": "..."}""",
                    "🧠 Transcribe + Answer": "Listen to this audio, transcribe it, then answer the question or fulfill the request.",
                    "🌐 Transcribe + Translate": "Listen to this audio, transcribe it, then translate to Hindi, Spanish, and French.",
                }

                try:
                    response = model.generate_content([mode_prompts[voice_mode], audio_value])
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Voice Error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 6: AI CHAT
# ──────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("""
    <div class="feature-header">
        <div class="feature-icon">💬</div>
        <div>
            <div class="feature-title">Gemini Chat</div>
            <div class="feature-desc">Free-form conversation with context awareness — knows about your uploaded data</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    col_chat1, col_chat2 = st.columns([5, 1])
    with col_chat1:
        chat_input = st.text_input(
            "Message Gemini",
            placeholder="Ask anything... I know about your uploaded data too!",
            key="chat_input",
            label_visibility="collapsed"
        )
    with col_chat2:
        send_btn = st.button("Send ⚡", key="btn_chat_send", use_container_width=True)

    if send_btn and chat_input:
        st.session_state.chat_history.append({"role": "user", "content": chat_input})

        with st.spinner("Thinking..."):
            model = get_gemini_model()
            # Build context
            context_parts = []
            if st.session_state.uploaded_data is not None:
                df = st.session_state.uploaded_data
                context_parts.append(
                    f"The user has uploaded data with columns: {list(df.columns)}. "
                    f"Shape: {df.shape}. Sample:\n{df.head(3).to_string()}"
                )
            # Include recent chat history
            recent_history = st.session_state.chat_history[-10:]
            history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent_history])
            context = "\n".join(context_parts) if context_parts else "No data uploaded yet."

            prompt = f"""You are a helpful AI assistant in the Gemini Shape-Shifter app.
Context about uploaded data: {context}

Conversation history:
{history_str}

Respond helpfully and concisely. If the user asks about their data, reference the actual columns and values."""

            try:
                response = model.generate_content(prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"Chat Error: {e}")

    # Clear chat
    if st.button("🗑️ Clear Chat", key="btn_clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 7. FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 20px 0; font-family: 'JetBrains Mono', monospace;">
    <div style="font-size: 0.7rem; color: #555;">
        SHAPE-SHIFTER ∞ — Built with Gemini 2.0 Flash & Streamlit<br>
        <span style="color: #00f0ff;">CSV</span> •
        <span style="color: #ff00e5;">PDF</span> •
        <span style="color: #8b5cf6;">Excel</span> •
        <span style="color: #00ff88;">Images</span> •
        <span style="color: #ff6b35;">Video</span> •
        <span style="color: #ffd700;">Audio</span> •
        <span style="color: #00f0ff;">Camera</span> •
        <span style="color: #ff00e5;">SQL</span> •
        <span style="color: #8b5cf6;">Chat</span>
    </div>
</div>
""", unsafe_allow_html=True)
