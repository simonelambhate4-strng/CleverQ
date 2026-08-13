import os
import io
import tempfile
 

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from PIL import Image

#PAGE CONFIG (must be first Streamlit call) 
st.set_page_config(page_title="CleverQ | AI Tutor", page_icon="🎓", layout="wide")

#LOAD ENV
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    load_dotenv(".env")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CONFIGURE SDKS
gemini_model = None
groq_client = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

#  SESSION STATE 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "Both + Fusion"
if "subject" not in st.session_state:
    st.session_state.subject = "General"

#  CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --secondary: #a855f7;
    --accent: #34d399;
    --bg-deep: #020617;
    --bg-card: rgba(15, 23, 42, 0.65);
    --border-subtle: rgba(255, 255, 255, 0.06);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
}

* { font-family: 'Inter', sans-serif !important; }

/*  App Background  */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 10% 20%, rgba(99,102,241,0.12), transparent 50%),
        radial-gradient(ellipse 60% 50% at 90% 80%, rgba(168,85,247,0.10), transparent 50%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(52,211,153,0.06), transparent 50%),
        var(--bg-deep);
}

[data-testid="stSidebar"] {
    background: rgba(2, 6, 23, 0.95) !important;
    border-right: 1px solid var(--border-subtle);
}

/* ---- Header ---- */
.hero-section {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
    position: relative;
}
.hero-section h1 {
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 40%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
    letter-spacing: -1px;
}
.hero-subtitle {
    color: var(--text-secondary);
    font-size: 1.05rem;
    font-weight: 400;
    letter-spacing: 0.5px;
}
.hero-pill {
    display: inline-block;
    padding: 5px 16px;
    border-radius: 50px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    background: rgba(99,102,241,0.15);
    color: var(--primary-light);
    border: 1px solid rgba(99,102,241,0.25);
    margin-top: 0.75rem;
}

/* ---- Glass Cards ---- */
.answer-card {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px 28px;
    margin: 12px 0;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.answer-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--card-accent, #6366f1), transparent);
    opacity: 0;
    transition: opacity 0.35s;
}
.answer-card:hover {
    transform: translateY(-3px);
    border-color: rgba(255,255,255,0.1);
    box-shadow: 0 20px 60px -15px rgba(0,0,0,0.5);
}
.answer-card:hover::before { opacity: 1; }

/* Card accent colors */
.card-gemini { --card-accent: #34d399; }
.card-groq { --card-accent: #a855f7; }
.card-fusion { --card-accent: #6366f1; }

/* ---- Badges ---- */
.model-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 8px;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.badge-gemini { background: rgba(52,211,153,0.12); color: #34d399 !important; border: 1px solid rgba(52,211,153,0.25); }
.badge-groq { background: rgba(168,85,247,0.12); color: #a855f7 !important; border: 1px solid rgba(168,85,247,0.25); }
.badge-fusion { background: rgba(99,102,241,0.12); color: #818cf8 !important; border: 1px solid rgba(99,102,241,0.25); }

.best-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.65rem !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    background: rgba(251,191,36,0.12);
    color: #fbbf24 !important;
    border: 1px solid rgba(251,191,36,0.25);
    margin-left: 8px;
}

/* ---- Answer Text ---- */
.answer-body {
    color: var(--text-primary);
    line-height: 1.75;
    font-size: 0.92rem;
    margin: 16px 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* ---- Score Bar ---- */
.score-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
}
.score-label {
    font-size: 0.7rem;
    color: var(--text-secondary);
    font-weight: 500;
    letter-spacing: 0.3px;
}
.score-track {
    flex: 1;
    height: 4px;
    background: rgba(30, 41, 59, 0.8);
    border-radius: 10px;
    margin-left: 12px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ---- Welcome Screen ---- */
.welcome-container {
    text-align: center;
    padding: 60px 20px;
    max-width: 600px;
    margin: 0 auto;
}
.welcome-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    display: block;
}
.welcome-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}
.welcome-text {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
}
.suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin-top: 1.5rem;
}
.chip {
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 0.8rem;
    color: var(--text-secondary);
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    cursor: default;
    transition: all 0.2s;
}
.chip:hover {
    border-color: rgba(99,102,241,0.3);
    color: var(--text-primary);
}

/* ---- Sidebar Styles ---- */
.sidebar-title {
    text-align: center;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.sidebar-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
    margin: 1rem 0;
    border: none;
}
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 6px;
}
.status-online { background: #34d399; box-shadow: 0 0 6px #34d399; }
.status-offline { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

/* ---- Chat Messages ---- */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 8px 0 !important;
}

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.25s !important;
}
</style>
""", unsafe_allow_html=True)  
# ===== HELPER FUNCTIONS =====

def score_answer(answer):
    """Score an AI answer on quality metrics (0-10)."""
    if not answer or answer.startswith("Error") or answer.startswith("Gemini Error") or answer.startswith("Groq Error"):
        return 0
    score = 0.0
    # Length — longer answers tend to be more thorough
    length = len(answer)
    if length > 500:
        score += 3
    elif length > 200:
        score += 2
    elif length > 80:
        score += 1

    # Structure — bullets, numbered lists, headers
    structural_markers = ["- ", "• ", "* ", "1.", "2.", "3.", "**", "##"]
    struct_count = sum(1 for m in structural_markers if m in answer)
    score += min(struct_count, 3)

    # Paragraphs / line breaks — well-organized
    newlines = answer.count("\n")
    if newlines >= 4:
        score += 2
    elif newlines >= 2:
        score += 1

    # Contains explanatory patterns
    explanation_markers = ["because", "therefore", "for example", "this means", "in other words", "such as"]
    expl_count = sum(1 for m in explanation_markers if m.lower() in answer.lower())
    if expl_count >= 2:
        score += 2
    elif expl_count >= 1:
        score += 1

    return min(int(score), 10)


def build_context_messages(user_input, context="", subject="General"):
    """Build a prompt with conversation history and subject context."""
    subject_hint = ""
    if subject != "General":
        subject_hint = f"The student is studying {subject}. Tailor your response to this subject area.\n"

    # Include last 4 exchanges for conversation memory
    history_text = ""
    recent = [m for m in st.session_state.messages if not m.get("html")]
    if recent:
        last_msgs = recent[-8:]  # last 4 pairs
        for msg in last_msgs:
            role = "Student" if msg["role"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"

    system_prompt = (
        "You are CleverQ, an expert AI tutor for students. "
        "Give clear, accurate, well-structured answers. "
        "Use bullet points, numbered steps, and examples where helpful. "
        "Be concise but thorough.\n"
        f"{subject_hint}"
    )

    full_prompt = system_prompt
    if history_text:
        full_prompt += f"\nRecent conversation:\n{history_text}\n"
    if context:
        full_prompt += f"\nAttached content: {context}\n"
    full_prompt += f"\nStudent's question: {user_input}"

    return full_prompt


def get_fusion_prompt(answer1, answer2, subject="General"):
    """Build the fusion prompt to combine two AI answers."""
    return (
        "You are an expert academic tutor. A student asked a question and received two answers "
        "from different AI models. Your job is to combine them into ONE perfect answer.\n\n"
        "Rules:\n"
        "- Start with a clear, concise definition or direct answer\n"
        "- Then provide well-organized bullet points or numbered steps\n"
        "- Include the best details from BOTH answers\n"
        "- Remove any redundancy\n"
        "- Add a brief example if appropriate\n"
        "- Keep it student-friendly and easy to understand\n"
        f"- Subject area: {subject}\n\n"
        f"Answer 1 (Gemini):\n{answer1}\n\n"
        f"Answer 2 (Groq/Llama):\n{answer2}\n\n"
        "Combined best answer:"
    )


def render_answer_card(title, badge_class, card_class, content, score, emoji, is_best=False):
    """Render a styled answer card as HTML."""
    best_html = '<span class="best-tag">⭐ Best Answer</span>' if is_best else ''
    # bar color
    color_map = {"card-gemini": "#34d399", "card-groq": "#a855f7", "card-fusion": "#818cf8"}
    bar_color = color_map.get(card_class, "#6366f1")

    # HTML 
    safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""
    <div class="answer-card {card_class}">
        <div style="display:flex; align-items:center; flex-wrap:wrap; gap:8px;">
            <span class="model-badge {badge_class}">{emoji} {title}</span>
            {best_html}
        </div>
        <div class="answer-body">{safe_content}</div>
        <div class="score-row">
            <span class="score-label">Quality: {score}/10</span>
            <div class="score-track">
                <div class="score-fill" style="width:{score*10}%; background: linear-gradient(90deg, {bar_color}, {bar_color}88);"></div>
            </div>
        </div>
    </div>
    """


# SIDEBAR 
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎓 CleverQ</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#94a3b8; font-size:0.8rem; margin-bottom:1rem;">AI-Powered Student Companion</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Model status indicators
    gemini_status = "online" if gemini_model else "offline"
    groq_status = "online" if groq_client else "offline"
    st.markdown(f"""
    <div style="font-size:0.82rem; color:#cbd5e1; margin-bottom:1rem;">
        <div style="margin-bottom:6px;"><span class="status-dot status-{gemini_status}"></span>Gemini 1.5 Flash</div>
        <div><span class="status-dot status-{groq_status}"></span>Groq Llama 3.3</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Mode selector
    st.session_state.mode = st.selectbox(
        "Response Mode",
        ["Both + Fusion", "Gemini Only", "Groq Only"],
        index=0,
        help="Choose which AI models to query"
    )

    # Subject context
    st.session_state.subject = st.selectbox(
        "📚 Subject Area",
        ["General", "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "History", "English", "Economics"],
        index=0,
        help="Set subject context for better answers"
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # File uploader
    st.markdown("##### 📎 Attach File")
    uploaded_file = st.file_uploader(
        "Upload image, audio, or PDF",
        type=["png", "jpg", "jpeg", "pdf", "mp3", "wav"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("💾 Export", use_container_width=True):
            if st.session_state.messages:
                chat_export = "CleverQ — Chat Export\n" + "=" * 40 + "\n\n"
                for msg in st.session_state.messages:
                    if not msg.get("html"):
                        role = "You" if msg["role"] == "user" else "CleverQ"
                        chat_export += f"[{role}]\n{msg['content']}\n\n"
                    else:
                        chat_export += f"[CleverQ — AI Response]\n(Formatted answer card)\n\n"
                st.download_button(
                    "⬇️ Download",
                    data=chat_export,
                    file_name="cleverq_chat.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center; font-size:0.7rem; color:#475569;">v4.0 • Multi-Model Fusion • By Saloni Tiwari</div>',
        unsafe_allow_html=True
    )
#HEADER 
st.markdown("""
<div class="hero-section">
    <h1>CleverQ</h1>
    <div class="hero-subtitle">Your AI-powered study companion — one question, multiple perspectives, one best answer.</div>
    <div class="hero-pill">✨ Powered by Gemini + Groq Fusion</div>
</div>
""", unsafe_allow_html=True)


# CHAT DISPLAY 
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-container">
        <span class="welcome-icon">💡</span>
        <div class="welcome-title">What would you like to learn?</div>
        <div class="welcome-text">
            Ask any question — I'll query multiple AI models and fuse their answers
            to give you the most accurate, well-structured response.
        </div>
        <div class="suggestion-chips">
            <span class="chip">🧪 Explain photosynthesis</span>
            <span class="chip">💻 What is recursion?</span>
            <span class="chip">📐 Pythagorean theorem</span>
            <span class="chip">🌍 Causes of WW2</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("html"):
                st.markdown(msg["content"], unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])


# ===== QUERY FUNCTIONS =====

def query_gemini(prompt, media_data=None):
    """Query Gemini model with fallback."""
    if not gemini_model:
        return "Error: Gemini API key not configured."
    try:
        if media_data:
            response = gemini_model.generate_content([prompt, media_data])
        else:
            response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            # Try fallback models
            for fallback_name in ["gemini-pro", "gemini-1.0-pro", "models/gemini-1.5-flash"]:
                try:
                    alt = genai.GenerativeModel(fallback_name)
                    response = alt.generate_content(prompt)
                    return response.text
                except Exception:
                    continue
            return "Gemini Error: All model attempts failed. Please check your API key."
        return f"Gemini Error: {e}"


def query_groq(prompt):
    """Query Groq model."""
    if not groq_client:
        return "Error: Groq API key not configured."
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {e}"


#  INPUT HANDLING 
if user_input := st.chat_input("Ask anything — I'll find the best answer for you..."):
    context = ""
    media_data = None

    # uploaded media
    if uploaded_file:
        file_type = uploaded_file.type or ""
        if "image" in file_type:
            media_data = Image.open(uploaded_file)
            context = "[Image attached — please analyze this image]"
        elif "audio" in file_type:
            with st.spinner("🎧 Transcribing audio..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(uploaded_file.read())
                        with open(tmp.name, "rb") as f:
                            transcript = groq_client.audio.transcriptions.create(
                                model="whisper-large-v3", file=f, response_format="text"
                            )
                        os.unlink(tmp.name)
                        context = f"[Audio Transcript]: {transcript}"
                except Exception as e:
                    context = f"[Audio transcription failed: {e}]"
        elif "pdf" in file_type:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(uploaded_file)
                pdf_text = " ".join([p.extract_text() or "" for p in reader.pages[:5]])
                context = f"[PDF Content]: {pdf_text[:3000]}"
            except Exception as e:
                context = f"[PDF processing failed: {e}]"

    # Add user message
    display_prefix = "📎 " if uploaded_file else ""
    st.session_state.messages.append({"role": "user", "content": f"{display_prefix}{user_input}"})

    # Build prompt with context
    full_prompt = build_context_messages(user_input, context, st.session_state.subject)
    mode = st.session_state.mode
    subject = st.session_state.subject

    with st.spinner(" Querying AI models..."):
        gemini_answer = ""
        groq_answer = ""
        fusion_answer = ""

        # Query based on selected mode
        if mode == "Both + Fusion" or mode == "Gemini Only":
            gemini_answer = query_gemini(full_prompt, media_data)

        if mode == "Both + Fusion" or mode == "Groq Only":
            groq_answer = query_groq(full_prompt)

        # Fusion 
        if mode == "Both + Fusion" and gemini_answer and groq_answer:
            # Only fuse if both answers are valid (not errors)
            gemini_ok = not gemini_answer.startswith(("Error", "Gemini Error"))
            groq_ok = not groq_answer.startswith(("Error", "Groq Error"))

            if gemini_ok and groq_ok:
                fusion_prompt = get_fusion_prompt(gemini_answer, groq_answer, subject)
                fusion_answer = query_gemini(fusion_prompt)
            elif gemini_ok:
                fusion_answer = gemini_answer  # fallback to working model
            elif groq_ok:
                fusion_answer = groq_answer

        # Score all answers
        s_gemini = score_answer(gemini_answer)
        s_groq = score_answer(groq_answer)
        s_fusion = score_answer(fusion_answer)

        # Determine best
        scores = {}
        if gemini_answer:
            scores["Gemini"] = s_gemini
        if groq_answer:
            scores["Groq"] = s_groq
        if fusion_answer:
            scores["Fusion"] = s_fusion
        best = max(scores, key=scores.get) if scores else "Fusion"

        # Pick the single best answer
        if mode == "Both + Fusion":
            # Map names to their data
            candidates = {
                "Gemini": {"answer": gemini_answer, "score": s_gemini, "badge": "badge-gemini", "card": "card-gemini", "title": "Gemini 1.5 Flash", "emoji": "🟢"},
                "Groq": {"answer": groq_answer, "score": s_groq, "badge": "badge-groq", "card": "card-groq", "title": "Llama 3.3 · Groq", "emoji": "🟣"},
                "Fusion": {"answer": fusion_answer, "score": s_fusion, "badge": "badge-fusion", "card": "card-fusion", "title": "Fused Answer", "emoji": "✨"},
            }
            winner = candidates[best]

            # Build comparison summary bar
            comparison_html = f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 16px 20px; margin-bottom: 10px;">
                <div style="font-size: 0.72rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                    ⚡ Model Comparison — <span style="color: #fbbf24;">{best}</span> wins
                </div>
                <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                    <div style="flex:1; min-width: 120px;">
                        <div style="font-size: 0.75rem; color: #34d399; margin-bottom: 4px;">🟢 Gemini: {s_gemini}/10</div>
                        <div style="height:4px; background:#1e293b; border-radius:4px; overflow:hidden;"><div style="width:{s_gemini*10}%; height:100%; background:#34d399; border-radius:4px;"></div></div>
                    </div>
                    <div style="flex:1; min-width: 120px;">
                        <div style="font-size: 0.75rem; color: #a855f7; margin-bottom: 4px;">🟣 Groq: {s_groq}/10</div>
                        <div style="height:4px; background:#1e293b; border-radius:4px; overflow:hidden;"><div style="width:{s_groq*10}%; height:100%; background:#a855f7; border-radius:4px;"></div></div>
                    </div>
                    <div style="flex:1; min-width: 120px;">
                        <div style="font-size: 0.75rem; color: #818cf8; margin-bottom: 4px;">✨ Fusion: {s_fusion}/10</div>
                        <div style="height:4px; background:#1e293b; border-radius:4px; overflow:hidden;"><div style="width:{s_fusion*10}%; height:100%; background:#818cf8; border-radius:4px;"></div></div>
                    </div>
                </div>
            </div>
            """

            # Render only the winning card
            best_card = render_answer_card(
                winner["title"], winner["badge"], winner["card"],
                winner["answer"], winner["score"], winner["emoji"], True
            )
            response_html = comparison_html + best_card

        elif mode == "Gemini Only":
            response_html = render_answer_card(
                "Gemini 1.5 Flash", "badge-gemini", "card-gemini",
                gemini_answer, s_gemini, "🟢", True
            )
        elif mode == "Groq Only":
            response_html = render_answer_card(
                "Llama 3.3 · Groq", "badge-groq", "card-groq",
                groq_answer, s_groq, "🟣", True
            )

        # Save plain-text version for conversation memory
        best_answer = fusion_answer or gemini_answer or groq_answer or "No answer generated."
        if mode == "Both + Fusion" and best in candidates:
            best_answer = candidates[best]["answer"]
        st.session_state.messages.append({"role": "assistant", "content": best_answer})
        # Store the HTML version for display
        st.session_state.messages.append({"role": "assistant", "content": response_html, "html": True})

    st.rerun()
