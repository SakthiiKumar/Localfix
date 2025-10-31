import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image
import textwrap
import base64

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
# Load env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# ---- Streamlit UI ----
st.set_page_config(page_title="LocalFix Assistant", layout="centered")

st.markdown("""
<style>
body {background-color: #0f172a; font-family: 'Inter', sans-serif;}
.main-title {font-size: 3rem; font-weight: 700; color: #38bdf8; text-align: center; margin-bottom: 0.3rem;}
.sub-title {font-size: 1.3rem; color: #94a3b8; text-align: center; margin-bottom: 2rem;}
.stButton button {background: linear-gradient(90deg, #2563eb, #1e40af); color: white; font-weight: bold; border-radius: 12px; padding: 12px 40px; font-size: 16px; border: none; transition: transform 0.2s ease, background 0.3s ease;}
.stButton button:hover {transform: scale(1.05); background: linear-gradient(90deg, #1e40af, #2563eb);}
.response-box {background: #1e293b; padding: 20px; border-radius: 15px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); margin-top: 25px; font-size: 18px; line-height: 1.6; color: #f8fafc;}
.highlight {color: #facc15; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛠 LocalFix Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload an image and/or describe your problem to get AI suggestions</div>', unsafe_allow_html=True)

# ---- Form ----
with st.form("localfix_form"):
    uploaded_image = st.file_uploader("Upload an image of the problem", type=["jpg","jpeg","png"])
    user_problem = st.text_area("Or describe your problem here:", placeholder="E.g., My kitchen sink is leaking...")
    submit_button = st.form_submit_button("🔍 Analyze & Get Help")

# ---- Gemini + LangChain (analysis) ----
if submit_button and (uploaded_image or user_problem):
    with st.spinner("Analyzing your input..."):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=GOOGLE_API_KEY,
            temperature=0.3
        )

        # Build message content
        content_parts = [
            {"type": "text", "text": """You are LocalFix AI. 
Analyze this input and respond in this format:

Problem Summary: ...
Suggested Fixer: ...
Why: ..."""}
        ]

        # Add user problem text if provided
        if user_problem:
            content_parts.append({"type": "text", "text": f"User description: {user_problem}"})

        # Add image if uploaded
        if uploaded_image:
            image_bytes = uploaded_image.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            content_parts.append({"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"})

        messages = [HumanMessage(content=content_parts)]
        response = llm(messages)
        wrapped_response = textwrap.fill(response.content, width=80)

    # ---- Display AI response ----
    st.markdown(f"""
    <div class="response-box">
        {wrapped_response.replace("Problem Summary", "<span class='highlight'>Problem Summary</span>").replace("Suggested Fixer", "<span class='highlight'>Suggested Fixer</span>").replace("Why", "<span class='highlight'>Why</span>")}
    </div>
    """, unsafe_allow_html=True)


