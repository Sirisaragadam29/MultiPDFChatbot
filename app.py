# app.py

import json
import requests
import streamlit as st
import uuid
from pathlib import Path

API_URL = "http://127.0.0.1:5000"

HISTORY_FILE = Path("chat_history.json")


st.set_page_config(
    page_title="MultiPDF Chatbot",
    page_icon=":material/picture_as_pdf:",
    layout="wide"
)


# =========================================================
# CHAT HISTORY FUNCTIONS
# =========================================================

def load_chat_history():

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception:
        return []


def save_chat_history(history):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=2,
            ensure_ascii=False
        )


def save_current_chat():

    messages = st.session_state.messages

    if not messages:
        return

    history = load_chat_history()

    chat_id = st.session_state.session_id

    existing_chat = None

    for chat in history:

        if chat["id"] == chat_id:
            existing_chat = chat
            break

    user_questions = [
        message["content"]
        for message in messages
        if message["role"] == "user"
    ]

    if not user_questions:
        return

    title = user_questions[0]

    if len(title) > 45:
        title = title[:45] + "..."

    if existing_chat:

        existing_chat["messages"] = messages

        existing_chat["title"] = title

    else:

        history.append({
            "id": chat_id,
            "title": title,
            "messages": messages
        })

    save_chat_history(history)


def open_chat(chat_id):

    history = load_chat_history()

    for chat in history:

        if chat["id"] == chat_id:

            st.session_state.session_id = chat["id"]

            st.session_state.messages = chat["messages"]

            return


def delete_chat(chat_id):

    history = load_chat_history()

    history = [
        chat
        for chat in history
        if chat["id"] != chat_id
    ]

    save_chat_history(history)


def start_new_chat():

    save_current_chat()

    st.session_state.session_id = str(uuid.uuid4())

    st.session_state.messages = []


# =========================================================
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(uuid.uuid4())


if "messages" not in st.session_state:

    st.session_state.messages = []


if "documents" not in st.session_state:

    st.session_state.documents = []


# =========================================================
# PDF FUNCTIONS
# =========================================================

def load_documents():

    try:

        response = requests.get(
            f"{API_URL}/documents",
            timeout=10
        )

        if response.ok:

            return response.json().get(
                "files",
                []
            )

    except requests.RequestException:

        pass

    return []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("MultiPDF")

    st.caption(
        "Student Learning Assistant"
    )

    st.divider()


    # =====================================================
    # UPLOAD PDFs
    # =====================================================

    st.subheader("Upload PDFs")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )


    if st.button(
        "Process PDFs",
        icon=":material/upload_file:",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning(
                "Please select at least one PDF."
            )

        else:

            files = []

            for file in uploaded_files:

                files.append(
                    (
                        "files",
                        (
                            file.name,
                            file.getvalue(),
                            "application/pdf"
                        )
                    )
                )


            try:

                response = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    timeout=180
                )


                if response.ok:

                    data = response.json()

                    for item in data.get(
                        "files",
                        []
                    ):

                        if "error" in item:

                            st.error(
                                f"{item['file']}: "
                                f"{item['error']}"
                            )

                        else:

                            st.success(
                                f"{item['file']} processed"
                            )

                    st.session_state.documents = (
                        load_documents()
                    )

                else:

                    st.error(response.text)


            except requests.RequestException:

                st.error(
                    "Backend is not running."
                )

    # =====================================================
    # NEW CHAT
    # =====================================================

    st.divider()

    if st.button(
        "New Chat",
        icon=":material/add_comment:",
        use_container_width=True
    ):

        start_new_chat()

        st.rerun()


    # =====================================================
    # CLEAR CURRENT CHAT
    # =====================================================

    if st.button(
        "Clear Chat",
        icon=":material/delete_sweep:",
        use_container_width=True
    ):

        try:

            requests.post(
                f"{API_URL}/clear-memory",
                json={
                    "session_id":
                    st.session_state.session_id
                },
                timeout=10
            )

        except requests.RequestException:

            pass


        st.session_state.messages = []

        st.rerun()


    # =====================================================
    # UPLOADED PDFs
    # =====================================================

    st.divider()

    st.subheader("Uploaded PDFs")

    st.session_state.documents = (
        load_documents()
    )

    documents = st.session_state.documents


    if documents:

        for filename in documents:

            col1, col2 = st.columns(
                [5, 1]
            )


            with col1:

                st.caption(filename)


            with col2:

                delete_clicked = st.button(
                    "",
                    icon=":material/delete:",
                    key=f"delete_{filename}",
                    help=f"Delete {filename}"
                )


            if delete_clicked:

                try:

                    response = requests.delete(
                        f"{API_URL}/documents/{filename}",
                        timeout=30
                    )


                    if response.ok:

                        st.rerun()

                    else:

                        st.error(response.text)


                except requests.RequestException:

                    st.error(
                        "Could not connect to backend."
                    )


    else:

        st.caption(
            "No PDFs uploaded yet."
        )





    # =====================================================
    # CHAT HISTORY
    # =====================================================

    st.divider()

    st.subheader("Chat History")

    history = load_chat_history()


    if history:

        for chat in reversed(history):

            col1, col2 = st.columns(
                [5, 1]
            )


            with col1:

                clicked = st.button(
                    chat["title"],
                    key=f"history_{chat['id']}",
                    use_container_width=True
                )


            with col2:

                delete_history = st.button(
                    "",
                    icon=":material/delete:",
                    key=f"history_delete_{chat['id']}",
                    help="Delete chat"
                )


            if clicked:

                open_chat(chat["id"])

                st.rerun()


            if delete_history:

                delete_chat(chat["id"])

                st.rerun()


    else:

        st.caption(
            "No chat history yet."
        )


    # =====================================================
    # FEATURES
    # =====================================================

    st.divider()

    st.subheader("Features")

    st.write("Multiple PDF Upload")
    st.write("PDF Question Answering")
    st.write("Exam Answers")
    st.write("Comparisons & Summaries")
    st.write("Quiz Mode")
    st.write("Source References")


# =========================================================
# MAIN PAGE
# =========================================================

st.title("MultiPDF Chatbot")

st.caption(
    "Ask questions from your uploaded study materials."
)


# =========================================================
# DISPLAY CURRENT CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


        sources = message.get(
            "sources",
            []
        )


        if sources:

            st.markdown(
                "**Sources:**"
            )


            for source in sources:

                page = source.get(
                    "page"
                )


                if page:

                    st.caption(
                        f"{source['source']} "
                        f"— Page {page}"
                    )

                else:

                    st.caption(
                        source["source"]
                    )


# =========================================================
# CHAT INPUT
# =========================================================

query = st.chat_input(
    "Ask something about your PDFs..."
)


if query:

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })


    with st.chat_message("user"):

        st.markdown(query)


    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    f"{API_URL}/chat",

                    json={
                        "message": query,
                        "session_id":
                        st.session_state.session_id
                    },

                    timeout=180
                )


                if response.ok:

                    data = response.json()

                    answer = data.get(
                        "answer",
                        "No answer received."
                    )


                    sources = data.get(
                        "sources",
                        []
                    )


                    st.markdown(answer)


                    if sources:

                        st.markdown(
                            "**Sources:**"
                        )


                        for source in sources:

                            page = source.get(
                                "page"
                            )


                            if page:

                                st.caption(
                                    f"{source['source']} "
                                    f"— Page {page}"
                                )

                            else:

                                st.caption(
                                    source["source"]
                                )


                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })


                    # SAVE CHAT
                    save_current_chat()


                else:

                    st.error(
                        response.text
                    )


            except requests.RequestException as error:

                st.error(
                    "Could not connect to backend."
                )

                st.caption(
                    str(error)
                )