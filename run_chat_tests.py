import csv
import time
import fetch_page
from fetch_page import get_page_text
from chat import chat_about_page

PAGES = [
    ("news (free)",      "https://www.cnn.com/2026/11/15/tech/ai-students-college-admissions"),
    ("wikipedia",        "https://en.wikipedia.org/wiki/P-value"),
    ("paywalled (news)",        "https://www.nytimes.com/2026/11/14/technology/jensen-huang-nvidia-board.html?eafs_enabled=false"),
    ("paywalled (academic paper)",        "https://ieeexplore.ieee.org/document/11341698"),
    ("pdf",              "https://arxiv.org/pdf/2611.18543"),
]


QUESTIONS = [
    "tl:dr",
    "Explain that again in one simple sentence.",
    "What is the capital of Australia?",
]

with open("chat_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["type", "url", "fetch_result", "words", "seconds",
                     "q1_answer", "q2_answer", "q3_answer", "quality", "notes"])
    for kind, url in PAGES:
        print("=" * 70)
        print(f"{kind}: {url}")
        start = time.time()
        text = get_page_text(url)
        if text is None:
            writer.writerow([kind, url, fetch_page.LAST_REASON, 0, "", "", "", "", "", ""])
            continue
        history, answers = [], []
        for q in QUESTIONS:
            a = chat_about_page(text, history, q)
            history += [{"role": "user", "content": q},
                        {"role": "assistant", "content": a}]
            answers.append(a)
            print(f"\nQ: {q}\nA: {a}")
        writer.writerow([kind, url, "ok", len(text.split()),
                         f"{time.time() - start:.1f}", *answers, "", ""])
