"""
Test the bot completely offline, using a fake "LLM" that just shows you
what prompt WOULD have been sent, instead of making a real API call.

This confirms your business.json and prompt-building logic are correct
before you spend any API credits or need a connection at all.

Usage:
    python test_offline.py
"""

import json

from brain import get_reply


def fake_llm(system_prompt: str, user_message: str) -> str:
    print("\n--- Prompt that would be sent to the model ---")
    print(system_prompt)
    print(f"Customer: {user_message}")
    print("--- end prompt ---\n")
    return "[placeholder reply — plug in llm_client.py once you're online for a real answer]"


def main():
    with open("business.json", "r", encoding="utf-8") as f:
        business = json.load(f)

    print("Offline bot tester. Type a customer message, or 'quit' to exit.\n")
    while True:
        message = input("Customer: ").strip()
        if message.lower() in ("quit", "exit"):
            break
        if not message:
            continue
        print(f"Bot: {get_reply(message, business, fake_llm)}\n")


if __name__ == "__main__":
    main()
