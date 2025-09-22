import openai
from typing import List, Dict
from backend.services.embeddings import detect_lang

CHAT_MODEL = "gpt-4o-mini"

def ask_openai(context: str, question: str, history: List[Dict[str, str]]) -> str:
    lang = detect_lang(question)
    
    #build system prompt
    system_msg = {
        "de": "Du bist ein akademischer Assistent. Antworte nur mit dem gegebenen Kontext. Wenn du nichts findest, sage es deutlich.",
        "en": "You are an academic assistant. Only use the context. If you can't find anything, say so."
    }

    # convert history to messages
    messages = [{"role": "system", "content": system_msg[lang]}]

    #sliding cutoff history to keep only last 3 turns (Q&A pairs)
    MAX_TURNS = 3
    if history:
        trimmed_history = history[-(MAX_TURNS * 2):] # each turn has 2 messages (user and assistant)
        for h in trimmed_history:
            messages.append({"role": h["role"], "content": h["content"]})

    # add current question with context
    user_prompt = (
        f"Kontext:\n{context}\n\nFrage: {question}" if lang == "de"
        else f"Context:\n{context}\n\nQuestion: {question}"
    )
    messages.append({"role": "user", "content": user_prompt})

    #ask OpenAI
    response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.2
    )   
    return response.choices[0].message.content
