# chatbot.py

from backend.router import route_message
from backend.rag import answer_question


def chat(query: str):

    route = route_message(
        query
    )

    if route == "greeting":

        return (
            "Hi! 👋 I'm your MultiPDF "
            "learning assistant."
        )

    if route == "conversation":

        return (
            "I'm your MultiPDF learning assistant. "
            "Upload your PDFs and ask me questions. 😊"
        )

    result = answer_question(
        query=query,
        route=route
    )

    return result["answer"]


if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "      MultiPDF Chatbot"
    )

    print(
        "================================"
    )

    print(
        "Type 'exit' to stop.\n"
    )


    while True:

        query = input(
            "You: "
        ).strip()

        if query.lower() == "exit":

            print(
                "Goodbye! 👋"
            )

            break

        try:

            answer = chat(
                query
            )

            print(
                "\nBot:",
                answer
            )

            print()

        except Exception as error:

            print(
                "\nError:",
                error
            )