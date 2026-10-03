# backend/api.py

import os
from pathlib import Path

from flask import (
    Flask,
    request,
    jsonify
)

from flask_cors import CORS

from werkzeug.utils import secure_filename

from .router import route_message

from .rag import (
    ingest_pdf,
    answer_question
)

from .memory import (
    add_message,
    get_history,
    clear_history
)

from .vector_store import (
    delete_documents_by_source
)


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(
    __name__
)

CORS(
    app
)


ALLOWED_EXTENSIONS = {
    "pdf"
}


DOCUMENTS_FOLDER = Path(
    "documents"
)

DOCUMENTS_FOLDER.mkdir(
    exist_ok=True
)


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(
    filename: str
):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
        "ok",

        "message":
        "MultiPDF Chatbot API is running."
    })


# =========================================================
# LIST UPLOADED PDFS
# =========================================================

@app.route(
    "/documents",
    methods=["GET"]
)
def list_documents():

    try:

        pdf_files = sorted(
            [
                file.name
                for file in DOCUMENTS_FOLDER.glob(
                    "*.pdf"
                )
            ],
            key=str.lower
        )


        return jsonify({

            "files":
            pdf_files

        })


    except Exception as error:

        return jsonify({

            "error":
            str(error)

        }), 500


# =========================================================
# UPLOAD PDF FILES
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_files():

    files = request.files.getlist(
        "files"
    )


    if not files:

        return jsonify({

            "error":
            "No PDF files were uploaded."

        }), 400


    results = []


    for file in files:

        if not file.filename:

            continue


        if not allowed_file(
            file.filename
        ):

            return jsonify({

                "error":
                f"Only PDF files are supported: "
                f"{file.filename}"

            }), 400


        filename = secure_filename(
            file.filename
        )


        if not filename:

            results.append({

                "file":
                file.filename,

                "error":
                "Invalid filename."

            })

            continue


        pdf_path = (
            DOCUMENTS_FOLDER
            / filename
        )


        try:

            # ---------------------------------------------
            # If PDF already exists, remove old chunks
            # ---------------------------------------------

            if pdf_path.exists():

                delete_documents_by_source(
                    filename
                )


            # ---------------------------------------------
            # Save PDF permanently
            # ---------------------------------------------

            file.save(
                str(pdf_path)
            )


            # ---------------------------------------------
            # Process PDF
            # ---------------------------------------------

            result = ingest_pdf(
                str(pdf_path)
            )


            results.append(
                result
            )


        except Exception as error:

            results.append({

                "file":
                filename,

                "error":
                str(error)

            })


    return jsonify({

        "message":
        "PDF processing completed.",

        "files":
        results

    })


# =========================================================
# DELETE ONE PDF
# =========================================================

@app.route(
    "/documents/<filename>",
    methods=["DELETE"]
)
def delete_document(
    filename
):

    filename = secure_filename(
        filename
    )


    if not filename:

        return jsonify({

            "error":
            "Invalid filename."

        }), 400


    if not allowed_file(
        filename
    ):

        return jsonify({

            "error":
            "Only PDF files can be deleted."

        }), 400


    pdf_path = (
        DOCUMENTS_FOLDER
        / filename
    )


    try:

        # ---------------------------------------------
        # Delete PDF chunks from ChromaDB
        # ---------------------------------------------

        vector_deleted = (
            delete_documents_by_source(
                filename
            )
        )


        # ---------------------------------------------
        # Delete actual PDF file
        # ---------------------------------------------

        if pdf_path.exists():

            pdf_path.unlink()

        else:

            return jsonify({

                "error":
                "PDF file not found."

            }), 404


        return jsonify({

            "message":
            f"{filename} deleted successfully.",

            "vector_data_deleted":
            vector_deleted

        })


    except Exception as error:

        return jsonify({

            "error":
            str(error)

        }), 500


# =========================================================
# CHAT
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json(
        silent=True
    ) or {}


    query = (
        data.get("message")
        or ""
    ).strip()


    session_id = data.get(
        "session_id",
        "default"
    )


    if not query:

        return jsonify({

            "error":
            "Message cannot be empty."

        }), 400


    route = route_message(
        query
    )


    # -----------------------------------------------------
    # Greeting
    # -----------------------------------------------------

    if route == "greeting":

        answer = (
            "Hi! I'm your MultiPDF "
            "learning assistant. "
            "Upload your PDFs and ask me questions."
        )


        return jsonify({

            "answer":
            answer,

            "route":
            route,

            "sources":
            []

        })


    # -----------------------------------------------------
    # Conversation
    # -----------------------------------------------------

    if route == "conversation":

        answer = (
            "I'm your MultiPDF learning assistant. "
            "I can help you understand topics from "
            "your uploaded PDFs."
        )


        return jsonify({

            "answer":
            answer,

            "route":
            route,

            "sources":
            []

        })


    # -----------------------------------------------------
    # Answer Question
    # -----------------------------------------------------

    try:

        result = answer_question(
            query=query,
            route=route
        )


    except Exception as error:

        return jsonify({

            "error":
            str(error)

        }), 500


    # -----------------------------------------------------
    # Save Chat Memory
    # -----------------------------------------------------

    add_message(
        session_id,
        "user",
        query
    )


    add_message(
        session_id,
        "assistant",
        result["answer"]
    )


    return jsonify({

        "answer":
        result["answer"],

        "route":
        route,

        "sources":
        result["sources"],

        "history_length":
        len(
            get_history(
                session_id
            )
        )

    })


# =========================================================
# CLEAR CHAT MEMORY
# =========================================================

@app.route(
    "/clear-memory",
    methods=["POST"]
)
def clear_chat_memory():

    data = request.get_json(
        silent=True
    ) or {}


    session_id = data.get(
        "session_id",
        "default"
    )


    clear_history(
        session_id
    )


    return jsonify({

        "message":
        "Chat history cleared."

    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )