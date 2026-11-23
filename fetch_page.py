import io
import sys
import re
import requests
import trafilatura
from pypdf import PdfReader  # reads the text layer inside PDF files
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

# Why the most recent fetch failed. The test script reads this for the results table.
LAST_REASON = ""

# Phrases paywalls commonly use. Lowercase, since we lowercase the page before searching.
PAYWALL_PHRASES = [
    "subscribe to continue reading",
    "subscribe to read",
    "already a subscriber",
    "create a free account to continue",
    "to continue reading, please",
]

# Wording that shows up on captcha and login walls
# Short markers that survive different wording. "captcha" alone matches
# "fill out the captcha", "solve the captcha", "recaptcha", and so on.
BLOCK_PAGE_MARKERS = [
    "captcha",
    "cf-turnstile", "challenge-platform",   # code names used by Cloudflare's check
    "unusual traffic", "verify you are human", "are you a robot",
    'type="password"',                      # a password box means a login page
    "sign in to continue", "log in to continue",
]

def paywall_warning(html, text):
    """Return a short reason if the page looks paywalled, or None if it looks fine."""
    # Clue 1: the site labels the article as not free. The pattern allows for
    # optional quote marks and spaces around the word "false".
    if re.search(r'"isAccessibleForFree"\s*:\s*"?false"?', html, re.IGNORECASE):
        return "the publisher labels this article as subscriber-only"
    # Clue 2: paywall wording anywhere in the raw page
    lowered = html.lower()
    for phrase in PAYWALL_PHRASES:
        if phrase in lowered:
            return f'the page contains the phrase "{phrase}"'
    # Clue 3: weakest clue, so the message hedges
    if len(text.split()) < 150:
        return "the text is very short, so it may be cut off"
    return None
BOT_NAME = "BrowseBuddy"  # the name robots.txt rules are matched against
# Say who we are, instead of pretending to be a normal browser
HEADERS = {"User-Agent": f"Mozilla/5.0 (compatible; {BOT_NAME}/0.1; student research project)"}

def allowed_by_robots(url):
    """Return True if the site's robots.txt lets us read this URL."""
    parts = urlparse(url)  # splits the address into pieces (https, site name, path)
    try:
        r = requests.get(f"{parts.scheme}://{parts.netloc}/robots.txt",
                         headers=HEADERS, timeout=10)
    except requests.RequestException:
        return True            # couldn't reach it; the page download will fail on its own if the site is down
    if r.status_code >= 500:
        return False           # server error: the standard says play it safe
    if r.status_code != 200:
        return True            # no robots.txt file (404 etc.) means no restrictions
    rules = RobotFileParser()
    rules.parse(r.text.splitlines())   # we download the file ourselves so we control the timeout
    return rules.can_fetch(BOT_NAME, url)

def get_page_text(url):
    """Download a page or PDF and return its main text, or None if we can't read it."""
    global LAST_REASON
    LAST_REASON = ""  # reset so an old failure never carries over to a new page
    if not allowed_by_robots(url):
        LAST_REASON = "robots.txt: the site asks automated tools not to read this page"
        print("Not reading: blocked by the site's robots.txt.")
        return None
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        LAST_REASON = f"download error: {error}"
        print(f"Couldn't download the page: {error}")
        return None

    # The server labels what it sent. We also check the web address, since
    # a few servers label PDFs wrongly.
    label = response.headers.get("Content-Type", "").lower()
    if "pdf" in label or url.lower().endswith(".pdf"):
        # response.content is the raw file. BytesIO makes it behave like a
        # file on disk, which is what PdfReader expects.
        reader = PdfReader(io.BytesIO(response.content))
        # Pull text from each page; "or ''" covers pages with no text
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = trafilatura.extract(response.text)

        # Captcha/login wall: one of these phrases AND very little real text.
    # (Plenty of normal pages mention "captcha" in a comment form, so the
    # short-text condition keeps us from flagging them.)
    if "pdf" not in label and (not text or len(text.split()) < 150):
        lowered = response.text.lower()
        if any(marker in lowered for marker in BLOCK_PAGE_MARKERS):
            LAST_REASON = "captcha or login wall"
            print("Not reading: this looks like a captcha or login page.")
            return None

    # PDFs have no HTML to check, so only HTML pages get the paywall test
    if "pdf" not in label and text:
        warning = paywall_warning(response.text, text)
        if warning:
            LAST_REASON = f"paywall check: {warning}"
            print(f"Not summarizing: {warning}.")
            return None  # stop here, so no text ever reaches the model

    if not text or not text.strip():
        LAST_REASON = "no readable text (JavaScript page, login wall, or scanned PDF)"
        print("Downloaded, but no readable text found (JavaScript page, "
              "login wall, or a scanned PDF with no text layer).")
        return None
    return text

if __name__ == "__main__":
    text = get_page_text(sys.argv[1])
    if text:
        print(f"[{len(text.split())} words]\n")
        print(text[:2000])
        print("\n--- END OF TEXT ---\n", text[-500:])  # the last 500 characters