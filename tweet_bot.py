import os, json
from datetime import date
from subprocess import run
import tweepy

# — Load Twitter creds from ENV —
api_key     = os.environ["API_KEY"]
api_secret  = os.environ["API_SECRET"]
access_tok  = os.environ["ACCESS_TOKEN"]
access_sec  = os.environ["ACCESS_SECRET"]

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_tok, access_sec)
api  = tweepy.API(auth)

# — Load last tweeted percentage —
with open("state.json") as f:
    state = json.load(f)

# — Compute today’s percentage of 2025 —
start = date(2025, 1, 1)
end   = date(2026, 1, 1)
today = date.today()
pct   = int(((today - start).days / (end - start).days) * 100)

# — Only proceed if pct > last_pct —
if pct <= state["last_pct"]:
    print(f"No increase (last={state['last_pct']}%, now={pct}%). Exiting.")
    exit(0)

# — Compose tweet text (emoji style) —
tweet_text = f"📆 {today.strftime('%B %d, %Y')}\n🟦 2025 is {pct}% complete!\n⏳ Keep going! 💪✨"

# — Send text-only tweet —
api.update_status(status=tweet_text)

# — Update state.json —
state["last_pct"] = pct
with open("state.json", "w") as f:
    json.dump(state, f)

# — Commit & push changes back to GitHub —
run(["git", "config", "user.name", "github-actions"])
run(["git", "config", "user.email", "actions@github.com"])
run(["git", "add", "state.json"])
run([
    "git", "commit", "-m",
    f"Update to {pct}%"
])
repo = os.environ["GITHUB_REPOSITORY"]
run([
    "git", "push",
    f"https://x-access-token:{os.environ['GITHUB_TOKEN']}@github.com/{repo}.git",
    "HEAD:main"
])
