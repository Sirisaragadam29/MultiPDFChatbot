# backend/rag.py

import os
import time
from pathlib import Path

from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .vector_store import add_documents
from .retriever import retrieve_documents, format_context
from .llm import generate_answer


CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "800"
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        "120"
    )
)


# =========================================================
# EXTRACT PDF TEXT
# =========================================================

def extract_pdf_text(pdf_path: str):

    reader = PdfReader(
        pdf_path
    )

    documents = []


    for page_number, page in enumerate(
        reader.pages
    ):

        text = page.extract_text()


        if not text:
            continue


        text = text.strip()


        if not text:
            continue


        document = Document(

            page_content=text,

            metadata={
                "source":
                Path(pdf_path).name,

                "page":
                page_number
            }
        )


        documents.append(
            document
        )


    return documents


# =========================================================
# SPLIT DOCUMENTS
# =========================================================

def split_documents(
    documents
):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=CHUNK_SIZE,

        chunk_overlap=CHUNK_OVERLAP,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )


    chunks = splitter.split_documents(
        documents
    )


    return chunks


# =========================================================
# INGEST ONE PDF
# =========================================================

def ingest_pdf(
    pdf_path: str
):

    documents = extract_pdf_text(
        pdf_path
    )


    if not documents:

        raise ValueError(
            "No readable text found in the PDF."
        )


    chunks = split_documents(
        documents
    )


    number_of_chunks = add_documents(
        chunks
    )


    return {

        "file":
        Path(pdf_path).name,

        "pages":
        len(documents),

        "chunks":
        number_of_chunks
    }


# =========================================================
# INGEST PDF FOLDER
# =========================================================

def ingest_folder(
    folder="documents"
):

    folder_path = Path(
        folder
    )


    folder_path.mkdir(
        exist_ok=True
    )


    results = []


    pdf_files = sorted(
        folder_path.glob(
            "*.pdf"
        )
    )


    for pdf_file in pdf_files:

        try:

            result = ingest_pdf(
                str(pdf_file)
            )


            results.append(
                result
            )


        except Exception as error:

            results.append({

                "file":
                pdf_file.name,

                "error":
                str(error)

            })


    return results


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(
    query: str,
    route: str
):

    # -----------------------------------------------------
    # START TOTAL TIMER
    # -----------------------------------------------------

    start = time.time()


    # -----------------------------------------------------
    # RETRIEVE DOCUMENTS
    # -----------------------------------------------------

    documents = retrieve_documents(
        query
    )


    retrieval_time = (
        time.time() - start
    )


    print(
        f"[TIME] Retrieval: "
        f"{retrieval_time:.2f}s"
    )


    # -----------------------------------------------------
    # FORMAT CONTEXT
    # -----------------------------------------------------

    context = format_context(
        documents
    )


    if not context:

        return {

            "answer":
            "I couldn't find this information in the uploaded documents.",

            "sources":
            []

        }


    # -----------------------------------------------------
    # LLM RESPONSE
    # -----------------------------------------------------

    llm_start = time.time()


    answer = generate_answer(

        query=query,

        route=route,

        context=context

    )


    llm_time = (
        time.time() - llm_start
    )


    total_time = (
        time.time() - start
    )


    print(
        f"[TIME] LLM: "
        f"{llm_time:.2f}s"
    )


    print(
        f"[TIME] Total: "
        f"{total_time:.2f}s"
    )


    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    sources = []

    seen_sources = set()


    for document in documents:

        source = document.metadata.get(

            "source",

            "Unknown document"

        )


        page = document.metadata.get(
            "page"
        )


        key = (
            source,
            page
        )


        if key in seen_sources:

            continue


        seen_sources.add(
            key
        )


        sources.append({

            "source":
            source,

            "page":
            page + 1
            if isinstance(page, int)
            else None

        })


    return {

        "answer":
        answer,

        "sources":
        sources

    }