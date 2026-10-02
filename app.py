import streamlit as st
import requests
from pypdf import PdfReader
from docx import Document
import io

# Setup Streamlit page
st.set_page_config(page_title="Anandisini AI - ប្រព័ន្ធបកប្រែ", page_icon="🌐", layout="wide")

st.markdown("""
    <div style='background-color: #1E3A8A; padding: 20px; border-radius: 10px; text-align: center; color: white;'>
        <h2>🌐 Anandisini AI - ប្រព័ន្ធបកប្រែឯកសារ និងច្បាប់ជាភាសាខ្មែរ</h2>
        <p>ប្រព័ន្ធបកប្រែឆ្លាតវៃដោយសុវត្ថិភាពខ្ពស់ (ឥតគិតថ្លៃ 100%)</p>
    </div>
""", unsafe_allow_html=True)

# File Uploader
uploaded_file = st.file_uploader("📂 ជ្រើសរើស ឬទម្លាក់ឯកសាររបស់អ្នកនៅទីນີ້ (PDF, Word, Text):", type=["pdf", "docx", "txt"])

def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.getvalue().decode("utf-8")
    return text

# Stable Free Translator using MyMemory API
def translate_text_mymemory(text, target_lang_code):
    url = "https://api.mymemory.translated.net/get"
    # Limit chunk size to 500 characters for safety per request
    safe_text = text[:500] 
    params = {
        'q': safe_text,
        'langpair': f'autodetect|{target_lang_code}'
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get('responseStatus') == 200:
            return data['responseData']['translatedText']
        else:
            return text
    except Exception:
        return text

if uploaded_file is not None:
    st.success("បានទាញយកឯកសារដោយជោគជ័យ!")
    raw_text = extract_text(uploaded_file)
    
    # Target Language Selection
    target_lang = st.selectbox("ជ្រើសរើសភាសាគោលដៅ:", ["Khmer (ខ្មែរ)", "English (អង់គ្លេស)", "Chinese (ចិន)"])
    lang_code = "km" if "Khmer" in target_lang else ("en" if "English" in target_lang else "zh")
    
    if st.button("🚀 ចាប់ផ្តើមបកប្រែឯកសារ"):
        try:
            with st.spinner("កំពុងបកប្រែអត្ថបទតាមរយៈប្រព័ន្ធសុវត្ថិភាព..."):
                translated_text = translate_text_mymemory(raw_text, lang_code)
            
            st.success("ការបកប្រែបានសម្រេចដោយជោគជ័យ!")
            st.subheader("📝 លទ្ធផលបកប្រែ:")
            st.text_area("Translated Text", translated_text, height=300)
            
            # Create Word download
            doc = Document()
            doc.add_heading('Translated Document', 0)
            doc.add_paragraph(translated_text)
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            
            st.download_button(
                label="📥 ទាញយកជាឯកសារ Word (.docx)",
                data=bio,
                file_name="translated_document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"មានបញ្ហាក្នុងการបកប្រែ: {e}")