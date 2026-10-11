"""
The real LLM call — using Groq's free tier, which needs no credit card
at all (unlike Anthropic/OpenAI, which require one for billing).

Setup (during a WiFi session):
    1. pip install groq
    2. Get a free key at https://console.groq.com/keys — sign up with
       just an email, no card required.
    3. Set it as an environment variable: GROQ_API_KEY=your-key-here
"""

import os

from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "your-api-key-here"))

# llama-3.3-70b-versatile is a strong free model on Groq. For faster,
# lighter replies at slightly lower quality, swap to "llama-3.1-8b-instant".
MODEL = "openai/gpt-oss-20b"


def real_llm(system_prompt: str, user_message: str) -> str:
    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return chat_completion.choices[0].message.content
