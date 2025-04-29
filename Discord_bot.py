import os
import requests
import asyncio
from dotenv import load_dotenv

import cloudscraper
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ─── Environment ──────────────────────────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN    = os.getenv("DISCORD_TOKEN")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CHANNEL_ID       = int(os.getenv("CHANNEL_ID"))


# instead of requests.Session()
session = cloudscraper.create_scraper(
    browser={
      "browser": "chrome",      # emulate Chrome
      "platform": "windows",    # on Windows
      "mobile": False
    }
)

# now you can do exactly the same sequence:
session.get("https://leetcode.com/")   # passes CF challenge
print(session.cookies)  # prints CF clearance cookie
csrf = session.cookies.get("csrftoken")

# Set all the cookies from the cURL’s `-b` string
session.cookies.update({
    "csrftoken":       csrf,
    "LEETCODE_SESSION": os.getenv("LEETCODE_SESSION"),
})

# Copy the non-cookie headers
session.headers.update({
    "Accept":             "*/*",
    "Accept-Language":    "en-US,en;q=0.9",
    "Content-Type":       "application/json",
    "Origin":             "https://leetcode.com",
    "Referer":            "https://leetcode.com/company/facebook/?favoriteSlug=facebook-thirty-days",
    "Sec-Fetch-Dest":     "empty",
    "Sec-Fetch-Mode":     "cors",
    "Sec-Fetch-Site":     "same-origin",
    "User-Agent":         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "X-CSRFToken":        csrf,
    "uuuserid":           "eaf8d5eb73257fc8a86580164cd7eda0",
})

COMPANIES   = {
    "microsoft": "Microsoft",
    "google":    "Google",
    "amazon":    "Amazon",
    "facebook":  "Meta",
}


    # ─── Build & send your GraphQL query ───────────────────────────────────────────
def fetch_top_questions(company_slug: str,
                        limit: int = 30,
                        days: int = 30):
    query = """
    query favoriteQuestionList(
        $favoriteSlug: String!,
        $filter: FavoriteQuestionFilterInput,
        $filtersV2: QuestionFilterInput,
        $sortBy: QuestionSortByInput,
        $limit: Int,
        $skip: Int,
        $version: String = "v2"
    ) {
        favoriteQuestionList(
        favoriteSlug: $favoriteSlug,
        filter: $filter,
        filtersV2: $filtersV2,
        sortBy: $sortBy,
        limit: $limit,
        skip: $skip,
        version: $version
        ) {
        questions {
            title
            titleSlug
            difficulty
            frequency
        }
        }
    }
    """

    # Build the favoriteSlug e.g. "amazon-thirty-days"
    favorite_slug = f"{company_slug}-thirty-days"

    variables = {
    "favoriteSlug": favorite_slug,
    "sortBy":       {"sortField": "FREQUENCY", "sortOrder": "DESCENDING"},
    "limit":        limit,
    "skip":         0
    }

    payload = {
    "operationName": "favoriteQuestionList",
    "query":         query,
    "variables":     variables
    }
    
    resp = session.post("https://leetcode.com/graphql/", json=payload)
    #resp.raise_for_status()
    data = resp.json()
    # print(data)
    return data["data"]["favoriteQuestionList"]["questions"]

async def post_weekly():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"⚠️ Channel {CHANNEL_ID} not found.")
        return

    # Send a separate embed for each company
    for slug, pretty_name in COMPANIES.items():
        embed = discord.Embed(
            title=f"📊 Top 30 LeetCode Questions – {pretty_name}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        try:
            qs = fetch_top_questions(slug)
        except Exception as e:
            embed.description = f"Error fetching data: {e}"
        else:
            # Build up to 30 lines of markdown
            lines = [
                f"[{q['title']}](https://leetcode.com/problems/{q['titleSlug']}/) — "
                f"{q['difficulty']} — freq {q.get('frequency', 'N/A')}"
                for q in qs[:30]
            ]
            embed.description = "\n".join(lines) or "*(no questions returned)*"

        await channel.send(embed=embed)

# ─── Bot Definition ──────────────────────────────────────────────────────────
intents = discord.Intents.default()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This runs *before* on_ready, within the actual event loop.
        loop = asyncio.get_running_loop()
        scheduler = AsyncIOScheduler(event_loop=loop)
        scheduler.add_job(
            post_weekly,
            trigger="cron",
            day_of_week="wed",
            hour=17,
            minute=26
        )
        scheduler.start()
        # If you need to reference it later:
        self.scheduler = scheduler

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run(DISCORD_TOKEN)
