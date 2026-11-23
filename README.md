# BrowseBuddy
This repo holds my Final Project for UNC Master of Applied Data Science Deep Learning course, called _BrowseBuddy._

_BrowseBuddy_ consists of a Chrome side-panel extension featuring a locally-hosted chatbot accessed via a Python server. The frontend reads the URL of the user’s active tab, and sends it to a backend, which runs on the user’s machine built with FastAPI and served by uvicorn. The page is retrieved using the requests library, after cross-referencing the site’s robots.txt to ensure the page is allowed to be accessed by a machine. Readable text is extracted from the HTML or PDF (it does not currently support JavaScript webpages). This text is passed to Qwen2.5, served by Ollama, completely circumventing any cloud services. Two layers of prompt injection defense were applied—system text and a reminder preceding the user’s question, as well as a regex filter that removes key words associated with prompt injections such as “ignore all previous instructions.” The page fetching script also screens for captcha and/or login phrases like “verify you are human” , “sign in”, etc., so it does not unintentionally bypass these hurdles.

## Setup (macOS; requires Python 3 and Google Chrome)

1. Install the Ollama app from ollama.com and open it (leave it running).
2. In a terminal, download the model:
       ollama pull qwen2.5:3b
3. Download this repository and open a terminal in its folder:
       cd path/to/repo-folder
4. Create and activate a virtual environment, then install the needed packages in requirements.txt:
       python3 -m venv \<name of desired virtual environment\>
       source \<name of desired virtual environment\>/bin/activate
       pip install -r requirements.txt
5. Start the backend server and leave this terminal open:
       uvicorn server:app --reload
6. Load the extension in Chrome:
   go to chrome://extensions, turn on Developer mode, click "Load unpacked", and select the "extension" folder.

## Using BrowseBuddy

1. Open a web page.
2. Click the BrowseBuddy icon in the Chrome toolbar.
3. Click "Load this page," then ask questions about the page.

