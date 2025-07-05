import os, json
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import tweepy
from subprocess import run

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

# — Generate a progress‑bar image —
W, H = 800, 200
bar_w = int((pct / 100) * (W - 40))
img = Image.new("RGB", (W, H), color="white")
draw = ImageDraw.Draw(img)
draw.rectangle([20, 80, W-20, 120], outline="black", width=2)
draw.rectangle([20, 80, 20+bar_w, 120], fill="skyblue")
font = ImageFont.load_default()
txt = f"2025 is {pct}% complete"
w, h = draw.textsize(txt, font=font)
draw.text(((W-w)/2, 30), txt, fill="black", font=font)
img_path = "progress.png"
img.save(img_path)

# — Tweet it with media —
tweet_text = f"2025 is {pct}% complete!"
api.update_with_media(img_path, tweet_text)

# — Update state.json —
state["last_pct"] = pct
with open("state.json", "w") as f:
    json.dump(state, f)

# — Commit & push changes back to GitHub —
run(["git", "config", "user.name", "github-actions"])
run(["git", "config", "user.email", "actions@github.com"])
run(["git", "add", "state.json", "progress.png"])
run([
    "git", "commit", "-m",
    f"Update to {pct}%"
])
# Use the injected GITHUB_TOKEN to push:
repo = os.environ["GITHUB_REPOSITORY"]
run([
    "git", "push",
    f"https://x-access-token:{os.environ['GITHUB_TOKEN']}@github.com/{repo}.git",
    "HEAD:main"
])
