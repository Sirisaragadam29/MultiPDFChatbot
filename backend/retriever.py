from .vector_store import get_vector_store


def retrieve_documents(query: str, k: int = 5):
    """
    Retrieves the most relevant document chunks
    from ChromaDB.
    """

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query,
        k=k
    )

    return documents


def format_context(documents):
    """
    Converts retrieved documents into
    readable context for the LLM.
    """

    if not documents:
        return ""

    context_parts = []

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown document"
        )

        page = document.metadata.get(
            "page"
        )

        text = document.page_content

        context_parts.append(
            f"Source: {source}\n"
            f"Page: {page + 1 if isinstance(page, int) else 'Unknown'}\n"
            f"Content:\n{text}"
        )

    return "\n\n---\n\n".join(
        context_parts
    )