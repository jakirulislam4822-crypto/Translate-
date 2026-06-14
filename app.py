import streamlit as st
import easyocr
import translators as ts
from fpdf import FPDF
from PIL import Image
import os

st.set_page_config(page_title="Universal Document Translator", page_icon="🌐", layout="centered")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ar', 'en'])

reader = load_ocr()

st.title("🌐 Universal Image-to-PDF Translator")
st.write("Upload an image of a document (e.g., Arabic), extract its text, translate it to English, and download it as a clean PDF.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload document image (PNG, JPG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Document Scan', use_column_width=True)
    
    if st.button("🚀 Extract, Translate & Generate PDF", type="primary"):
        with st.spinner("Step 1: Analyzing image and extracting text..."):
            temp_img_path = "temp_ocr_image.png"
            image.save(temp_img_path)
            ocr_results = reader.readtext(temp_img_path, detail=0)
            extracted_text = " ".join(ocr_results)
            
            if not extracted_text.strip():
                st.error("No text could be found in the image.")
                os.remove(temp_img_path)
                st.stop()
                
        with st.spinner("Step 2: Translating text to English..."):
            try:
                translated_text = ts.translate_text(extracted_text, from_language='auto', to_language='en', engine='google')
            except Exception as e:
                st.error(f"Translation failed: {e}")
                os.remove(temp_img_path)
                st.stop()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Extracted Raw Text")
            st.text_area("Original", extracted_text, height=250)
        with col2:
            st.subheader("✨ English Translation")
            st.text_area("Translated", translated_text, height=250)

        with st.spinner("Step 3: Creating your PDF..."):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(15, 15, 15)
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(0, 10, "Translated Document Report", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, txt=translated_text)
            
            output_pdf_path = "Translated_Document.pdf"
            pdf.output(output_pdf_path)

        st.success("🎉 Process Complete!")
        with open(output_pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Translated PDF",
                data=pdf_file,
                file_name="Translated_Document.pdf",
                mime="application/pdf"
            )
            
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
