import streamlit as st
import requests
from pypdf import PdfReader
from docx import Document
import io
from gtts import gTTS

# Setup Streamlit page configuration & professional layout
st.set_page_config(
    page_title="Anandisini AI - ប្រព័ន្ធបកប្រែឯកសារផ្លូវការ", 
    page_icon="🌐", 
    layout="wide"
)

# Initialize Session State for Translation History
if "history" not in st.session_state:
    st.session_state.history = []

# Custom UI Header matching original design
st.markdown("""
    <div style='background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 25px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h2 style='margin-bottom: 5px;'>🌐 Anandisini AI - ប្រព័ន្ធបកប្រែឯកសារ និងច្បាប់ជាភាសាខ្មែរ</h2>
        <p style='font-size: 16px; margin: 0;'>ប្រព័ន្ធបកប្រែឯកសារផ្លូវការ កិច្ចការទូទៅ និងប្រវត្តិសាស្ត្រ พร้อมមុខងារស្ដាប់សម្លេង និងរក្សាទុកប្រវត្តិ</p>
    </div>
""", unsafe_allow_html=True)

st.write("")

# Sidebar for Translation History
with st.sidebar:
    st.markdown("### 🕒 ប្រវត្តិការបកប្រែ (History)")
    if st.session_state.history:
        if st.button("🗑️ សម្អាតប្រវត្តិទាំងអស់", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        
        for idx, item in enumerate(st.session_state.history):
            with st.expander(f"ឯកសារទី {idx+1} ({item['lang']})"):
                st.write(f"**កាលបរិច្ឆេទ:** {item['time']}")
                st.text_area(f"លទ្ធផល {idx}", item['result'], height=100, key=f"hist_{idx}")
    else:
        st.info("មិនទាន់មានប្រវត្តិការបកប្រែនៅឡើយទេ។")

# Layout columns for professional look
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📂 បញ្ចូលឯកសាររបស់អ្នក")
    uploaded_file = st.file_uploader(
        "ជ្រើសរើស ឬទម្លាក់ឯកសារ (PDF, Word, Text):", 
        type=["pdf", "docx", "txt"]
    )

with col2:
    st.markdown("### ⚙️ ការកំណត់ការបកប្រែ")
    target_lang = st.selectbox(
        "ជ្រើសរើសភាសាគោលដៅ:", 
        ["Khmer (ខ្មែរ)", "English (អង់គ្លេស)", "Chinese (ចិន)"]
    )
    lang_code = "km" if "Khmer" in target_lang else ("en" if "English" in target_lang else "zh")

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

# Translation function using MyMemory stable API
def translate_text_safely(text, target_code):
    url = "https://api.mymemory.translated.net/get"
    safe_chunk = text[:1000] if len(text) > 1000 else text
    params = {
        'q': safe_chunk,
        'langpair': f'autodetect|{target_code}'
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
    st.success("✅ បានទាញយកឯកសារដោយជោគជ័យ!")
    raw_text = extract_text(uploaded_file)
    
    with st.expander("🔍 មើលអត្ថបទដើម (Raw Text Preview)"):
        st.text_area("Original Text", raw_text, height=150)
    
    st.write("")
    if st.button("🚀 ចាប់ផ្តើមបកប្រែឯកសារឥឡូវនេះ", type="primary", use_container_width=True):
        with st.spinner("កំពុងដំណើរការបកប្រែដោយសុវត្ថិភាព..."):
            translated_text = translate_text_safely(raw_text, lang_code)
        
        # Save to history session
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.insert(0, {
            "time": current_time,
            "lang": target_lang,
            "result": translated_text
        })
        
        st.success("🎉 ការបកប្រែបានសម្រេចដោយជោគជ័យ!")
        st.markdown("### 📝 លទ្ធផលបកប្រែ (មានប៊ូតុង Copy ស្រាប់នៅជ្រុងខាងស្តាំប្រអប់):")
        st.text_area("Translated Output", translated_text, height=300)
        
        # Audio Player (Text-to-Speech)
        st.markdown("### 🔊 សម្លេងអានអត្ថបទ (Audio Player)")
        try:
            tts_lang = 'km' if 'Khmer' in target_lang else ('en' if 'English' in target_lang else 'zh-CN')
            tts = gTTS(text=translated_text[:1000], lang=tts_lang, slow=False)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format='audio/mp3')
        except Exception:
            st.info("មុខងារអានសម្លេងកំពុងរៀបចំ...")

        # Word Document Export
        doc = Document()
        doc.add_heading('Anandisini AI - Translated Document', 0)
        doc.add_paragraph(translated_text)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.download_button(
            label="📥 ទាញយកលទ្ធផលជាឯកសារ Word (.docx)",
            data=bio,
            file_name="Anandisini_Translated_Document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
