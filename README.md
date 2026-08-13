  🎓 CleverQ — Multi-Model AI Q&A for Students

One question. Multiple AI perspectives. One best answer.

CleverQ is an AI-powered question-answering web application that eliminates the need for students to switch between multiple platforms. It uses a **multi-model fusion approach** (Groq + Gemini) to deliver the best AI-powered answers.

## 📖 Problem

Students often:
- Search across multiple platforms (Google, ChatGPT, notes, etc.)
- Get incomplete or inconsistent answers
- Waste time verifying information

## ✨ Features

| Feature | Description |
| --- | --- |
| 🤖 **Multi-Model AI** | Queries both Gemini 1.5 Flash and Llama 3.3 (via Groq) |
| 🔀 **Answer Fusion** | Combines responses into one optimized answer |
| 📊 **Quality Scoring** | Rates each answer on structure, depth, and clarity |
| 💬 **Conversation Memory** | Supports follow-up questions with context |
| 📎 **File Uploads** | Analyze images, transcribe audio, extract PDF text |
| ⚡ **Mode Selector** | Choose Fusion, Gemini-only, or Groq-only |
| 📚 **Subject Context** | Set subject area for tailored responses |
| 💾 **Chat Export** | Download conversation as a text file |
| 🎨 **Premium Dark UI** | Glassmorphic design with smooth animations |

---

## 🏗️ Architecture

```
Student Question
       │
       ▼
  ┌─────────────────────┐
  │   Prompt Builder     │ ← Subject context + conversation history
  │   (with memory)      │
  └──────┬──────┬────────┘
         │      │
         ▼      ▼
    ┌────────┐ ┌────────┐
    │ Gemini │ │  Groq  │
    │ 1.5    │ │ Llama  │
    │ Flash  │ │ 3.3    │
    └───┬────┘ └───┬────┘
        │          │
        ▼          ▼
  ┌─────────────────────┐
  │   Fusion Engine      │ ← Combines best of both
  │   + Quality Scoring  │
  └──────────┬──────────┘
             │
             ▼
      Best Answer Card
```

---

## 🛠️ Tech Stack

- **Python** — Core language
- **Streamlit** — Web UI framework
- **Google Gemini API** — Accurate, detailed responses
- **Groq API** — Ultra-fast LLM inference (Llama 3.3)
- **LangChain** — LLM orchestration
- **PyPDF2** — PDF text extraction
- **Pillow** — Image processing
- **python-dotenv** — Environment variable management

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CleverQ.git
cd CleverQ
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

> 🔑 Get your keys:
> - Gemini: [Google AI Studio](https://aistudio.google.com/app/apikey)
> - Groq: [Groq Console](https://console.groq.com/keys)

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🌐 Deployment (Streamlit Cloud)

1. Push your project to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [Streamlit Community Cloud](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add API keys in **Settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "your_key"
   GROQ_API_KEY = "your_key"
   ```
5. Deploy!

## 🔒 Security

**Never** upload your `.env` file to GitHub
- API keys are loaded via environment variables or Streamlit Secrets
- `.env` is included in `.gitignore` by default

---

## 📊 Model Comparison

| Feature | Gemini 1.5 Flash | Groq (Llama 3.3) | Fusion |
| --- | --- | --- | --- |
| **Speed** | Moderate | ⚡ Very Fast | Moderate |
| **Detail** | ✅ High | Moderate | ✅ High |
| **Accuracy** | ✅ High | Good | ✅ Best |
| **Structure** | Good | Good | ✅ Best |

---

## 💡 Use Cases

- 📖 **Students** — Quick, reliable answers for studying
- 💻 **Developers** — Technical concept explanations
- 🔬 **Researchers** — Multi-perspective analysis
- ✍️ **Assignment Help** — Well-structured responses

---

## 🔮 Future Improvements

- [ ] Confidence scoring with visual indicators
- [ ] Persistent chat history (database-backed)
- [ ] Web search integration
- [ ] Answer ranking with user feedback
- [ ] Voice input support
- [ ] Multi-language support

## 📁 Project Structure

```
CleverQ/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .env                   # API keys (not in repo)
├── .gitignore             # Git ignore rules
└── .streamlit/
    └── config.toml        # Streamlit theme config
```

---

## 👨‍💻 Author

**Simone Lambhate**  
Computer Science (AI) Student

<p align="center">
  Made with ❤️ using Streamlit, Gemini, and Groq
</p>
