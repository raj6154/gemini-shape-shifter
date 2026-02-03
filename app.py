import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import google.generativeai as genai
from PIL import Image, ImageDraw
import io
import sqlite3
import time
import cv2
import numpy as np
import tempfile
import os

# --- 1. CONFIGURATION & CSS POLISH ---
st.set_page_config(
    page_title="Gemini 3.0 Control Deck",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🎨 CUSTOM CYBERPUNK STYLING
st.markdown(
    """
<style>
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Cyberpunk Buttons */
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF0000;
        box-shadow: 0 0 10px #FF0000;
    }
    
    /* System Status Box */
    .status-box {
        padding: 15px;
        background-color: #1E1E1E;
        border-radius: 10px;
        border-left: 5px solid #00FF00;
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ⚠️ SECURITY: Safe Key Retrieval
# This try-except block prevents the "StreamlitSecretNotFoundError" crash
# when running locally without a secrets.toml file.
try:
    if "GEMINI_API_KEY" in st.secrets:
        DEFAULT_API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        DEFAULT_API_KEY = ""
except Exception:
    # If we are local and no secrets file exists, just default to empty.
    DEFAULT_API_KEY = ""

# --- 2. SIDEBAR: CONTROL DECK ---
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/2560px-Google_Gemini_logo.svg.png",
        width=180,
    )

    st.markdown("### 🎛️ System Control")

    # API Key Box (Auto-filled if deployed, Empty if local)
    api_key = st.text_input(
        "API Key (Security Clearance)", value=DEFAULT_API_KEY, type="password"
    )

    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        api_status = "ONLINE 🟢"
    except Exception as e:
        api_status = "OFFLINE 🔴"

    # System Status Box
    st.markdown(
        f"""
    <div class="status-box">
        <small>SYSTEM STATUS</small><br>
        <strong>Connection:</strong> {api_status}<br>
        <strong>Model:</strong> Gemini 3 Flash Preview<br>
        <strong>Video Engine:</strong> ONLINE 🎥
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --- JUDGE'S TOOLKIT ---
    st.subheader("🛠️ Judge's Toolkit")

    # A. SAMPLE CSV
    sample_data = pd.DataFrame(
        {
            "Category": ["AI", "Cloud", "Hardware", "Services", "AI", "Cloud"],
            "Sales": [500, 300, 200, 400, 600, 350],
            "Region": ["North", "North", "South", "South", "East", "West"],
        }
    )
    csv = sample_data.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Test CSV", csv, "sample_data.csv", "text/csv")

    # B. SAMPLE CHART
    img_chart = Image.new("RGB", (400, 300), color=(20, 20, 30))
    d = ImageDraw.Draw(img_chart)
    d.rectangle([50, 100, 100, 250], fill="cyan")
    d.rectangle([150, 150, 200, 250], fill="magenta")
    d.text((120, 50), "SALES GROWTH", fill="white")
    buf_chart = io.BytesIO()
    img_chart.save(buf_chart, format="PNG")
    st.download_button(
        "📊 Download Test Chart", buf_chart.getvalue(), "sample_chart.png", "image/png"
    )

    # C. SAMPLE UI SKETCH
    img_ui = Image.new("RGB", (400, 300), color=(255, 255, 255))
    d_ui = ImageDraw.Draw(img_ui)
    d_ui.rectangle([20, 20, 380, 60], outline="black", width=2)  # Navbar
    d_ui.text((30, 30), "LOGO", fill="black")
    d_ui.rectangle([20, 80, 180, 250], outline="black", width=2)  # Sidebar
    d_ui.text((30, 100), "Menu Item 1", fill="black")
    d_ui.rectangle([200, 80, 380, 250], outline="black", width=2)  # Content
    d_ui.text((220, 150), "Main Content Area", fill="black")
    buf_ui = io.BytesIO()
    img_ui.save(buf_ui, format="PNG")
    st.download_button(
        "📝 Download UI Sketch", buf_ui.getvalue(), "sample_ui_sketch.png", "image/png"
    )

    # D. SAMPLE VIDEO GENERATOR
    st.markdown("---")
    if st.button("🎥 Generate Test Video (MP4)"):
        with st.spinner("Rendering synthetic video..."):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            filename = tfile.name

            width, height = 640, 480
            fps = 10
            seconds = 3
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

            for i in range(fps * seconds):
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:] = (30, 20, 20)  # Dark Background
                x = int((i / (fps * seconds)) * (width - 100))
                cv2.rectangle(frame, (x, 200), (x + 50, 250), (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    f"Frame: {i}",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )
                out.write(frame)

            out.release()
            with open(filename, "rb") as f:
                video_bytes = f.read()

            st.download_button(
                "📥 Download Generated Video",
                video_bytes,
                "test_video.mp4",
                "video/mp4",
            )
            os.unlink(filename)

# --- 3. MAIN INTERFACE ---
st.title("Gemini 3.0: The Universal Engine 🧠")
st.markdown("### *Drop data, images, VIDEO, or ask questions. The engine adapts.*")
st.divider()

# --- 4. FEATURE 1: UNIVERSAL SHAPE-SHIFTER ---
st.subheader("1. 🦎 Universal Shape-Shifter")
st.caption("Now supports: CSV, Images, and VIDEO Files (MP4).")

universal_file = st.file_uploader(
    "Upload File", type=["csv", "png", "jpg", "jpeg", "mp4"]
)

if universal_file:
    # --- PATH A: DATA MODE (CSV) ---
    if universal_file.name.endswith(".csv"):
        st.info(f"📂 Data File Detected: {universal_file.name}")
        df = pd.read_csv(universal_file)
        st.dataframe(df.head(), use_container_width=True)

        if st.button("Generate Dashboard 🚀", key="btn_csv"):
            with st.spinner("Gemini is coding a dashboard..."):
                model = genai.GenerativeModel("gemini-3-flash-preview")
                prompt = f"""
                You are a Python Data Expert.
                The dataframe 'df' has columns: {list(df.columns)}.
                Write python code using Streamlit and Seaborn to visualize 2 insights.
                DO NOT import pandas/streamlit. Assume 'df' exists.
                NO markdown ticks. Just code.
                """
                try:
                    response = model.generate_content(prompt)
                    code = response.text.replace("```python", "").replace("```", "")
                    exec(code)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

    # --- PATH B: VISION MODE (Images) ---
    elif universal_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
        st.info(f"👁️ Visual File Detected: {universal_file.name}")
        image = Image.open(universal_file)
        st.image(image, caption="Visual Data Acquired", width=400)

        if st.button("Initialize Vision Analysis 🔍", key="btn_vis"):
            with st.spinner("Gemini is scanning..."):
                model = genai.GenerativeModel("gemini-3-flash-preview")
                prompt = "Analyze this image. If it is a chart, explain the data. If it is a UI Wireframe or Sketch, describe the frontend code needed to build it."
                response = model.generate_content([prompt, image])
                st.markdown(response.text)

    # --- PATH C: VIDEO MODE (MP4) ---
    elif universal_file.name.endswith(".mp4"):
        st.info(f"🎥 Video File Detected: {universal_file.name}")
        st.video(universal_file)

        if st.button("Analyze Video Intelligence 🎬", key="btn_video"):
            with st.spinner("Uploading & Processing Video (Long Context Window)..."):
                # 1. Save temp file
                with open("temp_video.mp4", "wb") as f:
                    f.write(universal_file.read())

                # 2. Upload to Gemini File API
                video_file = genai.upload_file(path="temp_video.mp4")

                # 3. Wait for processing
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Video processing failed.")
                else:
                    st.success("✅ Video Processed by Gemini.")
                    # 4. Generate Content
                    model = genai.GenerativeModel("gemini-3-flash-preview")
                    prompt = "Watch this video carefully. Summarize what happens, describe the motion, and identify any key events or data shown."
                    response = model.generate_content([prompt, video_file])
                    st.markdown(response.text)

st.divider()

# --- 5. FEATURE 2: LIVE FEED ---
st.subheader("2. 📸 Live Visual Feed")
with st.expander("📸 Open Camera Shutter"):
    camera_file = st.camera_input("Capture Live Data")

if camera_file:
    st.success("✅ Live Feed Captured")
    image = Image.open(camera_file)
    st.image(image, width=400)

    if st.button("Analyze Live Feed 🔴", key="btn_cam"):
        with st.spinner("Scanning..."):
            model = genai.GenerativeModel("gemini-3-flash-preview")
            response = model.generate_content(
                ["What do you see in this live feed?", image]
            )
            st.markdown(response.text)

st.divider()

# --- 6. FEATURE 3: SQL AGENT ---
st.subheader("3. 🤖 SQL Agent")
st.caption("Ask questions in plain English. The AI executes the SQL.")

conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, product TEXT, category TEXT, amount INTEGER, date TEXT)"""
)

user_query = st.text_input("Ask the database (e.g., 'Total sales for Hardware?')")

if user_query:
    if st.button("Execute Agent ⚡", key="btn_sql"):
        with st.spinner("Gemini is writing SQL..."):
            model = genai.GenerativeModel("gemini-3-flash-preview")
            prompt = f"""
            You are a SQL Expert. I have a SQLite database named 'sales'.
            Columns: id, product, category, amount, date.
            Write a valid SQL query to answer: "{user_query}"
            IMPORTANT: Return ONLY the SQL code. No markdown.
            """
            try:
                response = model.generate_content(prompt)
                sql_query = (
                    response.text.strip().replace("```sql", "").replace("```", "")
                )
                st.code(sql_query, language="sql")
                df_result = pd.read_sql_query(sql_query, conn)
                st.dataframe(df_result)
                if len(df_result) > 0 and len(df_result.columns) >= 2:
                    st.bar_chart(df_result)
            except Exception as e:
                st.error(f"Agent Error: {e}")

st.divider()

# --- 7. FEATURE 4: THE VOICE ---
st.subheader("4. 🎙️ Voice Command")
st.caption("Don't type. Just say it.")

audio_value = st.audio_input("Record a command")

if audio_value:
    st.success("🎤 Audio Captured")
    if st.button("Transcribe & Execute ⚡", key="btn_voice"):
        with st.spinner("Gemini is listening..."):
            model = genai.GenerativeModel("gemini-3-flash-preview")
            prompt = """
            Listen to this audio. 
            1. Transcribe it exactly.
            2. If it is a question about data, convert it to a SQL query for a table named 'sales'.
            3. Return a JSON object: {"transcription": "...", "sql": "..."}
            """
            try:
                response = model.generate_content([prompt, audio_value])
                st.write(response.text)
            except Exception as e:
                st.error(f"Voice Error: {e}")
