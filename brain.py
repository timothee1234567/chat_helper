"""
The "brain" of the bot.

No network code lives here. It takes a message and business info, builds a
prompt, and calls whatever `ask_llm` function it's given. That means you
can test everything in this file offline with a fake ask_llm, and only
swap in a real one (llm_client.py) once you're online.
"""

SYSTEM_PROMPT_TEMPLATE = """You are a helpful customer service assistant for {business_name}.

Business info:
{business_info}

Answer customer questions using only the information above. If you don't
know the answer, say a team member will follow up — never invent details
like prices, hours, or addresses. Keep replies short and friendly, like a
text message.
"""


def build_system_prompt(business: dict) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        business_name=business["name"],
        business_info=business["info"],
    )


def get_reply(message: str, business: dict, ask_llm) -> str:
    """
    message:  the customer's message
    business: dict with "name" and "info" (see business.json)
    ask_llm:  a function(system_prompt, user_message) -> str
              Swap between the fake one (test_offline.py) and the real one
              (llm_client.py) without changing anything in this file.
    """
    system_prompt = build_system_prompt(business)
    return ask_llm(system_prompt, message)
