import os
import streamlit as st
from retrieval import retrieval_app
from ingestion import ingest_pdf
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
openai_key = os.getenv("OPENAI_KEY")

st.set_page_config(page_title="Finance RAG", page_icon="💰")
st.title("💰 AI Financial Assistant")

if "user" not in st.session_state:
    st.session_state.user = None

class user_statement_analysis(retrieval_app):
    def __init__(self, url, key, openai_key):
        super().__init__(url, key, openai_key)

@st.cache_resource
def init_connection():
    
    # Return the instance of your class
    return user_statement_analysis(url, key, openai_key)

app = init_connection()

with st.sidebar:
    st.header("🔐 Secure Login")

    if not st.session_state.user:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Log In"):
                try:
                    session = app.supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = session.user
                    st.success("✅ Logged in!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            if st.button("Sign Up"):
                try:
                    # Create new user in Supabase
                    session = app.supabase.auth.sign_up({"email": email, "password": password})
                    st.session_state.user = session.user
                    st.success("✅ Account created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info(f"👤 {st.session_state.user.email}")
        
        if st.button("Logout"):
            app.supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        st.divider()
        # after getting logged in
        if st.session_state.user:
            st.header("📂 Upload Data")
            uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type=["pdf"])
            
            if uploaded_file is not None:
                if st.button("Process & Ingest"):
                    with st.spinner("Extracting data... This may take a minute."):
                        try:
                            ingestor = ingest_pdf(url, key, openai_key)

                            user_id = st.session_state.user.id
                            ingestor.process_pdf(uploaded_file, user_id)
                            st.success("✅ Statement processed and stored securely!")
                        
                        except Exception as e:
                            st.error(f"❌ An error occurred: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("Ask about your finances..."):
    # Display User Message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add User Message to History
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get Response from your Backend
    if st.session_state.user:
        with st.spinner("Analyzing bank statement..."):
            user_id = st.session_state.user.id
            ai_response = app.response(prompt, user_id)

        with st.chat_message("assistant"):
            st.markdown(ai_response)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    else:
        # Polite warning instead of crashing
        warning_msg = "Please **Login** in the sidebar to access your financial data."
        with st.chat_message("assistant"):
            st.warning(warning_msg)
        st.session_state.messages.append({"role": "assistant", "content": warning_msg})
