# app.py

import streamlit as st
import tempfile
import os

from pdf_processor import extract_text_from_document
from chunking import chunk_text
from embeddings import create_embeddings
from vector_store import store_vectors, reset_vector_store
from audio_processor import extract_text_from_audio
from video_processor import extract_audio_from_video
from vision_processor import extract_text_from_image
from video_frames import extract_text_from_video_frames

# ---------------- SESSION STATE ---------------- #

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed" not in st.session_state:
    st.session_state.processed = False

if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "text_ready" not in st.session_state:
    st.session_state.text_ready = ""

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VIDORA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* ==================================================
FULL APP
================================================== */

.stApp{
    background:#eef2f7;
}

/* ==================================================
TOP NAVBAR
================================================== */

.navbar{
    position:fixed;
    top:0;
    left:0;

    width:100%;
    height:70px;

    background:#8fbcd7;

    display:flex;
    align-items:center;

    padding-left:25px;

    font-size:30px;
    font-weight:700;

    color:white;

    z-index:1000;

    border-bottom:1px solid #7eaac3;
}

/* ==================================================
SIDEBAR
================================================== */

section[data-testid="stSidebar"]{

    background:#d9dee7 !important;

    width:230px !important;

    min-width:230px !important;

    border-right:1px solid #bcc5d3;

    margin-top:70px;
}

/* FORCE SIDEBAR OPEN */

section[data-testid="stSidebar"][aria-expanded="false"]{

    min-width:320px !important;

    max-width:320px !important;

    transform:translateX(0px) !important;
}

/* Sidebar content */

section[data-testid="stSidebar"] > div{

    padding-top:10px;

    padding-left:20px;

    padding-right:20px;
}

/* Hide collapse button */

button[kind="header"]{

    display:none !important;
}


/* ==================================================
HISTORY BUTTONS
================================================== */

.stSidebar .stButton button{

    width:100%;

    background:white;

    color:#111827;

    border:none;

    border-radius:12px;

    padding:12px;

    text-align:left;

    margin-bottom:10px;

    font-size:15px;
}

.stSidebar .stButton button:hover{

    background:#cfe3ff;
}

/* ==================================================
UPLOAD BOX
================================================== */

.upload-box{

    background:transparent;

    border:none;

    padding:0;

    margin-bottom:20px;
}

/* ==================================================
USER MESSAGE
================================================== */

.user-bubble{

    background:#8fbcd7;

    color:white;

    padding:14px 18px;

    border-radius:18px;

    margin-left:30%;

    margin-bottom:14px;

    font-size:16px;
}

/* ==================================================
BOT MESSAGE
================================================== */

.bot-bubble{

    background:white;

    color:#111827;

    padding:14px 18px;

    border-radius:18px;

    margin-right:30%;

    margin-bottom:18px;

    font-size:16px;

    border:1px solid #d1d5db;
}

/* ==================================================
CHAT INPUT
================================================== */

.stChatInputContainer{

    background:#eef2f7;

    border-top:1px solid #d1d5db;
}

/* ==================================================
HIDE STREAMLIT DEFAULTS
================================================== */

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# NAVBAR
# =========================================================

st.markdown(
    """
    <div class="navbar">
        VIDORA
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SESSION STATES
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processed" not in st.session_state:
    st.session_state.processed = False

if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "text_ready" not in st.session_state:
    st.session_state.text_ready = ""

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <h2 style="
        color:#111827;
        font-size:28px;
        font-weight:700;
        margin-bottom:20px;
    ">
        📁 History
    </h2>
    """, unsafe_allow_html=True)

    if len(st.session_state.chat_sessions) == 0:

        st.info("No chats yet")

    else:

        for chat_name in reversed(
            list(st.session_state.chat_sessions.keys())
        ):

            if st.button(
                f"💬 {chat_name}",
                key=f"history_{chat_name}"
            ):

                old_chat = st.session_state.chat_sessions[
                    chat_name
                ]

                st.session_state.messages = old_chat[
                    "messages"
                ]

                st.session_state.current_chat = chat_name

                st.rerun()

# =========================================================
# FILE PROCESSING
# =========================================================

def process_file(temp_path, file_type):

    # ---------------- VIDEO ---------------- #

    if file_type in ["mp4", "mkv", "avi"]:

        st.info("🎬 Processing video (audio + visuals)...")

        audio_path = "temp_audio.wav"
        if os.path.exists(audio_path):
            os.remove(audio_path)

        audio_text = None
        visual_text = None

        try:
            extract_audio_from_video(temp_path, audio_path)
            audio_text = extract_text_from_audio(audio_path)
            print("AUDIO TEXT:")
            print(audio_text)
        except:
            audio_text = None

        try:
            visual_text = extract_text_from_video_frames(temp_path)
            print("VISUAL TEXT:")
            print(visual_text)
        except:
            visual_text = None

        def is_meaningful(text):
            return text and len(text.strip()) >= 40

        audio_ok = is_meaningful(audio_text)
        visual_ok = is_meaningful(visual_text)

        if audio_ok and visual_ok:
            return audio_text + "\n\n" + visual_text

        elif audio_ok:
            return audio_text

        elif visual_ok:
            return visual_text

        else:
            return None

    # ---------------- IMAGE ---------------- #

    elif file_type in ["jpg", "jpeg", "png"]:

        st.info("🖼️ Processing image...")
        return extract_text_from_image(temp_path)

    # ---------------- AUDIO ---------------- #

    elif file_type in ["mp3", "wav"]:

        st.info("🗣️ Processing audio...")

        try:
            return extract_text_from_audio(temp_path)
        except:
            return None

    # ---------------- DOCUMENT ---------------- #

    elif file_type in ["pdf", "docx", "txt"]:

        st.info("📄 Processing document...")
        return extract_text_from_document(temp_path)

    return None

# =========================================================
# MAIN AREA
# =========================================================


uploaded_file = st.file_uploader(
    "Upload File",
    type=[
        "pdf", "docx", "txt",
        "mp3", "wav",
        "mp4", "mkv", "avi",
        "jpg", "jpeg", "png"
    ],
    label_visibility="collapsed",
    key="main_uploader"
)


# =========================================================
# PROCESS NEW FILE
# =========================================================

# =========================================================
# FILE UPLOAD + CHAT HISTORY SYSTEM
# =========================================================
# ---------------------------------------------------------
# WHEN NEW FILE IS UPLOADED
# ---------------------------------------------------------

if uploaded_file:

    new_file_name = uploaded_file.name

    # NEW CHAT DETECTED
    if st.session_state.current_file != new_file_name:

        # SAVE OLD CHAT
        if (
            st.session_state.current_chat
            and len(st.session_state.messages) > 0
        ):

            st.session_state.chat_sessions[
                st.session_state.current_chat
            ] = {
                "messages": st.session_state.messages.copy()
            }

        # RESET CHAT
        st.session_state.messages = []

        st.session_state.processed = False

        st.session_state.current_file = new_file_name

        st.session_state.current_chat = new_file_name

    # -----------------------------------------------------
    # PROCESS FILE ONLY ONCE
    # -----------------------------------------------------

    if not st.session_state.processed:

        reset_vector_store()

        file_type = new_file_name.split(".")[-1].lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{file_type}"
        ) as tmp:

            tmp.write(uploaded_file.read())

            temp_path = tmp.name

        text = process_file(temp_path, file_type)


        # VALIDATION
        if not text:

            st.warning("No content found.")

            st.stop()

        # SAVE TEXT
        st.session_state.text_ready = text

        with open(
            "full_document.txt",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(text)

        # RAG
        chunks = chunk_text(text)

        embeddings, clean_chunks = create_embeddings(chunks)

        store_vectors(embeddings, clean_chunks)

        st.session_state.processed = True

# =========================================================
# CHAT DISPLAY
# =========================================================

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class="user-bubble">
                {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="bot-bubble">
                {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask anything about your uploaded content..."
)

# =========================================================
# QUESTION ANSWERING
# =========================================================

if question:

    if not st.session_state.processed:

        st.warning("⚠️ Please upload a file first.")
        st.stop()

    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    st.rerun()

# =========================================================
# GENERATE ANSWER
# =========================================================

if (
    len(st.session_state.messages) > 0
    and st.session_state.messages[-1]["role"] == "user"
):

    latest_question = st.session_state.messages[-1]["content"]

    from doc_scan import scan_document_for_counts
    from qa_engine import retrieve_answer, generate_answer

    with st.spinner("Thinking..."):

        scan_result = scan_document_for_counts(latest_question)

        if scan_result:
            answer = scan_result

        else:
            results = retrieve_answer(latest_question)

            context = "\n\n".join(results)

            answer = generate_answer(
                latest_question,
                context
            )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # SAVE CHAT TO HISTORY
    if st.session_state.current_chat:

        st.session_state.chat_sessions[
            st.session_state.current_chat
        ] = {
            "messages": st.session_state.messages.copy()
        }


    st.rerun()