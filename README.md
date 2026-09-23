# 🦸‍♂️ CyberSec Threat Intelligence Assistant 🛡️

Welcome to the headquarters of the **CyberSec Threat Intelligence Assistant**! 🕵️‍♂️ 
Have you ever dreamed of having a tireless sidekick who reads thousands of boring (ahem, *very important*) logs and corporate policies while you sip your coffee? Well, you're in the right place!

This project is a **RAG (Retrieval-Augmented Generation)** system with superpowers, born from my experience at the **CYBER 4.0** competence center. It has been trained to extract the truth (and nothing but the truth!) from your security documents, thwarting any hallucination attempts by the AI. No "false positive" panic here!

## 🧠 How the Magic Works (RAG Architecture)

1. **Ingestion (The PDF Feast)** 📚: Drop your `.pdf` and `.txt` files into the `data/` folder. Our bot will devour everything using `LangChain`.
2. **The Mince (Text Chunking)** 🔪: The AI can't swallow everything whole, so we cut the texts into perfect little 1000-character "bites" (chunks) to keep the memory light.
3. **The Vector Brain (Embeddings & ChromaDB)** 🌐: We use OpenAI's magic (`text-embedding-3-small`) to turn words into numbers and hide them in our local vault, **ChromaDB**. No data travels to external databases: your documents stay safely on your PC.
4. **The Interrogation (Retrieval & Generation)** 🎤: Ask a question via the terminal and our `gpt-4o-mini` agent will sift through the files in a nanosecond to give you the answer. And if it doesn't know? It throws its hands up and admits defeat. Zero made-up stories, pinky promise! 🤞

## 🧪 Ready, Set... Hack! (Local Testing Instructions)

Want to unleash the beast on your computer? Follow these simple steps:

### 1. Set up Base Camp
Open your terminal and make sure you are in this folder:
```bash
# Get into the action
cd cybersecurityRAG
```

### 2. Put on your HAZMAT suit (Virtual Environment)
Let's avoid making a mess of your system by creating an isolated environment:
```bash
python -m venv venv

# If you use Mac/Linux:
source venv/bin/activate

# If you use Windows (because you love living on the edge):
# venv\Scripts\activate
```

### 3. Load the Arsenal (Dependencies)
Install all the necessary AI super-modules:
```bash
pip install -r requirements.txt
```

### 4. Enter the Launch Code (API Key)
Create a file named `.env` (you can copy the `.env.example` file) and put your secret OpenAI pass in it:
```env
OPENAI_API_KEY=sk-your_super_secret_api_key_here
```

### 5. Load the Ammo 📄
Create a folder named `data/` (if it isn't there already) and throw in some manuals, CVE reports, or corporate policies (in PDF or TXT format). 

### 6. 🔥 Start the Engines!
Launch the assistant:
```bash
python app.py
```
On the first run, it will take a moment to memorize the documents, then you can ask it as many questions as you want. *Et voilà!* Now you can interrogate the bot and feel a bit like Mr. Robot. 💻

---
*Designed with ☕ and 🛡️ so you'll never be caught off guard by ransomware.*
