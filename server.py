#To test, go to http://127.0.0.1:8000/docs?

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # describes what a request must contain

import fetch_page
from fetch_page import get_page_text
from chat import chat_about_page, MAX_CHARS

app = FastAPI()

# Chrome blocks extensions from talking to servers unless the server says
# it's okay. "*" means "anyone"; adjust this later if time permits
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# The server's memory: session id -> page text and chat so far.
# It vanishes when the server stops, which is fine for a proof of concept.
SESSIONS = {}

class StartRequest(BaseModel):   # a /start request must contain a url
    url: str

class AskRequest(BaseModel):     # an /ask request must contain these two things
    session_id: str
    question: str

def friendly_error(reason):
    """Turn the short reason from fetch_page into a message a person can read."""
    if reason.startswith("paywall"):
        return "This page appears to be behind a paywall, so I won't read it."
    if reason.startswith("download"):
        return "The site wouldn't let me download this page (some sites block automated access)."
    if reason.startswith("captcha"):
        return "This page asks for a captcha or login, which I can't get past."
    if reason.startswith("robots"):
        return "This site's robots.txt asks automated tools not to read this page, so I won't."
    return "I couldn't find readable text on this page (it may need JavaScript, a login, or be a scanned PDF)."

# Plain "def" (not "async def") on purpose: the model takes many seconds, and
# FastAPI runs plain functions in the background so the server doesn't freeze.
@app.post("/start")
def start(req: StartRequest):
    text = get_page_text(req.url)
    if text is None:
        # 422 = "I understood the request but can't process it"
        raise HTTPException(status_code=422, detail=friendly_error(fetch_page.LAST_REASON))
    session_id = str(uuid.uuid4())  # a random, unique ticket number
    SESSIONS[session_id] = {"text": text, "history": []}
    return {
        "session_id": session_id,
        "words": len(text.split()),
        "truncated": len(text) > MAX_CHARS,
        # What share of the page the model can actually read (capped at 100)
        "percent_read": min(100, round(100 * MAX_CHARS / len(text))),
    }

@app.post("/ask")
def ask(req: AskRequest):
    session = SESSIONS.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session. Load the page again.")
    answer = chat_about_page(session["text"], session["history"], req.question)
    session["history"] += [{"role": "user", "content": req.question},
                           {"role": "assistant", "content": answer}]
    return {"answer": answer}