import streamlit as st
import requests
import json
import base64
from io import BytesIO
import streamlit.components.v1 as components
from gtts import gTTS
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from streamlit_lottie import st_lottie

# ---------------- Page Config ----------------
st.set_page_config(page_title="Language Translator", layout="wide", page_icon="🌐")

# ---------------- CSS Animations ----------------
st.markdown("""
<style>
    /* Background Image - Room with Plants */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1497215728101-856f4ea42174?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        animation: fadeIn 0.8s ease-in-out;
    }

    /* Dark Overlay for Readability */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(255,255,255,0.3); /* Light overlay */
        z-index: -1; /* Place overlay behind content */
    }

    /* Transparent Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.2); /* Light transparent */
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar Text Color */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #111111 !important;
        text-shadow: 0 1px 2px rgba(255,255,255,0.7);
    }

    /* Ghost Select Boxes */
    div[data-testid="stSelectbox"] div[role="combobox"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #000000 !important;
        backdrop-filter: blur(5px);
    }

    /* Select box arrow color */
    div[data-testid="stSelectbox"] svg {
        fill: #000000 !important;
    }

    /* Select box hover/focus */
    div[data-testid="stSelectbox"] div[role="combobox"]:hover {
        border-color: rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
    }

    /* Select Box Dropdown Menu */
    div[data-baseweb="popover"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
    }

    /* Dropdown Items */
    div[data-baseweb="popover"] ul[role="listbox"] li {
        color: #000000 !important;
        transition: background-color 0.2s ease;
    }

    /* Dropdown Item on Hover */
    div[data-baseweb="popover"] ul[role="listbox"] li:hover {
        background-color: rgba(0, 0, 0, 0.05) !important;
    }

    /* Selected Dropdown Item */
    div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"] {
        background-color: rgba(0, 0, 0, 0.1) !important;
    }

    /* Selectbox Labels "From" and "To" */
    div[data-testid="stSelectbox"] label {
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }

    /* Translucent Input/Output Boxes */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #000000 !important;
        font-weight: 500;
    }
    
    /* General Text Visibility */
    h1, h2, h3, p, label, .stMarkdown {
        color: #000000;
        text-shadow: 0 1px 3px rgba(255,255,255,0.6);
    }

    /* Global Fade In Animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Smooth entry for text areas */
    div[data-testid="stTextArea"] {
        animation: slideIn 0.6s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Button Hover Effects */
    div.stButton > button:first-child {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Clear Button Style in Sidebar */
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent;
        border: 1px solid rgba(255, 255, 255, 0.7);
        color: #000000;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "history" not in st.session_state:
    st.session_state.history = []
if "source_lang" not in st.session_state:
    st.session_state.source_lang = "Auto Detect"
if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Spanish"
# ---------------- Session State for Output ----------------
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# ---------------- Load Lottie ----------------
def load_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

loading_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")
success_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_touohxv0.json")

# ---------------- Header ----------------
st.markdown("<h1 style='text-align:center; color:white; text-shadow: 0 2px 5px rgba(0,0,0,0.7);'>🌐 Language Translator</h1>", unsafe_allow_html=True)

# ---------------- Sidebar Controls ----------------
# ---------------- History ----------------
st.sidebar.markdown("<h3 style='color:black; text-shadow: 0 2px 4px rgba(0,0,0,0.5);'>📜 History</h3>", unsafe_allow_html=True)
if st.sidebar.button("Clear"):
    st.session_state.history = []

for i, item in enumerate(reversed(st.session_state.history)):
    with st.sidebar.expander(f"{item['src']} ➡ {item['tgt']}"):
        st.caption(f"**In:** {item['original'][:30]}...")
        st.write(f"**Out:** {item['translated']}")

# ---------------- Translator ----------------
translator = GoogleTranslator(source="auto")

lang_map = {name.capitalize(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}
language_names = sorted(lang_map.keys())

# ---------------- Language Selection ----------------
st.markdown("<h3 style='color:white; text-shadow: 0 2px 5px rgba(0,0,0,0.7);'>⚙️ Configuration</h3>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([3, 1, 3, 2])

def swap_languages():
    if st.session_state.source_lang == "Auto Detect":
        st.toast("⚠️ Cannot swap 'Auto Detect' with a specific language.")
    else:
        src = st.session_state.source_lang
        tgt = st.session_state.target_lang
        st.session_state.source_lang = tgt
        st.session_state.target_lang = src

with c1:
    source_language = st.selectbox("From", ["Auto Detect"] + language_names, key="source_lang")

with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("⇄", on_click=swap_languages, help="Swap Languages")

with c3:
    target_language = st.selectbox("To", language_names, key="target_lang")

with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    translate_btn = st.button("🚀 Translate", type="primary", use_container_width=True)

# ---------------- Layout ----------------
col1, col2 = st.columns(2)

def speak_text(text, lang):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay="true" style="display:none"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"TTS Error: {e}")

with col1:
    st.subheader("📝 Input Text")
    input_text = st.text_area("Input", height=300, placeholder="Type text here...", label_visibility="collapsed")
    
    # Input Controls
    ic1, ic2, ic3 = st.columns([1, 4, 1])
    with ic1:
        if st.button("🔊", key="tts_in", help="Listen to Input"):
            if input_text.strip():
                src_lang_code = "en" if source_language == "Auto Detect" else lang_map[source_language]
                speak_text(input_text, src_lang_code)
    with ic3:
        if st.button("📋", key="copy_in", help="Copy Input"):
            st.toast("Copied to clipboard!", icon="📋")
            components.html(f"""
                <script>
                    parent.navigator.clipboard.writeText({json.dumps(input_text)});
                </script>
            """, height=0)

with col2:
    st.subheader("✨ Translated Output")
    st.text_area("Output", value=st.session_state.translated_text, height=300, label_visibility="collapsed")
    
    # Output Controls
    oc1, oc2, oc3 = st.columns([1, 4, 1])
    with oc1:
        if st.button("🔊", key="tts_out", help="Listen to Output"):
            if st.session_state.translated_text.strip():
                speak_text(st.session_state.translated_text, lang_map[target_language])
    with oc3:
        if st.button("📋", key="copy_out", help="Copy Output"):
            st.toast("Copied to clipboard!", icon="📋")
            components.html(f"""
                <script>
                    parent.navigator.clipboard.writeText({json.dumps(st.session_state.translated_text)});
                </script>
            """, height=0)

# ---------------- Translation Logic ----------------
if translate_btn:
    if not input_text.strip():
        st.warning("⚠️ Please enter text to translate.")
    else:
        loader_placeholder = st.empty()
        with loader_placeholder:
            if loading_anim:
                st_lottie(loading_anim, height=150, key="loader")

            try:
                translator.source = "auto" if source_language == "Auto Detect" else lang_map[source_language]
                translator.target = lang_map[target_language]

                translated_text = translator.translate(input_text)
                st.session_state.translated_text = translated_text

                # ---------------- Add to History ----------------
                st.session_state.history.append({
                    "src": source_language,
                    "tgt": target_language,
                    "original": input_text,
                    "translated": translated_text
                })
                
                st.rerun()

            except Exception as e:
                st.error(f"Translation Error: {e}")
