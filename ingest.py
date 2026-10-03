# ingest.py

from backend.rag import ingest_folder


if __name__ == "__main__":

    print(
        "\nStarting PDF ingestion...\n"
    )

    results = ingest_folder(
        "documents"
    )

    if not results:

        print(
            "No PDF files found in the documents folder."
        )

    else:

        for result in results:

            if "error" in result:

                print(
                    f"❌ {result['file']}: "
                    f"{result['error']}"
                )

            else:

                print(
                    f"✅ {result['file']}"
                )

                print(
                    f"   Pages  : {result['pages']}"
                )

                print(
                    f"   Chunks : {result['chunks']}"
                )

    print(
        "\nPDF ingestion completed."
    )