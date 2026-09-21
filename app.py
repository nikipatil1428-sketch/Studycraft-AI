"""
StudyCraft AI - AI-Powered Student Utility Web Application.
Built for the AI Engineer Internship Evaluation (Beginner Level).
"""

import streamlit as st
import config

# Smart imports: works whether files are in the same folder or in subfolders
try:
    from validator import validate_input, validate_qa_pair, get_text_stats
    from prompt_templates import (
        SUMMARIZER_SYSTEM_PROMPT, build_summarizer_prompt,
        QUIZ_SYSTEM_PROMPT, build_quiz_prompt,
        IMPROVER_SYSTEM_PROMPT, build_answer_improver_prompt,
        EXPLAINER_SYSTEM_PROMPT, build_concept_explainer_prompt
    )
    from ai_service import AIService
    from samples import (
        SAMPLE_NOTES_BIOLOGY,
        SAMPLE_NOTES_HISTORY,
        SAMPLE_IMPROVER_QUESTION,
        SAMPLE_IMPROVER_WEAK_ANSWER,
        SAMPLE_CONCEPT_TOPIC
    )
except ModuleNotFoundError:
    from services.validator import validate_input, validate_qa_pair, get_text_stats
    from services.prompt_templates import (
        SUMMARIZER_SYSTEM_PROMPT, build_summarizer_prompt,
        QUIZ_SYSTEM_PROMPT, build_quiz_prompt,
        IMPROVER_SYSTEM_PROMPT, build_answer_improver_prompt,
        EXPLAINER_SYSTEM_PROMPT, build_concept_explainer_prompt
    )
    from services.ai_service import AIService
    from sample_data.samples import (
        SAMPLE_NOTES_BIOLOGY,
        SAMPLE_NOTES_HISTORY,
        SAMPLE_IMPROVER_QUESTION,
        SAMPLE_IMPROVER_WEAK_ANSWER,
        SAMPLE_CONCEPT_TOPIC
    )

st.set_page_config(
    page_title="StudyCraft AI | Student Utility",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-badge {
        display: inline-block; background-color: #EFF6FF; color: #1D4ED8;
        border: 1px solid #BFDBFE; border-radius: 9999px; padding: 0.2rem 0.75rem;
        font-size: 0.82rem; font-weight: 600; margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "total_requests" not in st.session_state:
    st.session_state.total_requests = 0
if "summarizer_input" not in st.session_state:
    st.session_state.summarizer_input = ""
if "quiz_input" not in st.session_state:
    st.session_state.quiz_input = ""
if "improver_q_input" not in st.session_state:
    st.session_state.improver_q_input = ""
if "improver_a_input" not in st.session_state:
    st.session_state.improver_a_input = ""
if "concept_input" not in st.session_state:
    st.session_state.concept_input = ""

# Sidebar Settings
with st.sidebar:
    st.markdown("## 🎓 StudyCraft AI")
    st.caption("AI-Powered Student Utility Platform")
    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")

    has_env_key = bool(config.GEMINI_API_KEY_ENV)
    mode_option = st.radio(
        "Operating Mode",
        options=["Interactive Demo Mode (Zero-Config)", "Live Google Gemini API"],
        index=0 if not has_env_key else 1,
    )
    is_demo_mode = "Demo" in mode_option

    api_key_input = ""
    if not is_demo_mode:
        api_key_input = st.text_input(
            "Gemini API Key",
            value=config.GEMINI_API_KEY_ENV,
            type="password",
            placeholder="AIzaSy...",
            help="Get your key at https://aistudio.google.com/"
        )
    else:
        st.info("💡 **Demo Mode Active**: Instant realistic evaluation without an API key.")

    selected_model = st.selectbox(
        "Gemini Model",
        options=config.AVAILABLE_MODELS,
        index=0,
        disabled=is_demo_mode
    )

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Requests", st.session_state.total_requests)
    with col2:
        st.metric("Status", "🟢 Ready" if (is_demo_mode or api_key_input) else "🟡 Needs Key")

# Initialize AI Service
ai_service = AIService(
    api_key=api_key_input if not is_demo_mode else "demo-mock-key",
    model_name=selected_model
)

# Header
st.markdown('<div class="main-header">📚 StudyCraft AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Transform unstructured notes into active-recall quizzes, diagnostic answer feedback, '
    'and intuitive conceptual breakdowns.</div>',
    unsafe_allow_html=True
)

# Tabs
tab_summary, tab_quiz, tab_improver, tab_explainer, tab_inspector = st.tabs([
    "📝 Notes Summarizer",
    "🎯 Practice Quiz Generator",
    "✍️ Weak Answer Enhancer",
    "💡 Concept Explainer",
    "🔍 Prompt & Arch Inspector"
])

# ----------------- TAB 1: SUMMARIZER -----------------
with tab_summary:
    st.subheader("📝 Smart Notes Summarizer & High-Yield Takeaways")
    col1, col2 = st.columns(2)
    with col1:
        detail_level = st.selectbox("Summary Depth", ["Standard Study Notes (Balanced)", "Concise TL;DR", "Comprehensive Deep Dive"])
    with col2:
        focus_topic = st.text_input("Optional Focus Area", placeholder="e.g., ATP Synthase")

    b1, b2, _ = st.columns([1.5, 1.5, 5])
    with b1:
        if st.button("📥 Load Biology Sample Notes"):
            st.session_state.summarizer_input = SAMPLE_NOTES_BIOLOGY
            st.rerun()
    with b2:
        if st.button("🗑️ Clear Notes"):
            st.session_state.summarizer_input = ""
            st.rerun()

    notes_text = st.text_area("Paste notes here:", value=st.session_state.summarizer_input, height=200)
    st.session_state.summarizer_input = notes_text

    stats = get_text_stats(notes_text)
    st.markdown(
        f'<span class="metric-badge">Chars: {stats["character_count"]} / {config.MAX_INPUT_CHARS}</span>'
        f'<span class="metric-badge">Words: {stats["word_count"]}</span>'
        f'<span class="metric-badge">Tokens: ~{stats["estimated_tokens"]}</span>',
        unsafe_allow_html=True
    )

    if st.button("✨ Generate Structured Summary", type="primary"):
        val = validate_input(notes_text, min_chars=config.MIN_INPUT_CHARS, max_chars=config.MAX_INPUT_CHARS, field_name="Study Notes")
        if not val.is_valid:
            st.error(val.error_message)
        else:
            prompt = build_summarizer_prompt(notes_text, detail_level, focus_topic)
            with st.spinner("Analyzing and summarizing notes..."):
                resp = ai_service.generate(prompt, SUMMARIZER_SYSTEM_PROMPT, config.TEMPERATURE_SETTINGS["summarizer"], force_demo=is_demo_mode)
            if not resp.success:
                st.error(resp.error)
            else:
                st.session_state.total_requests += 1
                st.success(f"Generated in {resp.duration_sec}s using `{resp.model_used}`")
                st.markdown(resp.content)
                st.download_button("💾 Download Summary (.md)", resp.content, "studycraft_summary.md", "text/markdown")

# ----------------- TAB 2: QUIZ GENERATOR -----------------
with tab_quiz:
    st.subheader("🎯 Active-Recall Practice Quiz Generator")
    q1, q2, q3 = st.columns(3)
    with q1:
        num_q = st.slider("Questions", 1, 6, 2)
    with q2:
        diff = st.selectbox("Difficulty", ["High School", "Undergraduate", "Advanced"])
    with q3:
        q_style = st.selectbox("Format", ["Multiple Choice Questions (MCQs)", "Flashcards"])

    qb1, qb2, _ = st.columns([1.5, 1.5, 5])
    with qb1:
        if st.button("📥 Load History Sample Notes"):
            st.session_state.quiz_input = SAMPLE_NOTES_HISTORY
            st.rerun()
    with qb2:
        if st.button("🗑️ Clear Quiz Input"):
            st.session_state.quiz_input = ""
            st.rerun()

    quiz_text = st.text_area("Source notes for quiz:", value=st.session_state.quiz_input, height=180)
    st.session_state.quiz_input = quiz_text

    if st.button("⚡ Generate Practice Quiz", type="primary"):
        val = validate_input(quiz_text, min_chars=config.MIN_INPUT_CHARS, max_chars=config.MAX_INPUT_CHARS, field_name="Quiz Content")
        if not val.is_valid:
            st.error(val.error_message)
        else:
            prompt = build_quiz_prompt(quiz_text, num_q, diff, q_style)
            with st.spinner("Creating questions and explanations..."):
                resp = ai_service.generate(prompt, QUIZ_SYSTEM_PROMPT, config.TEMPERATURE_SETTINGS["quiz"], force_demo=is_demo_mode)
            if not resp.success:
                st.error(resp.error)
            else:
                st.session_state.total_requests += 1
                st.success(f"Generated in {resp.duration_sec}s using `{resp.model_used}`")
                st.markdown(resp.content)
                st.download_button("💾 Download Quiz (.md)", resp.content, "studycraft_quiz.md", "text/markdown")

# ----------------- TAB 3: ANSWER IMPROVER -----------------
with tab_improver:
    st.subheader("✍️ Weak Answer Enhancer & Rubric Evaluator")
    col_i1, col_i2 = st.columns([2, 1])
    with col_i1:
        if st.button("📥 Load Economics Sample (Question & Weak Answer)"):
            st.session_state.improver_q_input = SAMPLE_IMPROVER_QUESTION
            st.session_state.improver_a_input = SAMPLE_IMPROVER_WEAK_ANSWER
            st.rerun()
    with col_i2:
        acad_level = st.selectbox("Benchmark", ["High School", "College / Undergraduate", "Graduate"])

    q_in = st.text_input("Assignment or Exam Question:", value=st.session_state.improver_q_input)
    st.session_state.improver_q_input = q_in
    a_in = st.text_area("Your Draft Answer:", value=st.session_state.improver_a_input, height=140)
    st.session_state.improver_a_input = a_in

    if st.button("🔍 Diagnose & Enhance Answer", type="primary"):
        val = validate_qa_pair(q_in, a_in)
        if not val.is_valid:
            st.error(val.error_message)
        else:
            prompt = build_answer_improver_prompt(q_in, a_in, acad_level)
            with st.spinner("Scoring answer and generating model rewrite..."):
                resp = ai_service.generate(prompt, IMPROVER_SYSTEM_PROMPT, config.TEMPERATURE_SETTINGS["improver"], force_demo=is_demo_mode)
            if not resp.success:
                st.error(resp.error)
            else:
                st.session_state.total_requests += 1
                st.success(f"Evaluated in {resp.duration_sec}s using `{resp.model_used}`")
                st.markdown(resp.content)
                st.download_button("💾 Download Critique (.md)", resp.content, "studycraft_critique.md", "text/markdown")

# ----------------- TAB 4: CONCEPT EXPLAINER -----------------
with tab_explainer:
    st.subheader("💡 Deep Concept Explainer (Feynman Technique)")
    e1, e2 = st.columns(2)
    with e1:
        aud = st.selectbox("Complexity", ["High School Student", "ELI5 (Explain Like I'm 5)", "Undergraduate"])
    with e2:
        inc_meta = st.checkbox("Include everyday analogy", value=True)

    if st.button("📥 Load AI Concept Sample"):
        st.session_state.concept_input = SAMPLE_CONCEPT_TOPIC
        st.rerun()

    c_in = st.text_input("Topic or Concept to Explain:", value=st.session_state.concept_input)
    st.session_state.concept_input = c_in

    if st.button("🧠 Demystify Concept", type="primary"):
        val = validate_input(c_in, min_chars=5, max_chars=500, field_name="Concept Topic")
        if not val.is_valid:
            st.error(val.error_message)
        else:
            prompt = build_concept_explainer_prompt(c_in, aud, inc_meta)
            with st.spinner("Explaining concept..."):
                resp = ai_service.generate(prompt, EXPLAINER_SYSTEM_PROMPT, config.TEMPERATURE_SETTINGS["explainer"], force_demo=is_demo_mode)
            if not resp.success:
                st.error(resp.error)
            else:
                st.session_state.total_requests += 1
                st.success(f"Generated in {resp.duration_sec}s using `{resp.model_used}`")
                st.markdown(resp.content)
                st.download_button("💾 Download Guide (.md)", resp.content, "studycraft_concept.md", "text/markdown")

# ----------------- TAB 5: INSPECTOR -----------------
with tab_inspector:
    st.subheader("🔍 Prompt & Architecture Inspector")
    st.write("Live transparency into prompt engineering templates and system constraints:")
    tool_inspect = st.selectbox("Select Utility:", ["Notes Summarizer", "Practice Quiz Generator", "Weak Answer Enhancer", "Concept Explainer"])
    if tool_inspect == "Notes Summarizer":
        st.code(SUMMARIZER_SYSTEM_PROMPT, language="markdown")
    elif tool_inspect == "Practice Quiz Generator":
        st.code(QUIZ_SYSTEM_PROMPT, language="markdown")
    elif tool_inspect == "Weak Answer Enhancer":
        st.code(IMPROVER_SYSTEM_PROMPT, language="markdown")
    elif tool_inspect == "Concept Explainer":
        st.code(EXPLAINER_SYSTEM_PROMPT, language="markdown")