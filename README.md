# BrowseBuddy
This repo holds my Final Project for UNC Master of Applied Data Science Deep Learning course, called _BrowseBuddy._

_BrowseBuddy_ consists of a Chrome side-panel extension featuring a locally-hosted chatbot accessed via a Python server. The frontend reads the URL of the user’s active tab, and sends it to a backend, which runs on the user’s machine built with FastAPI and served by uvicorn. The page is retrieved using the requests library, after cross-referencing the site’s robots.txt to ensure the page is allowed to be accessed by a machine. Readable text is extracted from the HTML or PDF (it does not currently support JavaScript webpages). This text is passed to Qwen2.5, served by Ollama, completely circumventing any cloud services. Two layers of prompt injection defense were applied—system text and a reminder preceding the user’s question, as well as a regex filter that removes key words associated with prompt injections such as “ignore all previous instructions.” The page fetching script also screens for captcha and/or login phrases like “verify you are human” , “sign in”, etc., so it does not unintentionally bypass these hurdles.

To use this extension, you must:
- Install the Ollama app from ollama.com and run ollama pull qwen2.5:3b
- Download the files in this GitHub repository to your computer
- Load the extension in Chrome with chrome://extensions → Developer mode → Load unpacked → the extension folder
- Make sure Ollama is open and running
- Run the following commands in terminal:
  - python3 -m venv \<name of your desired virtual environment\>
  - source \<name of your desired virtual environment\>/bin/activate
  - pip install -r requirements.txt
  - uvicorn server:app --reload
