"""
Indonesia Daily News Agent
- Fetches top Indonesian news via Claude AI (with web search)
- Sends a formatted summary to WhatsApp via Twilio
- Designed to run daily at 8am (via cron or cloud scheduler)

Requirements:
    pip install anthropic twilio schedule requests

Setup:
    1. Get a free API key at https://newsapi.org  (or just use Claude's web search)
    2. Sign up at https://twilio.com, enable WhatsApp Sandbox
    3. Fill in the config below
"""

import anthropic
import schedule
import time
from twilio.rest import Client
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────[...]

ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"   # https://console.anthropic.com

TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN  = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_FROM        = "whatsapp:+14155238886"    # Twilio sandbox number
YOUR_WHATSAPP      = "whatsapp:+62XXXXXXXXXX"  # Your number with country code

SEND_TIME          = "08:00"                   # 24-hour format, local machine time
TIMEZONE           = "Asia/Jakarta"            # WIB — make sure your server uses this TZ

# ─── FETCH NEWS VIA CLAUDE ────────────────────────────────────────────────────

def fetch_indonesia_news() -> str:
    """Ask Claude (with web search) for today's top Indonesian news."""
    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    today = datetime.now().strftime("%A, %d %B %Y")

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {today}. "
                    "Search for the top 5 news stories from major Indonesian news sources "
                    "such as Kompas, Detik, Tempo, CNN Indonesia, or Tribunnews. "
                    "The articles will likely be in Bahasa Indonesia — read and understand them, "
                    "then translate and summarize each story into clear, natural English. "
                    "Focus on major national topics: politics, economy, disasters, or society. "
                    "Format as a WhatsApp message like this:\n\n"
                    "📰 *Indonesia News Digest — {today}*\n\n"
                    "1. *[Translated headline]*\n"
                    "[2-3 sentence English summary translated from the original article]\n"
                    "📌 Source: [publication name]\n\n"
                    "...repeat for all 5 stories...\n\n"
                    "🤖 _Translated by Claude AI_\n\n"
                    "Do NOT write in Bahasa Indonesia — everything must be in English."
                )
            }
        ]
    )

    # Extract all text blocks from the response
    full_text = "\n".join(
        block.text for block in response.content if block.type == "text"
    )
    return full_text.strip()

# ─── SEND TO WHATSAPP ─────────────────────────────────────────────────────────[...]

def send_whatsapp(message: str):
    """Send a message to WhatsApp via Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        body=message,
        from_=TWILIO_FROM,
        to=YOUR_WHATSAPP
    )
    print(f"[{datetime.now()}] Message sent! SID: {msg.sid}")

# ─── MAIN JOB ───────────────────────────────────────────────────────────[...]

def run_news_job():
    print(f"[{datetime.now()}] Fetching Indonesia news...")
    try:
        news = fetch_indonesia_news()
        print("News fetched:\n", news[:300], "...\n")
        send_whatsapp(news)
    except Exception as e:
        print(f"Error: {e}")

# ─── SCHEDULER ──────────────────────────────────────────────────────────[...]

if __name__ == "__main__":
    print(f"Agent started. Will send news daily at {SEND_TIME} WIB.")

    schedule.every().day.at(SEND_TIME).do(run_news_job)

    # Uncomment the line below to test immediately without waiting:
    # run_news_job()

    while True:
        schedule.run_pending()
        time.sleep(30)
