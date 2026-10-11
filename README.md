# AI Customer Service Bot — Zero-Cost Build

## Where money could have entered, and how it's zeroed out

There are only two places this project costs anything: the AI model calls,
and the hosting. Both are now set to genuinely free options that need no
credit card:

- **AI calls** — llm_client.py now uses **Groq** instead of Anthropic.
  Groq's free tier (30 requests/minute, ~14,400/day) needs only an email
  to sign up, no card. Free tiers can change their terms over time, but
  this is currently the most generous no-card option available.
- **Hosting** — **Render**'s free web service tier needs no card either.
  The trade-off: it sleeps after 15 minutes with no traffic, and the
  first message after a quiet spell takes 30-60 seconds to get a reply
  while it wakes up. For a small business bot that's an acceptable
  trade for $0.

## Files

- **brain.py** — the reply logic. Unchanged, no network code.
- **business.json** — editable facts about the business. Unchanged.
- **test_offline.py** — offline tester with a fake LLM. Unchanged, still
  completely free to run.
- **llm_client.py** — now calls Groq instead of Anthropic.
- **webhook_server.py** — NEW. A small Flask server that Telegram sends
  messages to, built specifically to work with Render's sleep-and-wake
  free tier. This is the one to deploy.
- **telegram_bot.py** — the original Telethon version. Keep this around
  only if you later move to an always-on host (e.g. Oracle Cloud's free
  tier, which is also $0 but requires a card on file for identity
  verification, even though it's never charged). Render needs no card at
  all, which is why webhook_server.py is the recommended path for now.
- **requirements.txt** — NEW. `flask`, `requests`, `groq`.

One simplification: webhook_server.py only needs a BOT_TOKEN from
@BotFather. You no longer need API_ID/API_HASH from my.telegram.org at
all — those are specific to Telethon's style of connecting, which this
approach doesn't use.

## This week, offline

Same as before — `python test_offline.py`, edit `business.json`. Still
completely free, no dependencies beyond the standard library.

## Next WiFi window

1. `pip install flask requests groq`
2. Get a free Groq key at console.groq.com/keys (email only, no card),
   set it as `GROQ_API_KEY`.
3. Test it in isolation:
   ```python
   from llm_client import real_llm
   print(real_llm("You are a helpful assistant.", "Say hello."))
   ```
4. Get a BOT_TOKEN from @BotFather on Telegram.
5. Push this folder to a GitHub repo.
6. On render.com, create a free account (no card), then "New Web
   Service" connected to that repo. Set `GROQ_API_KEY` and
   `TELEGRAM_BOT_TOKEN` as environment variables in Render's dashboard.
   Render will run `python webhook_server.py` automatically once it
   detects requirements.txt.
7. Once deployed, Render gives you a public URL. Register it with
   Telegram once (you can do this from your phone's browser, no code
   needed):
   `https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_RENDER_URL>/webhook`
8. Message your bot on Telegram and confirm you get a real AI reply.

From that point on, it runs continuously at $0 — no card, no ongoing
cost — independent of your own WiFi schedule.
