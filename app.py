import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os
import datetime

# ✅ Define Gemini API Key
genai.configure(api_key="AIzaSyBYJvAGWjDCVtFmPKgqPNFEwWAoAgf2WEU")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-pro")

translator = GoogleTranslator()
recognizer = sr.Recognizer()

# User Authentication
USERNAME = "admin"
PASSWORD = "password"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "search_history" not in st.session_state:
    st.session_state.search_history = []

def login_page():
    st.set_page_config(page_title="🔐 Login | Slang Decoder", page_icon="🔑", layout="centered")
    st.title("🔐 Login to Slang Decoder")
    username = st.text_input("Enter Username:")
    password = st.text_input("Enter Password:", type="password")
    if st.button("Sign In"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again!")

if not st.session_state.logged_in:
    login_page()
else:
    st.set_page_config(page_title="🌍 Slang Decoder Pro", page_icon="🔥", layout="wide")
    
    # Sidebar Navigation
    st.sidebar.title("🔄 Menu")
    if st.sidebar.button("🏠 Home"):
        st.sidebar.info("Coming Soon!")
    if st.sidebar.button("📜 Recent History"):
        if st.session_state.search_history:
            for entry in reversed(st.session_state.search_history):
                st.sidebar.markdown(f'📌 {entry["search"]} ({entry["date"].strftime("%Y-%m-%d %H:%M:%S")})')
        else:
            st.sidebar.info("No recent history available.")
    
    if st.sidebar.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    # UI Header
    st.markdown("""
        <div style="text-align: center; background: #708090; padding: 20px; border-radius: 15px; color: white;">
            <h1>🔥 Slang Decoder Pro</h1>
            <p>Decode and translate slang phrases effortlessly!</p>
        </div>
    """, unsafe_allow_html=True)

    # Language Selection
    languages = {"English": "en", "Hindi (हिन्दी)": "hi", "Bengali (বাংলা)": "bn", "Spanish": "es"}
    
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("🌎 Translate from:", list(languages.keys()))
    with col2:
        target_lang = st.selectbox("🎯 Translate to:", list(languages.keys()))
    
    # Input Mode Selection
    st.markdown("#### 🎧 Select Input Method")
    mode = st.radio("Choose an input method:", ["✍ Text Input", "🎤 Microphone Input", "🎵 Audio File Input"], horizontal=True)
    
    # Gemini API Call
    def get_slang_meaning(sentence):
        try:
            response = model.generate_content(f"Explain this slang phrase: {sentence}")
            return response.text if response else "No explanation received"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def translate_text(text, src, dest):
        try:
            return GoogleTranslator(source=src, target=dest).translate(text)
        except Exception as e:
            return f"❌ Translation Error: {str(e)}"
    
    def text_to_speech(text, lang):
        try:
            tts = gTTS(text=text, lang=lang)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            return temp_file.name
        except Exception as e:
            return None
    
    detected_text = ""
    if mode == "✍ Text Input":
        user_input = st.text_area("Enter your slang phrase here:")
        detected_text = user_input
    elif mode == "🎵 Audio File Input":
        audio_file = st.file_uploader("Upload an audio file (WAV/MP3):", type=["wav", "mp3"])
        if audio_file:
            st.warning("Audio processing feature not yet implemented for Gemini API")
    elif mode == "🎤 Microphone Input":
        if st.button("🎤 Record from Microphone"):
            st.warning("Microphone processing feature not yet implemented for Gemini API")
    
    if detected_text:
        if "❌" not in detected_text:
            translated_text = translate_text(detected_text, languages[source_lang], "en")
            slang_meaning = get_slang_meaning(translated_text)
            final_translation = translate_text(slang_meaning, "en", languages[target_lang])
            st.success(f"💬 Meaning in {target_lang}: {final_translation}")
            st.session_state.search_history.append({"date": datetime.datetime.now(), "search": detected_text})
            audio_path = text_to_speech(final_translation, languages[target_lang])
            if audio_path:
                st.audio(audio_path, format="audio/mp3")
                os.remove(audio_path)
        else:
            st.warning("⚠ Could not process input. Please try again!")
    
    st.markdown("---")
    st.markdown("👨‍💻 Built with ❤ using Streamlit, Gemini AI, Google Translate & Speech Recognition")