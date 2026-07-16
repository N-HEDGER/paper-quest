import math
import streamlit as st
import streamlit.components.v1 as components
import base64
import requests
import yaml
from pathlib import Path
from streamlit_agraph import agraph, Node, Edge, Config

BASE = Path(__file__).parent
WEEKS_DIR = BASE / "weeks"
HERO_IMAGE = BASE / "graphics" / "A97603_SREP_TOP_100_NEUROSCI_HERO_580x326px-b834fe7c2c0f7a2082d6501e2a5b8433.jpg"

WEEK_NUMBERS = []


def _load_weeks():
    weeks = []
    for f in sorted(WEEKS_DIR.glob("week_*.yaml")):
        with open(f) as fh:
            w = yaml.safe_load(fh)
            weeks.append(w)
            WEEK_NUMBERS.append(w["week_number"])
    return weeks


WEEKS = _load_weeks()


# ---------------------------------------------------------------------------
# Google Sheets persistence
# ---------------------------------------------------------------------------

def _get_gsheet():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        return None

    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
    except (KeyError, FileNotFoundError):
        return None

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    try:
        sheet_url = st.secrets["sheet_url"]
        spreadsheet = client.open_by_url(sheet_url)
    except (KeyError, FileNotFoundError):
        return None

    return spreadsheet.sheet1


def _load_user_progress(username: str):
    sheet = _get_gsheet()
    if sheet is None:
        return None

    try:
        records = sheet.get_all_records()
    except Exception:
        return None

    for row in records:
        if str(row.get("username", "")).strip().lower() == username.strip().lower():
            return row
    return {}


def _save_user_progress(username: str):
    sheet = _get_gsheet()
    if sheet is None:
        return

    progress = {}
    for wn in WEEK_NUMBERS:
        col = f"week_{wn}"
        progress[col] = st.session_state.get(f"week_{wn}_stage", 0)
    progress["xp"] = st.session_state.get("xp", 0)

    try:
        cell = sheet.find(username, in_column=1)
        row_num = cell.row
    except Exception:
        cell = None
        row_num = None

    headers = [f"week_{wn}" for wn in WEEK_NUMBERS]
    all_headers = ["username"] + headers + ["xp"]

    if row_num is None:
        existing_headers = sheet.row_values(1)
        if not existing_headers or existing_headers[0] != "username":
            sheet.update("A1", [all_headers])
        values = [username] + [progress.get(h, 0) for h in headers] + [progress["xp"]]
        sheet.append_row(values)
    else:
        existing_headers = sheet.row_values(1)
        if not existing_headers or existing_headers[0] != "username":
            sheet.update("A1", [all_headers])
            existing_headers = all_headers
        values = [username] + [progress.get(h, 0) for h in headers] + [progress["xp"]]
        sheet.update(f"A{row_num}", [values])


def _restore_progress_to_session(username: str, row: dict):
    st.session_state.username = username
    st.session_state.logged_in = True
    st.session_state.xp = int(row.get("xp", 0))
    for wn in WEEK_NUMBERS:
        col = f"week_{wn}"
        st.session_state[f"week_{wn}_stage"] = int(row.get(col, 0))


def _week_is_unlocked(week_idx: int) -> bool:
    if week_idx == 0:
        return True
    prev_wn = WEEK_NUMBERS[week_idx - 1]
    return st.session_state.get(f"week_{prev_wn}_stage", 0) >= 5


def _sheets_available() -> bool:
    try:
        import gspread  # noqa: F401
        from google.oauth2.service_account import Credentials  # noqa: F401
        _ = st.secrets["gcp_service_account"]
        _ = st.secrets["sheet_url"]
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.stApp { font-family: 'Inter', sans-serif; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e27 0%, #131842 50%, #1a1040 100%);
    border-right: 1px solid rgba(100, 120, 255, 0.15);
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e4ff !important;
}

.hero-banner {
    position: relative; border-radius: 16px; overflow: hidden;
    margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(80, 100, 255, 0.15);
}
.hero-banner img { width: 100%; height: 200px; object-fit: cover; display: block; }
.hero-overlay {
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 1.5rem 2rem;
    background: linear-gradient(transparent, rgba(10, 14, 39, 0.95));
}
.hero-overlay h1 {
    font-size: 1.8rem; font-weight: 700; color: #ffffff;
    margin: 0 0 0.25rem 0; text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.hero-overlay p {
    font-size: 0.95rem; color: rgba(200, 210, 255, 0.85);
    margin: 0; font-weight: 300;
}

.content-card {
    background: linear-gradient(135deg, rgba(20, 25, 60, 0.6) 0%, rgba(30, 20, 60, 0.4) 100%);
    border: 1px solid rgba(100, 120, 255, 0.12); border-radius: 12px;
    padding: 2rem; margin-bottom: 1.5rem; backdrop-filter: blur(10px);
}
.question-card {
    background: rgba(15, 20, 50, 0.5);
    border: 1px solid rgba(100, 120, 255, 0.1); border-radius: 10px;
    padding: 1.5rem; margin-bottom: 1.2rem;
}

.stage-pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem;
    font-weight: 500; margin-bottom: 0.4rem; width: 100%;
}
.stage-done {
    background: rgba(80, 200, 120, 0.15); color: #50c878;
    border: 1px solid rgba(80, 200, 120, 0.25);
}
.stage-active {
    background: rgba(100, 130, 255, 0.2); color: #8fa4ff;
    border: 1px solid rgba(100, 130, 255, 0.4);
    box-shadow: 0 0 12px rgba(100, 130, 255, 0.15);
}
.stage-locked {
    background: rgba(60, 60, 80, 0.3); color: rgba(150, 150, 180, 0.5);
    border: 1px solid rgba(100, 100, 130, 0.15);
}

.xp-display {
    text-align: center; padding: 1.2rem; margin-top: 1rem;
    background: linear-gradient(135deg, rgba(255, 180, 50, 0.1) 0%, rgba(255, 120, 50, 0.08) 100%);
    border: 1px solid rgba(255, 180, 50, 0.2); border-radius: 12px;
}
.xp-number { font-size: 2.5rem; font-weight: 700; color: #ffb432; line-height: 1; }
.xp-label {
    font-size: 0.75rem; font-weight: 600; color: rgba(255, 180, 50, 0.7);
    text-transform: uppercase; letter-spacing: 0.1em;
}

.section-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.section-icon {
    font-size: 2rem; width: 3rem; height: 3rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px; background: rgba(100, 130, 255, 0.12);
}
.section-title { font-size: 1.4rem; font-weight: 600; color: #e0e4ff; margin: 0; }
.section-subtitle { font-size: 0.85rem; color: rgba(180, 190, 220, 0.7); margin: 0; }

.paper-meta { display: flex; gap: 1rem; margin: 0.75rem 0 1.5rem 0; flex-wrap: wrap; }
.meta-tag {
    font-size: 0.78rem; padding: 0.3rem 0.75rem; border-radius: 6px;
    background: rgba(100, 130, 255, 0.1); color: rgba(180, 195, 255, 0.8);
    border: 1px solid rgba(100, 130, 255, 0.15);
}

.completion-card {
    text-align: center;
    background: linear-gradient(135deg, rgba(80, 200, 120, 0.08) 0%, rgba(100, 130, 255, 0.08) 100%);
    border: 1px solid rgba(80, 200, 120, 0.2); border-radius: 16px; padding: 3rem 2rem;
}
.completion-icon { font-size: 4rem; margin-bottom: 1rem; }

.stProgress > div > div {
    background: linear-gradient(90deg, #6482ff, #a855f7) !important; border-radius: 10px;
}
.stProgress > div { background: rgba(100, 130, 255, 0.1) !important; border-radius: 10px; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6482ff 0%, #a855f7 100%) !important;
    border: none !important; border-radius: 8px !important; font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(100, 130, 255, 0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(100, 130, 255, 0.35) !important;
}
.stButton > button[kind="secondary"] {
    border: 1px solid rgba(100, 130, 255, 0.3) !important; border-radius: 8px !important;
    font-weight: 500 !important; color: #8fa4ff !important;
}

.stRadio > div { gap: 0.3rem !important; }

.stTextArea textarea {
    border: 1px solid rgba(100, 130, 255, 0.2) !important; border-radius: 8px !important;
    background: rgba(15, 20, 50, 0.5) !important;
}
.stTextArea textarea:focus {
    border-color: rgba(100, 130, 255, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(100, 130, 255, 0.1) !important;
}

.sidebar-brand {
    text-align: center; padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(100, 120, 255, 0.15); margin-bottom: 1.5rem;
}
.sidebar-brand h2 {
    font-size: 1.3rem; font-weight: 700;
    background: linear-gradient(135deg, #8fa4ff, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
}
.sidebar-brand p {
    font-size: 0.75rem; color: rgba(180, 190, 220, 0.5); margin: 0.25rem 0 0 0;
}

.login-card {
    max-width: 400px; margin: 4rem auto; padding: 2.5rem;
    background: linear-gradient(135deg, rgba(20, 25, 60, 0.8) 0%, rgba(30, 20, 60, 0.6) 100%);
    border: 1px solid rgba(100, 120, 255, 0.2); border-radius: 16px;
    backdrop-filter: blur(10px); text-align: center;
}
</style>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = not _sheets_available()
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "week_idx" not in st.session_state:
        st.session_state.week_idx = 0
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
    for wn in WEEK_NUMBERS:
        key = f"week_{wn}_stage"
        if key not in st.session_state:
            st.session_state[key] = 0


def _current_week_stage_key() -> str:
    wn = WEEKS[st.session_state.week_idx]["week_number"]
    return f"week_{wn}_stage"


def _award_xp(amount: int, reason: str):
    key = f"xp_{reason}"
    if key not in st.session_state:
        st.session_state[key] = True
        st.session_state.xp += amount


def _advance_stage(new_stage: int):
    st.session_state.stage = new_stage
    wk_key = _current_week_stage_key()
    if new_stage > st.session_state.get(wk_key, 0):
        st.session_state[wk_key] = new_stage
    if _sheets_available():
        _save_user_progress(st.session_state.username)


def _progress_fraction() -> float:
    return st.session_state.stage / 5


def _img_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


# ---------------------------------------------------------------------------
# Citation network
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_citation_network(openalex_id: str, max_citing: int = 15, max_refs: int = 10):
    base = "https://api.openalex.org/works"
    headers = {"Accept": "application/json"}

    citing = requests.get(
        base,
        params={
            "filter": f"cites:{openalex_id}",
            "per_page": max_citing,
            "sort": "cited_by_count:desc",
            "select": "id,doi,title,publication_year,authorships,cited_by_count",
        },
        headers=headers, timeout=10,
    ).json().get("results", [])

    center_data = requests.get(
        f"{base}/{openalex_id}",
        params={"select": "id,doi,title,publication_year,authorships,cited_by_count,referenced_works"},
        headers=headers, timeout=10,
    ).json()

    ref_ids = center_data.get("referenced_works", [])[:max_refs]
    refs = []
    if ref_ids:
        id_filter = "|".join(r.split("/")[-1] for r in ref_ids)
        refs = requests.get(
            base,
            params={
                "filter": f"openalex:{id_filter}",
                "per_page": max_refs,
                "select": "id,doi,title,publication_year,authorships,cited_by_count",
            },
            headers=headers, timeout=10,
        ).json().get("results", [])

    return center_data, citing, refs


def _first_author(work: dict) -> str:
    authorships = work.get("authorships", [])
    if authorships:
        return authorships[0].get("author", {}).get("display_name", "Unknown")
    return "Unknown"


def _short_label(work: dict, max_len: int = 25) -> str:
    title = work.get("title", "Untitled") or "Untitled"
    if len(title) > max_len:
        title = title[:max_len - 1] + "…"
    return title


def _doi_url(work: dict) -> str:
    doi = work.get("doi")
    if doi:
        return doi if doi.startswith("http") else f"https://doi.org/{doi}"
    return ""


def _render_citation_network(paper: dict):
    openalex_id = paper.get("openalex_id")
    if not openalex_id:
        st.info("No citation data available for this paper.")
        return

    with st.spinner("Fetching citation network from OpenAlex..."):
        try:
            center, citing, refs = _fetch_citation_network(openalex_id)
        except Exception:
            st.error("Could not fetch citation data. Please try again later.")
            return

    nodes, edges, node_lookup = [], [], {}
    cx, cy, radius = 350, 250, 180

    node_lookup[openalex_id] = center
    nodes.append(Node(
        id=openalex_id, label=_short_label(center),
        title=center.get("title", ""), size=35, color="#a855f7",
        font={"color": "#e0e4ff", "size": 11, "strokeWidth": 3, "strokeColor": "#0a0e27"},
        shape="dot", x=cx, y=cy,
    ))

    n_citing = len(citing)
    for i, work in enumerate(citing):
        wid = work["id"].split("/")[-1]
        node_lookup[wid] = work
        angle = math.pi + (math.pi / (n_citing + 1)) * (i + 1)
        nodes.append(Node(
            id=wid, label=_short_label(work), title=work.get("title", ""),
            size=20, color="#6482ff",
            font={"color": "#8fa4ff", "size": 9, "strokeWidth": 2, "strokeColor": "#0a0e27"},
            shape="dot",
            x=int(cx + radius * math.cos(angle)), y=int(cy + radius * math.sin(angle)),
        ))
        edges.append(Edge(source=wid, target=openalex_id, color="rgba(100,130,255,0.4)", width=1.5))

    ref_idx = 0
    n_refs = len(refs)
    for work in refs:
        wid = work["id"].split("/")[-1]
        node_lookup[wid] = work
        if not any(n.id == wid for n in nodes):
            angle = (math.pi / (n_refs + 1)) * (ref_idx + 1)
            nodes.append(Node(
                id=wid, label=_short_label(work), title=work.get("title", ""),
                size=20, color="#50c878",
                font={"color": "#50c878", "size": 9, "strokeWidth": 2, "strokeColor": "#0a0e27"},
                shape="dot",
                x=int(cx + radius * math.cos(angle)), y=int(cy + radius * math.sin(angle)),
            ))
            ref_idx += 1
        edges.append(Edge(source=openalex_id, target=wid, color="rgba(80,200,120,0.4)", width=1.5))

    config = Config(
        width=700, height=500, directed=True, physics=False, hierarchical=False,
        nodeHighlightBehavior=True, highlightColor="#ffb432", collapsible=False,
        node={"labelProperty": "label"}, link={"renderLabel": False},
        backgroundColor="rgba(0,0,0,0)",
    )

    st.markdown(
        '<p style="font-size:0.8rem; color:rgba(180,190,220,0.6);">'
        '<span style="color:#a855f7;">●</span> This paper &nbsp; '
        '<span style="color:#6482ff;">●</span> Cited by &nbsp; '
        '<span style="color:#50c878;">●</span> References &nbsp; '
        '<span style="font-style:italic;">Click a node to see details</span></p>',
        unsafe_allow_html=True,
    )

    selected_node = agraph(nodes=nodes, edges=edges, config=config)

    if selected_node and selected_node in node_lookup:
        work = node_lookup[selected_node]
        doi_link = _doi_url(work)
        title = work.get("title", "Untitled") or "Untitled"
        author = _first_author(work)
        year = work.get("publication_year", "—")
        cites = work.get("cited_by_count", 0)
        st.markdown(
            f'<div style="padding:1rem; margin:0.5rem 0; border-radius:8px; '
            f'background:rgba(100,130,255,0.08); border:1px solid rgba(100,130,255,0.2);">'
            f'<strong style="color:#e0e4ff;">{title}</strong><br>'
            f'<span style="font-size:0.85rem; color:rgba(180,190,220,0.7);">'
            f'{author} · {year} · {cites} citations</span><br>',
            unsafe_allow_html=True,
        )
        if doi_link:
            st.markdown(f"[Open paper ↗]({doi_link})")
        st.markdown("</div>", unsafe_allow_html=True)

    def _render_paper_list(works):
        works_sorted = sorted(works, key=lambda w: w.get("cited_by_count", 0), reverse=True)
        for w in works_sorted:
            doi_link = _doi_url(w)
            title = w.get("title", "Untitled") or "Untitled"
            author = _first_author(w)
            year = w.get("publication_year", "—")
            cites = w.get("cited_by_count", 0)
            if doi_link:
                st.markdown(
                    f'<div style="padding:0.5rem 0; border-bottom:1px solid rgba(100,120,255,0.1);">'
                    f'<a href="{doi_link}" target="_blank" style="color:#8fa4ff; text-decoration:none; font-weight:500;">{title}</a>'
                    f'<br><span style="font-size:0.8rem; color:rgba(180,190,220,0.6);">{author} · {year} · {cites} citations</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="padding:0.5rem 0; border-bottom:1px solid rgba(100,120,255,0.1);">'
                    f'<span style="color:#e0e4ff; font-weight:500;">{title}</span>'
                    f'<br><span style="font-size:0.8rem; color:rgba(180,190,220,0.6);">{author} · {year} · {cites} citations</span></div>',
                    unsafe_allow_html=True,
                )

    tab_cited, tab_refs = st.tabs(["Cited by", "References"])
    with tab_cited:
        if citing:
            st.caption(f"{len(citing)} papers that cite this work (showing top by citation count)")
            _render_paper_list(citing)
        else:
            st.info("No citing papers found.")
    with tab_refs:
        if refs:
            st.caption(f"{len(refs)} references from this paper")
            _render_paper_list(refs)
        else:
            st.info("No references found.")


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------

def _render_login():
    if HERO_IMAGE.exists():
        img_b64 = _img_to_base64(HERO_IMAGE)
        st.markdown(
            f'<div class="hero-banner">'
            f'<img src="data:image/jpeg;base64,{img_b64}" alt="banner">'
            f'<div class="hero-overlay"><h1>Paper Quest</h1>'
            f'<p>Neuroscience Module</p></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("#### Welcome! Enter your username to continue.")
    username = st.text_input("Username", placeholder="e.g. jsmith", label_visibility="collapsed")
    if st.button("Start", type="primary", use_container_width=True):
        if not username or not username.strip():
            st.error("Please enter a username.")
        else:
            username = username.strip()
            row = _load_user_progress(username)
            if row is None:
                st.session_state.username = username
                st.session_state.logged_in = True
                st.rerun()
            elif row == {}:
                _restore_progress_to_session(username, {})
                _save_user_progress(username)
                st.rerun()
            else:
                _restore_progress_to_session(username, row)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_hero(week):
    if HERO_IMAGE.exists():
        img_b64 = _img_to_base64(HERO_IMAGE)
        st.markdown(
            f'<div class="hero-banner">'
            f'<img src="data:image/jpeg;base64,{img_b64}" alt="banner">'
            f'<div class="hero-overlay"><h1>Paper Quest</h1>'
            f'<p>{week["subtitle"]}</p></div></div>',
            unsafe_allow_html=True,
        )


def _render_sidebar(week):
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><h2>Paper Quest</h2>'
            '<p>Neuroscience Module</p></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.username:
            st.caption(f"Logged in as **{st.session_state.username}**")
            if st.button("Log out", type="secondary", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        if len(WEEKS) > 1:
            week_labels = []
            for i, w in enumerate(WEEKS):
                if _week_is_unlocked(i):
                    week_labels.append(w["title"])
                else:
                    week_labels.append(f"\U0001f512 {w['title']}")

            selected = st.selectbox("Select week", week_labels, index=st.session_state.week_idx)
            new_idx = week_labels.index(selected)
            if selected.startswith("\U0001f512"):
                st.warning("Complete the previous week to unlock this one.")
            elif new_idx != st.session_state.week_idx:
                st.session_state.week_idx = new_idx
                wn = WEEKS[new_idx]["week_number"]
                st.session_state.stage = st.session_state.get(f"week_{wn}_stage", 0)
                st.session_state.mcq_answers = {}
                st.session_state.sa_revealed = set()
                st.session_state.sa_self_marks = {}
                st.rerun()

        st.markdown("#### Journey")
        st.progress(_progress_fraction())

        stage_config = [
            ("Podcast", "\U0001f3a7"),
            ("Read Paper 1", "\U0001f4d6"),
            ("Paper 1 Questions", "\U0001f4dd"),
            ("Read Paper 2", "\U0001f4d6"),
            ("Paper 2 Questions", "\U0001f4dd"),
            ("Complete", "✅"),
        ]

        for i, (label, icon) in enumerate(stage_config):
            if i < st.session_state.stage:
                css_class, status = "stage-done", "✓"
            elif i == st.session_state.stage:
                css_class, status = "stage-active", "→"
            else:
                css_class, status = "stage-locked", "\U0001f512"
            st.markdown(
                f'<div class="stage-pill {css_class}">{status} {icon} {label}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="xp-display">'
            f'<div class="xp-label">Experience Points</div>'
            f'<div class="xp-number">{st.session_state.xp}</div></div>',
            unsafe_allow_html=True,
        )


def _render_podcast(week):
    _render_hero(week)

    st.markdown(
        '<div class="section-header"><div class="section-icon">\U0001f3a7</div>'
        '<div><p class="section-title">Listen to the Podcast</p>'
        '<p class="section-subtitle">An introduction to this week\'s two papers</p>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    podcast_cfg = week.get("podcast", {})
    embed_url = podcast_cfg.get("embed_url")

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    if embed_url:
        components.html(
            f'<iframe src="{embed_url}" width="100%" height="80" '
            f'allow="autoplay" style="border:none; border-radius:8px;"></iframe>',
            height=100,
        )
    else:
        st.warning("Podcast not available.")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        wk = week["week_number"]
        if st.button("I've listened — continue ▶️", type="primary", use_container_width=True):
            _award_xp(10, f"w{wk}_podcast")
            _advance_stage(1)
            st.rerun()


def _render_read_paper(week, paper_index: int, next_stage: int):
    paper = week["papers"][paper_index]
    wk = week["week_number"]

    st.markdown(
        f'<div class="section-header"><div class="section-icon">\U0001f4d6</div>'
        f'<div><p class="section-title">Read Paper {paper_index + 1}</p>'
        f'<p class="section-subtitle">Take your time — the questions come next</p>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"**{paper['title']}**")
    st.markdown(
        f'<div class="paper-meta">'
        f'<span class="meta-tag">\U0001f464 {paper["authors"]}</span>'
        f'<span class="meta-tag">\U0001f4f0 {paper.get("journal", "")}</span></div>',
        unsafe_allow_html=True,
    )

    embed_url = paper.get("embed_url")
    if embed_url:
        components.html(
            f'<iframe src="{embed_url}" width="100%" height="800" '
            f'allow="autoplay" style="border:none; border-radius:8px;"></iframe>',
            height=820,
        )
    else:
        st.warning("No embedded viewer available for this paper.")

    with st.expander("\U0001f52c Explore the citation network"):
        _render_citation_network(paper)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("I've read the paper — continue ▶️", type="primary", use_container_width=True):
            _award_xp(10, f"w{wk}_read_p{paper_index}")
            _advance_stage(next_stage)
            st.rerun()


def _render_paper_questions(week, paper_index: int):
    paper = week["papers"][paper_index]
    wk = week["week_number"]

    st.markdown(
        f'<div class="section-header"><div class="section-icon">\U0001f4dd</div>'
        f'<div><p class="section-title">Paper {paper_index + 1} — Comprehension</p>'
        f'<p class="section-subtitle">{paper["authors"]} · {paper.get("journal", "")}</p>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Multiple Choice")
    mcq_complete = True
    for i, mcq in enumerate(paper.get("mcqs", [])):
        key = f"w{wk}_mcq_p{paper_index}_q{i}"
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"**Q{i+1}.** {mcq['question']}")
        selected = st.radio(
            "Select your answer:", mcq["options"],
            index=None, key=f"radio_{key}", label_visibility="collapsed",
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
    st.markdown("#### Short Answer")
    sa_complete = True
    for i, sa in enumerate(paper.get("short_answers", [])):
        sa_key = f"w{wk}_sa_p{paper_index}_q{i}"
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
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
        label = "Continue to Paper 2 ▶️" if paper_index == 0 else "Complete week \U0001f389"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(label, type="primary", use_container_width=True):
                _advance_stage(next_stage)
                st.rerun()
    else:
        st.info("Answer all questions above to continue.")


def _render_complete(week):
    st.balloons()
    _render_hero(week)
    st.markdown(
        f'<div class="completion-card">'
        f'<div class="completion-icon">\U0001f389</div>'
        f'<h2 style="color:#50c878; margin-bottom:0.5rem;">Week Complete!</h2>'
        f'<p style="color:rgba(200,210,255,0.7); font-size:1.1rem;">'
        f'You\'ve finished <strong>{week["title"]}</strong></p>'
        f'<div style="margin-top:1.5rem;">'
        f'<div class="xp-label">Total XP Earned</div>'
        f'<div class="xp-number">{st.session_state.xp}</div></div>'
        f'<p style="color:rgba(180,190,220,0.5); margin-top:1.5rem; font-size:0.9rem;">'
        f'Come back next week for more papers!</p></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Paper Quest", page_icon="\U0001f9e0", layout="centered")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    _init_state()

    if not WEEKS:
        st.error("No week configs found in weeks/ directory.")
        return

    if not st.session_state.logged_in:
        _render_login()
        return

    week_idx = st.session_state.week_idx
    if not _week_is_unlocked(week_idx):
        st.session_state.week_idx = 0
        st.rerun()

    week = WEEKS[week_idx]
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
