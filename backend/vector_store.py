# backend/vector_store.py

import os
import shutil

from dotenv import load_dotenv
from langchain_chroma import Chroma

from .embeddings import get_embeddings


load_dotenv()


CHROMA_DIR = os.getenv(
    "CHROMA_DIR",
    "chroma_db"
)


COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "multipdf_documents"
)


# =========================================================
# GET VECTOR STORE
# =========================================================

def get_vector_store():

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store


# =========================================================
# ADD DOCUMENTS
# =========================================================

def add_documents(documents):

    if not documents:
        return 0

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents
    )

    return len(documents)


# =========================================================
# DELETE DOCUMENT BY SOURCE
# =========================================================

def delete_documents_by_source(
    source: str
):

    vector_store = get_vector_store()

    try:

        vector_store.delete(
            where={
                "source": source
            }
        )

        return True

    except Exception as error:

        print(
            f"Error deleting {source} "
            f"from ChromaDB: {error}"
        )

        return False


# =========================================================
# CLEAR ENTIRE VECTOR STORE
# =========================================================

def clear_vector_store():

    if os.path.exists(CHROMA_DIR):

        shutil.rmtree(
            CHROMA_DIR
        )