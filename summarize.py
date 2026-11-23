import sys
import ollama
from fetch_page import get_page_text

MAX_CHARS = 15000  # about 3,000 words; keeps long pages within the model's memory

def summarize(text):
    """Send page text to the local model and return a short summary."""
    text = text[:MAX_CHARS]
    reply = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "system",
             "content": "You summarize web pages. Write 3 to 5 sentences covering "
                        "the main points. Use only the text provided."},
            {"role": "user", "content": text},
        ],
        # Ollama's default context window is small and silently cuts off long
        # input, so we ask for a bigger one.
        options={"num_ctx": 8192},
    )
    return reply["message"]["content"]

if __name__ == "__main__":
    text = get_page_text(sys.argv[1])
    if text:
        print(summarize(text))