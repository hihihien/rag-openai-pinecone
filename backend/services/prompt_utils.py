import openai
from typing import List, Dict
from services.embeddings import detect_lang

CHAT_MODEL = "gpt-4o-mini"

def ask_openai(context: str, question: str, history: List[Dict[str, str]]) -> str:
    lang = detect_lang(question)

    # Build system prompt with richer role description
    system_msg = {
        "de": (
            "Du bist ein akademischer Assistent für den Fachbereich Medien der Hochschule Düsseldorf. "
            "Verwende den gegebenen Kontext, der sowohl aus Modulhandbüchern als auch von offiziellen Studiengangsseiten stammen kann. "
            "Beantworte die Fragen sachlich und präzise. "
            "Wenn im Kontext keine passende Information enthalten ist, sage ehrlich, dass du keine Antwort hast."
        ),
        "en": (
            "You are an academic assistant for the Faculty of Media at the University of Applied Sciences Düsseldorf. "
            "Use the provided context, which may include information from both module handbooks and official study program websites. "
            "Answer factually and precisely. "
            "If the context does not contain the relevant information, state that clearly."
        ),
    }

    # Convert conversation history into messages (keep only recent turns)
    messages = [{"role": "system", "content": system_msg[lang]}]
    MAX_TURNS = 3
    if history:
        trimmed_history = history[-(MAX_TURNS * 2):]  # last 3 turns (Q&A)
        for h in trimmed_history:
            messages.append({"role": h["role"], "content": h["content"]})

    # Combine context and question into the user prompt
    user_prompt = (
        f"Kontext:\n{context}\n\nFrage: {question}" if lang == "de"
        else f"Context:\n{context}\n\nQuestion: {question}"
    )
    messages.append({"role": "user", "content": user_prompt})

    # Call OpenAI
    try:
        response = openai.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return (
            "Fehler beim Generieren der Antwort. Bitte versuche es später erneut."
            if lang == "de"
            else "An error occurred while generating the response. Please try again later."
        )
