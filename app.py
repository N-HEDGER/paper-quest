import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE = Path(__file__).parent
HERO_IMAGE = BASE / "graphics" / "A97603_SREP_TOP_100_NEUROSCI_HERO_580x326px-b834fe7c2c0f7a2082d6501e2a5b8433.jpg"

WEEKS = [
    {
        "title": "Autism & the Brain",
        "subtitle": "Week 1 — Neural Mechanisms in Autism Spectrum Disorders",
        "podcast": str(BASE / "podcast" / "Autism.wav"),
        "papers": [
            {
                "title": "fMRI activation of the fusiform gyrus and amygdala to cartoon characters but not to faces in a boy with autism",
                "authors": "Grelotti et al. (2005)",
                "journal": "Neuropsychologia",
                "file": str(BASE / "papers" / "Paper1.pdf"),
                "embed_url": "https://drive.google.com/file/d/1_S0olC5KXR6ONap-0wilcw5pezgtBAUM/preview",
                "mcqs": [
                    {
                        "question": "Which brain region is primarily associated with face processing in typically developing individuals?",
                        "options": [
                            "Hippocampus",
                            "Fusiform gyrus",
                            "Prefrontal cortex",
                            "Cerebellum",
                        ],
                        "answer": 1,
                    },
                    {
                        "question": "What type of stimuli did the boy with autism show greater fusiform activation for, compared to faces?",
                        "options": [
                            "Animals",
                            "Landscapes",
                            "Cartoon characters",
                            "Geometric shapes",
                        ],
                        "answer": 2,
                    },
                ],
                "short_answers": [
                    {
                        "question": "What does this case study suggest about the role of expertise and interest in fusiform gyrus activation?",
                        "model_answer": "The study suggests that fusiform gyrus activation may be driven by individual expertise and personal interest rather than being face-specific — the boy's intense interest in cartoon characters led to fusiform activation for those stimuli instead of faces.",
                    },
                ],
            },
            {
                "title": "Local functional overconnectivity in posterior brain regions is associated with symptom severity in autism spectrum disorders",
                "authors": "Keown et al. (2013)",
                "journal": "Cell Reports",
                "file": str(BASE / "papers" / "Paper2.pdf"),
                "embed_url": "https://drive.google.com/file/d/1iKpb6pnbW8XPs_mWOxYwQBltwZ-6CmZM/preview",
                "mcqs": [
                    {
                        "question": "What pattern of functional connectivity did the authors find in posterior brain regions of participants with ASD?",
                        "options": [
                            "Underconnectivity",
                            "No difference from controls",
                            "Overconnectivity",
                            "Random connectivity patterns",
                        ],
                        "answer": 2,
                    },
                    {
                        "question": "How did local overconnectivity relate to autism symptom severity?",
                        "options": [
                            "No relationship was found",
                            "Greater overconnectivity was associated with milder symptoms",
                            "Greater overconnectivity was associated with more severe symptoms",
                            "The relationship was U-shaped",
                        ],
                        "answer": 2,
                    },
                ],
                "short_answers": [
                    {
                        "question": "How do the findings of local overconnectivity relate to theories of long-range underconnectivity in autism?",
                        "model_answer": "The findings suggest that autism involves both local overconnectivity and long-range underconnectivity — posterior regions are overly connected locally, which may come at the cost of efficient long-range integration, supporting a model where local over-processing and global under-integration coexist.",
                    },
                ],
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* --- Global --- */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* --- Sidebar --- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e27 0%, #131842 50%, #1a1040 100%);
    border-right: 1px solid rgba(100, 120, 255, 0.15);
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e4ff !important;
}

/* --- Hero banner --- */
.hero-banner {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(80, 100, 255, 0.15);
}

.hero-banner img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
}

.hero-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1.5rem 2rem;
    background: linear-gradient(transparent, rgba(10, 14, 39, 0.95));
}

.hero-overlay h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.25rem 0;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.hero-overlay p {
    font-size: 0.95rem;
    color: rgba(200, 210, 255, 0.85);
    margin: 0;
    font-weight: 300;
}

/* --- Cards --- */
.content-card {
    background: linear-gradient(135deg, rgba(20, 25, 60, 0.6) 0%, rgba(30, 20, 60, 0.4) 100%);
    border: 1px solid rgba(100, 120, 255, 0.12);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}

.question-card {
    background: rgba(15, 20, 50, 0.5);
    border: 1px solid rgba(100, 120, 255, 0.1);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

/* --- Stage indicator pills --- */
.stage-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.4rem;
    width: 100%;
}

.stage-done {
    background: rgba(80, 200, 120, 0.15);
    color: #50c878;
    border: 1px solid rgba(80, 200, 120, 0.25);
}

.stage-active {
    background: rgba(100, 130, 255, 0.2);
    color: #8fa4ff;
    border: 1px solid rgba(100, 130, 255, 0.4);
    box-shadow: 0 0 12px rgba(100, 130, 255, 0.15);
}

.stage-locked {
    background: rgba(60, 60, 80, 0.3);
    color: rgba(150, 150, 180, 0.5);
    border: 1px solid rgba(100, 100, 130, 0.15);
}

/* --- XP display --- */
.xp-display {
    text-align: center;
    padding: 1.2rem;
    margin-top: 1rem;
    background: linear-gradient(135deg, rgba(255, 180, 50, 0.1) 0%, rgba(255, 120, 50, 0.08) 100%);
    border: 1px solid rgba(255, 180, 50, 0.2);
    border-radius: 12px;
}

.xp-number {
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffb432;
    line-height: 1;
}

.xp-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(255, 180, 50, 0.7);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* --- Section headers --- */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.section-icon {
    font-size: 2rem;
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(100, 130, 255, 0.12);
}

.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #e0e4ff;
    margin: 0;
}

.section-subtitle {
    font-size: 0.85rem;
    color: rgba(180, 190, 220, 0.7);
    margin: 0;
}

/* --- Paper info --- */
.paper-meta {
    display: flex;
    gap: 1rem;
    margin: 0.75rem 0 1.5rem 0;
    flex-wrap: wrap;
}

.meta-tag {
    font-size: 0.78rem;
    padding: 0.3rem 0.75rem;
    border-radius: 6px;
    background: rgba(100, 130, 255, 0.1);
    color: rgba(180, 195, 255, 0.8);
    border: 1px solid rgba(100, 130, 255, 0.15);
}

/* --- Completion screen --- */
.completion-card {
    text-align: center;
    background: linear-gradient(135deg, rgba(80, 200, 120, 0.08) 0%, rgba(100, 130, 255, 0.08) 100%);
    border: 1px solid rgba(80, 200, 120, 0.2);
    border-radius: 16px;
    padding: 3rem 2rem;
}

.completion-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

/* --- Progress bar override --- */
.stProgress > div > div {
    background: linear-gradient(90deg, #6482ff, #a855f7) !important;
    border-radius: 10px;
}

.stProgress > div {
    background: rgba(100, 130, 255, 0.1) !important;
    border-radius: 10px;
}

/* --- Button overrides --- */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6482ff 0%, #a855f7 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(100, 130, 255, 0.25) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(100, 130, 255, 0.35) !important;
}

.stButton > button[kind="secondary"] {
    border: 1px solid rgba(100, 130, 255, 0.3) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #8fa4ff !important;
}

/* --- Radio buttons --- */
.stRadio > div {
    gap: 0.3rem !important;
}

/* --- Text area --- */
.stTextArea textarea {
    border: 1px solid rgba(100, 130, 255, 0.2) !important;
    border-radius: 8px !important;
    background: rgba(15, 20, 50, 0.5) !important;
}

.stTextArea textarea:focus {
    border-color: rgba(100, 130, 255, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(100, 130, 255, 0.1) !important;
}

/* --- Sidebar branding --- */
.sidebar-brand {
    text-align: center;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(100, 120, 255, 0.15);
    margin-bottom: 1.5rem;
}

.sidebar-brand h2 {
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #8fa4ff, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.sidebar-brand p {
    font-size: 0.75rem;
    color: rgba(180, 190, 220, 0.5);
    margin: 0.25rem 0 0 0;
}
</style>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_state():
    if "week" not in st.session_state:
        st.session_state.week = 0
    if "stage" not in st.session_state:
        st.session_state.stage = 0
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "mcq_answers" not in st.session_state:
        st.session_state.mcq_answers = {}
    if "sa_revealed" not in st.session_state:
        st.session_state.sa_revealed = set()
    if "sa_self_marks" not in st.session_state:
        st.session_state.sa_self_marks = {}


def _award_xp(amount: int, reason: str):
    key = f"xp_{reason}"
    if key not in st.session_state:
        st.session_state[key] = True
        st.session_state.xp += amount


def _progress_fraction() -> float:
    return st.session_state.stage / 5


def _img_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------

def _render_hero(week):
    if HERO_IMAGE.exists():
        img_b64 = _img_to_base64(HERO_IMAGE)
        st.markdown(
            f"""
            <div class="hero-banner">
                <img src="data:image/jpeg;base64,{img_b64}" alt="banner">
                <div class="hero-overlay">
                    <h1>Paper Quest</h1>
                    <p>{week['subtitle']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_sidebar(week):
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <h2>Paper Quest</h2>
                <p>Neuroscience Module</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Journey")
        st.progress(_progress_fraction())

        stage_config = [
            ("Podcast",           "🎧"),
            ("Read Paper 1",      "📖"),
            ("Paper 1 Questions", "📝"),
            ("Read Paper 2",      "📖"),
            ("Paper 2 Questions", "📝"),
            ("Complete",          "✅"),
        ]

        for i, (label, icon) in enumerate(stage_config):
            if i < st.session_state.stage:
                css_class = "stage-done"
                status = "✓"
            elif i == st.session_state.stage:
                css_class = "stage-active"
                status = "→"
            else:
                css_class = "stage-locked"
                status = "🔒"
            st.markdown(
                f'<div class="stage-pill {css_class}">{status} {icon} {label}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="xp-display">
                <div class="xp-label">Experience Points</div>
                <div class="xp-number">{st.session_state.xp}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_podcast(week):
    _render_hero(week)

    st.markdown(
        """
        <div class="section-header">
            <div class="section-icon">🎧</div>
            <div>
                <p class="section-title">Listen to the Podcast</p>
                <p class="section-subtitle">An introduction to this week's two papers</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    podcast_path = Path(week["podcast"])
    if podcast_path.exists():
        st.audio(str(podcast_path), format="audio/wav")
    else:
        st.warning("Podcast file not found.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("I've listened — continue ▶️", type="primary", use_container_width=True):
            _award_xp(10, "podcast")
            st.session_state.stage = 1
            st.rerun()


def _render_read_paper(week, paper_index: int, next_stage: int):
    paper = week["papers"][paper_index]

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-icon">📖</div>
            <div>
                <p class="section-title">Read Paper {paper_index + 1}</p>
                <p class="section-subtitle">Take your time — the questions come next</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**{paper['title']}**")
    journal = paper.get("journal", "")
    st.markdown(
        f"""
        <div class="paper-meta">
            <span class="meta-tag">👤 {paper['authors']}</span>
            <span class="meta-tag">📰 {journal}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    embed_url = paper.get("embed_url")
    if embed_url:
        components.html(
            f'<iframe src="{embed_url}" '
            f'width="100%" height="800" '
            f'allow="autoplay" '
            f'style="border: none; border-radius: 8px;"></iframe>',
            height=820,
        )
    else:
        st.warning("No embedded viewer available for this paper.")

    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("I've read the paper — continue ▶️", type="primary", use_container_width=True):
            _award_xp(10, f"read_p{paper_index}")
            st.session_state.stage = next_stage
            st.rerun()


def _render_paper_questions(week, paper_index: int):
    paper = week["papers"][paper_index]

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-icon">📝</div>
            <div>
                <p class="section-title">Paper {paper_index + 1} — Comprehension</p>
                <p class="section-subtitle">{paper['authors']} · {paper.get('journal', '')}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- MCQs ---
    st.markdown("#### Multiple Choice")
    mcq_complete = True
    for i, mcq in enumerate(paper["mcqs"]):
        key = f"mcq_p{paper_index}_q{i}"
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"**Q{i+1}.** {mcq['question']}")
        selected = st.radio(
            "Select your answer:",
            mcq["options"],
            index=None,
            key=f"radio_{key}",
            label_visibility="collapsed",
        )
        if selected is not None:
            chosen_idx = mcq["options"].index(selected)
            if chosen_idx == mcq["answer"]:
                st.success("Correct! +5 XP")
                _award_xp(5, key)
                st.session_state.mcq_answers[key] = True
            else:
                st.error("Not quite — try again.")
                st.session_state.mcq_answers[key] = False
        if key not in st.session_state.mcq_answers or not st.session_state.mcq_answers[key]:
            mcq_complete = False
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- Short answer ---
    st.markdown("#### Short Answer")
    sa_complete = True
    for i, sa in enumerate(paper["short_answers"]):
        sa_key = f"sa_p{paper_index}_q{i}"
        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"**Q{i+1}.** {sa['question']}")
        st.text_area("Write your answer here...", key=f"ta_{sa_key}", label_visibility="collapsed", height=120)

        if sa_key not in st.session_state.sa_revealed:
            if st.button("Reveal model answer", key=f"rev_{sa_key}"):
                st.session_state.sa_revealed.add(sa_key)
                st.rerun()
        else:
            st.info(f"**Model answer:** {sa['model_answer']}")
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                if st.button("Got it ✓", key=f"got_{sa_key}", type="primary"):
                    st.session_state.sa_self_marks[sa_key] = True
                    _award_xp(10, sa_key)
                    st.rerun()
            with col2:
                if st.button("Missed it ✗", key=f"miss_{sa_key}"):
                    st.session_state.sa_self_marks[sa_key] = False
                    st.rerun()
            if sa_key in st.session_state.sa_self_marks:
                if st.session_state.sa_self_marks[sa_key]:
                    st.success("Nice work! +10 XP")
                else:
                    st.warning("No worries — review and try again next time.")

        if sa_key not in st.session_state.sa_self_marks:
            sa_complete = False
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    all_done = mcq_complete and sa_complete
    if all_done:
        next_stage = st.session_state.stage + 1
        label = "Continue to Paper 2 ▶️" if paper_index == 0 else "Complete week 🎉"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(label, type="primary", use_container_width=True):
                st.session_state.stage = next_stage
                st.rerun()
    else:
        st.info("Answer all questions above to continue.")


def _render_complete(week):
    st.balloons()
    _render_hero(week)
    st.markdown(
        f"""
        <div class="completion-card">
            <div class="completion-icon">🎉</div>
            <h2 style="color: #50c878; margin-bottom: 0.5rem;">Week Complete!</h2>
            <p style="color: rgba(200, 210, 255, 0.7); font-size: 1.1rem;">
                You've finished <strong>{week['title']}</strong>
            </p>
            <div style="margin-top: 1.5rem;">
                <div class="xp-label">Total XP Earned</div>
                <div class="xp-number">{st.session_state.xp}</div>
            </div>
            <p style="color: rgba(180, 190, 220, 0.5); margin-top: 1.5rem; font-size: 0.9rem;">
                Come back next week for more papers!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Paper Quest", page_icon="🧠", layout="centered")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    _init_state()

    week = WEEKS[st.session_state.week]
    _render_sidebar(week)

    stage = st.session_state.stage
    if stage == 0:
        _render_podcast(week)
    elif stage == 1:
        _render_read_paper(week, paper_index=0, next_stage=2)
    elif stage == 2:
        _render_paper_questions(week, paper_index=0)
    elif stage == 3:
        _render_read_paper(week, paper_index=1, next_stage=4)
    elif stage == 4:
        _render_paper_questions(week, paper_index=1)
    elif stage >= 5:
        _render_complete(week)


if __name__ == "__main__":
    main()
