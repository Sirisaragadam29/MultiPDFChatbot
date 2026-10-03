# backend/memory.py

from collections import defaultdict


conversation_history = defaultdict(
    list
)


def get_history(
    session_id: str
):

    return conversation_history[
        session_id
    ]


def add_message(
    session_id: str,
    role: str,
    content: str
):

    conversation_history[
        session_id
    ].append({

        "role":
        role,

        "content":
        content
    })

    # Keep latest 20 messages
    conversation_history[
        session_id
    ] = conversation_history[
        session_id
    ][-20:]


def clear_history(
    session_id: str
):

    conversation_history[
        session_id
    ].clear()