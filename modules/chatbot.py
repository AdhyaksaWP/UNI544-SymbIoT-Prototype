import streamlit as st
import google.generativeai as genai

def run():
    st.title("🤖 Chatbot Gemini")

    # Tambahkan style untuk jawaban chatbot
    st.markdown("""
        <style>
        .chat-assistant {
            background-color: #f0f0f0;
            color: black;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .chat-user {
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Ambil API key
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)

    # Model Gemini 1.5 Flash
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Tanyakan sesuatu ke Gemini...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        try:
            response = model.generate_content(user_input)
            st.session_state.chat_history.append(("assistant", response.text))
        except Exception as e:
            st.error(f"Terjadi error: {e}")

    # Tampilkan riwayat chat
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            if role == "assistant":
                st.markdown(f'<div class="chat-assistant">{msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg}</div>', unsafe_allow_html=True)