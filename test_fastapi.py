import requests
import time

BASE_URL = "http://127.0.0.1:8000"

URLS = [
    "https://www.cnn.com/2026/11/15/tech/  ai-students-college-admissions",
    "https://en.wikipedia.org/wiki/P-value",
    "https://www.nytimes.com/2026/11/14/technology/jensen-huang-nvidia-board.html?eafs_enabled=false",  # Attention Is All You Need
    "https://ieeexplore.ieee.org/document/  11341698",
    "https://arxiv.org/pdf/2611.18543",
]

QUESTIONS = [
    "Summarize this page.",
    "Condense that summary into one sentence.",
    "What is the capital of Australia?",
]

for url in URLS:
    print("\n" + "=" * 80)
    print(f"URL: {url}")
    print("=" * 80)

    # Start a session with the backend
    try:
        response = requests.post(
            f"{BASE_URL}/start",
            json={"url": url},
            timeout=120,
        )
        response.raise_for_status()
        session_id = response.json()["session_id"]

    except Exception as e:
        print(f"FAILED TO LOAD PAGE: {e}")
        continue

    # Ask the three questions
    for question in QUESTIONS:
        print(f"\nQ: {question}")

        start = time.perf_counter()

        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json={
                    "session_id": session_id,
                    "question": question,
                },
                timeout=300,
            )
            response.raise_for_status()

            answer = response.json()["answer"]
            elapsed = time.perf_counter() - start

            print(f"Time: {elapsed:.2f} seconds")
            print(f"Answer: {answer}")

        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"FAILED ({elapsed:.2f} seconds): {e}")