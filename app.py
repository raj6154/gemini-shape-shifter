import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# --- 1. SETUP ---
st.set_page_config(
    page_title="Gemini 3.0: Multimodal Engine", layout="wide", page_icon="👁️"
)

st.markdown(
    """
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1 { color: #4F8BF9; }
    .stButton>button { background-color: #4F8BF9; color: white; border-radius: 10px; }
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg",
        width=150,
    )
    st.title("Control Deck")
    api_key = st.text_input("API Key (Security Clearance)", type="password")
    st.info("System Status: MULTIMODAL ACTIVE 🚀")

# --- 2. THE ENGINE ---
if api_key:
    genai.configure(api_key=api_key)
    # Using Flash Preview because it supports Text AND Images
    model = genai.GenerativeModel("gemini-3-flash-preview")

    st.title("Gemini 3.0: The Universal Engine 🧠")
    st.markdown("### Drop Data (CSV) to visualize OR Drop Images to analyze.")

    # UPDATED: Accept Images AND CSVs
    uploaded_file = st.file_uploader(
        "Drop Intelligence", type=["csv", "xlsx", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1].lower()

        # === MODE A: DATA ANALYST (The CSV Logic) ===
        if file_type in ["csv", "xlsx"]:
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("📂 Data Detected. Activating Dashboard Mode.")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Raw Matrix")
                st.dataframe(df.head(3))
                goal = st.text_input("What is your mission?", "Analyze the trends")

            if st.button("Generate Dashboard ⚡"):
                with st.spinner("Gemini is coding the dashboard..."):
                    try:
                        prompt = f"""
                        You are a Senior Data Scientist.
                        DATA: {list(df.columns)}
                        Sample: {df.head(1).to_dict()}
                        GOAL: {goal}
                        
                        Write a Streamlit script (using st, pd, plt) to visualize this.
                        RULES: Use 'df' directly. Create 2 charts. Output ONLY CODE.
                        """
                        response = model.generate_content(prompt)
                        generated_code = (
                            response.text.replace("```python", "")
                            .replace("```", "")
                            .strip()
                        )

                        with col2:
                            exec(
                                generated_code,
                                {"df": df, "st": st, "pd": pd, "plt": plt, "sns": sns},
                            )
                    except Exception as e:
                        st.error(f"Crash: {e}")

        # === MODE B: VISUAL ANALYST (The New Image Logic) ===
        elif file_type in ["png", "jpg", "jpeg"]:
            st.success("👁️ Image Detected. Activating Vision Mode.")

            # 1. Open the Image
            image = Image.open(uploaded_file)

            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="Uploaded Evidence", use_container_width=True)

            with col2:
                st.subheader("AI Analysis")
                user_question = st.text_input(
                    "What do you want to know about this image?",
                    "Explain what is happening in this image in detail.",
                )

                if st.button("Analyze Image 🔍"):
                    with st.spinner("Gemini is seeing..."):
                        # Send Image + Text to Gemini
                        response = model.generate_content([user_question, image])
                        st.markdown(response.text)
                        st.balloons()

else:
    st.markdown("### 🛑 Waiting for Neural Link (Enter API Key)")
