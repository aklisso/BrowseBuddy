import ollama  # lets Python talk to the Ollama app running on your Mac

reply = ollama.chat(
    model="qwen2.5:7b",  # must match the model you downloaded
    messages=[{"role": "user", "content": "In one sentence, what is a p-value?"}],
)
print(reply["message"]["content"])  # the model's answer lives inside this nested structure