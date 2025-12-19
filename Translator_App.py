import streamlit as st
import requests
import time
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from streamlit_lottie import st_lottie

# ---------------- Page Config ----------------
st.set_page_config(page_title="Language Translator", layout="wide")

# ---------------- CSS Animations ----------------
st.markdown("""
<style>
.fade-in { animation: fadeIn 1.5s ease-in-out; }
@keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }
.slide-up { animation: slideUp 0.5s ease; }
@keyframes slideUp { from {transform: translateY(10px); opacity:0;} to {transform: translateY(0); opacity:1;} }
</style>
""", unsafe_allow_html=True)

# ---------------- Load Lottie ----------------
def load_lottie(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

loading_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")

# ---------------- Translator Setup ----------------
lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

# ---------------- Sidebar ----------------
st.sidebar.header("🎛️ Controls")
typing_speed = st.sidebar.slider("⌨️ Typing Speed (ms)", 5, 100, 20)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=True)

# ---------------- Main UI ----------------
st.markdown("<h1 class='fade-in' style='text-align:center;'>🌐 Language Translator</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Input Text")
    input_text = st.text_area("", height=200, placeholder="Type text here...", key="input")

with col2:
    st.subheader("Translated Output")
    output_container = st.container(border=True)
    output_box = output_container.empty()

# ---------------- Language Selection ----------------
st.markdown("---")
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    source_language = st.selectbox("From", ["Auto Detect"] + language_names)
with c2:
    target_language = st.selectbox("To", language_names, index=language_names.index("Spanish"))
with c3:
    st.write("##") # Spacer
    translate_btn = st.button("🚀 Translate", use_container_width=True)

# ---------------- Logic ----------------
if translate_btn:
    if not input_text.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        try:
            # Translation
            src_code = "auto" if source_language == "Auto Detect" else lang_map[source_language]
            targ_code = lang_map[target_language]
            
            translated_text = GoogleTranslator(source=src_code, target=targ_code).translate(input_text)

            # Typing Effect
            displayed = ""
            for char in translated_text:
                displayed += char
                output_box.markdown(f"<div class='slide-up'>{displayed}</div>", unsafe_allow_html=True)
                time.sleep(typing_speed / 1000)

            # Text to Speech Logic
            if enable_tts:
                with st.spinner("Generating Voice..."):
                    tts = gTTS(text=translated_text, lang=targ_code, slow=False)
                    # Use a unique filename or overwrite
                    tts.save("speech.mp3")
                    st.audio("speech.mp3", format="audio/mp3")
            
            st.success("✅ Done!")

        except Exception as e:
            st.error(f"Error: {e}")
