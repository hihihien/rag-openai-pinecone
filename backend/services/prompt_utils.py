import openai
from typing import List, Dict
from services.embeddings import detect_lang

CHAT_MODEL = "gpt-4o-mini"


def build_prompt(context: str, question: str, lang: str) -> List[Dict[str, str]]:
    system_msg = {
        "de": "Du bist ein akademischer Assistent. Antworte nur mit dem gegebenen Kontext. Wenn du nichts findest, sage es deutlich.",
        "en": "You are an academic assistant. Only use the context. If you can't find anything, say so."
    }

    user_prompt = (
        f"Kontext:\n{context}\n\nFrage: {question}" if lang == "de"
        else f"Context:\n{context}\n\nQuestion: {question}"
    )

    return [
        {"role": "system", "content": system_msg[lang]},
        {"role": "user", "content": user_prompt}
    ]


def ask_openai(context: str, question: str) -> str:
    lang = detect_lang(question)
    messages = build_prompt(context, question, lang)
    response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content
