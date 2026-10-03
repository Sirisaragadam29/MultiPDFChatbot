# backend/router.py

def route_message(message: str):
    """
    Determines the type of user request.
    """

    text = message.lower().strip()

    # Greetings
    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if text in greetings:
        return "greeting"

    # General conversation
    conversation_phrases = [
        "thank you",
        "thanks",
        "are you mad",
        "what can you do",
        "who are you",
        "how are you"
    ]

    if any(phrase in text for phrase in conversation_phrases):
        return "conversation"

    # Comparison
    if (
        "compare" in text
        or "difference between" in text
        or "differentiate" in text
    ):
        return "compare"

    # Summary
    if (
        "summarize" in text
        or "summary" in text
        or "key points" in text
    ):
        return "summary"

    # Charts / diagrams
    if (
        "flowchart" in text
        or "bar chart" in text
        or "pie chart" in text
        or "graph" in text
        or "diagram" in text
    ):
        return "chart"

    # Exam answers
    if (
        "marks answer" in text
        or "5 marks" in text
        or "10 marks" in text
        or "exam answer" in text
    ):
        return "exam_answer"

    # Quiz
    if (
        "quiz me" in text
        or "quiz" in text
        or "test me" in text
    ):
        return "quiz"

    # Explanation
    if (
        text.startswith("explain")
        or "explain " in text
    ):
        return "explain"

    # Default: document question
    return "question"