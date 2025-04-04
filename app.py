from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import time
import platform
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Automatically detect OS and set Poppler path
if platform.system() == "Windows":
    POPPLER_PATH = r"C:\Program Files (x86)\poppler\Library\bin"
else:
    POPPLER_PATH = "/usr/bin"  # Path for Linux (Streamlit Cloud)

# Streamlit App Configuration
st.set_page_config(page_title="📑 ATS Resume Expert", layout="wide")

# Header with Styling
st.markdown(
    """
    <h1 style="text-align:center; color:#4A90E2;">📑 ATS Resume Expert</h1>
    <p style="text-align:center; font-size:18px; color:#333;">
        Optimize your resume for ATS & improve job matching 🚀
    </p>
    """,
    unsafe_allow_html=True,
)

# Function to process PDF and extract first page as an image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            with st.spinner("📄 Converting PDF to image..."):
                images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=POPPLER_PATH)

                first_page = images[0]
                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG', quality=100)  # Keep quality high
                img_byte_arr = img_byte_arr.getvalue()

                pdf_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_byte_arr).decode()
                    }
                ]
                return pdf_parts
        except Exception as e:
            st.error(f"⚠️ Error processing PDF: {e}")
            return None
    else:
        st.error("⚠️ No file uploaded")
        return None

# Function to send request to Google Gemini API
def get_gemini_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        with st.spinner("⏳ Sending request to Google Gemini API..."):
            start_time = time.time()
            response = model.generate_content(
                [input_text, pdf_content[0], prompt], 
                request_options={"timeout": 30}  # Set a 30s timeout
            )
            end_time = time.time()
            st.success(f"✅ Response received in {end_time - start_time:.2f} seconds")

        return response.text
    except Exception as e:
        st.error(f"⚠️ Gemini API Timeout/Error: {e}")
        return None

# Sidebar
with st.sidebar:
    st.header("🔍 Quick Guide")
    st.markdown(
        """
        - 📄 **Upload your Resume** (PDF only)
        - 📝 **Paste Job Description**
        - 🚀 **Analyze & Optimize** your resume
        - 📊 **Get ATS Score & Missing Keywords**
        """
    )

    st.divider()
    st.info("👀 This tool helps you optimize your resume for ATS-based hiring!")

# Layout: Two Columns
col1, col2 = st.columns(2)

# Column 1: Job Description
with col1:
    st.subheader("📋 Job Description")
    input_text = st.text_area("Paste the Job Description Here:", height=250)

# Column 2: Resume Upload
with col2:
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

    if uploaded_file is not None:
        if uploaded_file.size > 100 * 1024 * 1024:  # 100MB Limit
            st.error("⚠️ File too large! Please upload a resume smaller than 100MB.")
        else:
            st.success("✅ Resume Uploaded Successfully")

# Prompts for Gemini AI
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of ATS functionality. 
Evaluate the resume against the provided job description and:
- Provide a **percentage match**
- List **missing keywords**
- Give **overall thoughts**
"""

# Buttons for Actions
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    submit1 = st.button("📌 Get Resume Evaluation")
with col2:
    submit3 = st.button("📊 Get ATS Score & Missing Keywords")

# Processing based on button clicks
if submit1:
    if uploaded_file is not None:
        with st.spinner("⏳ Processing resume, please wait..."):
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content:
                response = get_gemini_response(input_prompt1, pdf_content, input_text)
                if response:
                    st.subheader("📌 Resume Evaluation")
                    st.success(response)
    else:
        st.warning("⚠️ Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        with st.spinner("⏳ Processing resume, please wait..."):
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content:
                response = get_gemini_response(input_prompt3, pdf_content, input_text)
                if response:
                    st.subheader("📊 ATS Match Score & Analysis")
                    st.success(response)
    else:
        st.warning("⚠️ Please upload the resume")
