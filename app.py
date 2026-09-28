"""
MeetMind AI — single-file Streamlit app (converted from the FastAPI main.py).

Reuses the existing core/ and utils/ pipeline. No AI logic is duplicated —
this file orchestrates the pipeline and enforces the demo's usage limits
(one video per session, 10-minute cap, 10 questions, 300-character questions).

Place this file in the project root (next to core/ and utils/).
Run:  uv run python -m streamlit run streamlit_app.py
"""
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Optional

import streamlit as st

# Must be the first Streamlit command.
st.set_page_config(page_title="MeetMind AI", page_icon="🧠", layout="centered")

from dotenv import load_dotenv

from setup_deno import install_deno

# Make sure Deno exists before yt-dlp is used.
DENO_PATH = install_deno()

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

# On Streamlit Community Cloud the key comes from st.secrets instead of .env.
# It stays server-side either way — the browser never sees it.
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

from core.extractor import (  # noqa: E402
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import ask_question, build_rag_chain  # noqa: E402
from core.summarizer import generate_title, summarize  # noqa: E402
from core.transcriber import transcribe_all_chunks  # noqa: E402
from utils.video_processor import process_input  # noqa: E402

# ---------------------------------------------------------------------------
# Demo limits
# ---------------------------------------------------------------------------
MAX_DURATION_SECONDS = 10 * 60
MAX_QUESTIONS = 10
MAX_QUESTION_LENGTH = 300
SUGGESTIONS = [
    "What were the main decisions?",
    "What action items were assigned?",
    "What were the key concerns?",
    "Summarize the most important points.",
]

# ---------------------------------------------------------------------------
# Session state — replaces the FastAPI SESSIONS dict / cookie.
# One video + 10 questions per browser session.
# ---------------------------------------------------------------------------
DEFAULTS = {
    "video_submitted": False,
    "result": None,
    "rag_chain": None,
    "messages": [],
    "question_count": 0,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Duration checking (same logic as the FastAPI version)
# ---------------------------------------------------------------------------
def get_duration_seconds(source: str, is_youtube: bool) -> Optional[float]:
    """Best-effort duration lookup. Returns None if it can't be determined,
    in which case processing proceeds (fail-open)."""
    if is_youtube:
        try:
            import yt_dlp

            with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
                info = ydl.extract_info(source, download=False)
                duration = info.get("duration")
                return float(duration) if duration else None
        except Exception:
            return None
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json", source,
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Pipeline — same steps and logging as the FastAPI worker(), but the
# progress is shown live with st.status instead of polling /api/status.
# ---------------------------------------------------------------------------
def run_pipeline(source: str) -> None:
    with st.status("Processing your video...", expanded=True) as status:
        print("[MeetMind] Starting video processing...")
        st.write("Processing video & extracting audio...")
        chunks = process_input(source)
        print(f"[MeetMind] Audio processing completed: {len(chunks)} chunk(s)")

        print("[MeetMind] Starting transcription...")
        st.write("Transcribing & translating speech...")
        transcript = transcribe_all_chunks(chunks)
        print(f"[MeetMind] Transcription completed: {len(transcript)} characters")

        st.write("Generating title & summary...")
        print("[MeetMind] Generating title...")
        title = generate_title(transcript)
        print("[MeetMind] Title generated")

        print("[MeetMind] Generating summary...")
        summary = summarize(transcript)
        print("[MeetMind] Summary generated")

        st.write("Extracting action items, decisions & open questions...")
        print("[MeetMind] Extracting action items...")
        action_items = extract_action_items(transcript)
        print("[MeetMind] Action items extracted")

        print("[MeetMind] Extracting key decisions...")
        decisions = extract_key_decisions(transcript)
        print("[MeetMind] Key decisions extracted")

        print("[MeetMind] Extracting questions...")
        questions = extract_questions(transcript)
        print("[MeetMind] Questions extracted")

        st.write("Building knowledge base...")
        print("[MeetMind] Building RAG chain...")
        rag_chain = build_rag_chain(transcript)
        print("[MeetMind] RAG chain created")

        st.session_state.rag_chain = rag_chain
        st.session_state.result = {
            "title": title,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": decisions,
            "open_questions": questions,
            "transcript": transcript,
        }
        status.update(label="Ready — ask questions below", state="complete", expanded=False)
        print("[MeetMind] Processing completed successfully!")


# ---------------------------------------------------------------------------
# Analyze (replaces POST /api/analyze)
# ---------------------------------------------------------------------------
def handle_analyze(youtube_url: str, uploaded_file) -> None:
    if st.session_state.video_submitted:
        st.error("**Session limit reached** — This session is limited to one video.")
        return
    if not youtube_url and uploaded_file is None:
        st.warning("Please enter a YouTube URL or upload a video file.")
        return

    tmp_dir: Optional[Path] = None
    try:
        if uploaded_file is not None:
            tmp_dir = Path(tempfile.mkdtemp(prefix="meetmind_"))
            path = tmp_dir / f"upload{Path(uploaded_file.name).suffix}"
            path.write_bytes(uploaded_file.getbuffer())
            source, is_youtube = str(path), False
        else:
            source, is_youtube = youtube_url.strip(), True

        duration = get_duration_seconds(source, is_youtube)
        if duration is not None and duration > MAX_DURATION_SECONDS:
            st.error("**Video too long** — Please choose a video that is 10 minutes or shorter.")
            return

        # Lock the session to this one video before the heavy work starts.
        st.session_state.video_submitted = True

        try:
            run_pipeline(source)
        except Exception as exc:  # never show internals to the user
            print(f"[MeetMind] processing error: {exc}")
            traceback.print_exc()
            st.error("**Something went wrong** — We couldn't complete this request. Please try again.")
            return

        st.rerun()
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Chat (replaces POST /api/chat)
# ---------------------------------------------------------------------------
def handle_question(question: str) -> None:
    question = question.strip()
    if not question:
        return
    if len(question) > MAX_QUESTION_LENGTH:
        st.error("**Question too long** — Please keep your question under 300 characters.")
        return
    if st.session_state.question_count >= MAX_QUESTIONS:
        return
    if st.session_state.rag_chain is None:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    try:
        with st.spinner("Thinking..."):
            answer = ask_question(st.session_state.rag_chain, question)
        st.session_state.question_count += 1
    except Exception as exc:
        print(f"[MeetMind] chat error: {exc}")
        traceback.print_exc()
        answer = "Something went wrong — we couldn't complete this request. Please try again."
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()


def render_items(items) -> None:
    """Extractors may return a list or a text block — handle both."""
    if not items:
        st.write("None identified.")
    elif isinstance(items, list):
        st.markdown("\n".join(f"- {item}" for item in items))
    else:
        st.markdown(str(items))


# ---------------------------------------------------------------------------
# UI — hero
# ---------------------------------------------------------------------------
st.title("🧠 MeetMind AI")
st.markdown("##### AI-Powered Video & Meeting Intelligence")
st.caption(
    "Turn conversations into searchable knowledge. Upload a video, extract the "
    "insights, and ask questions using AI."
)

# ---------------------------------------------------------------------------
# UI — input
# ---------------------------------------------------------------------------
locked = st.session_state.video_submitted

with st.container(border=True):
    tab_url, tab_file = st.tabs(["YouTube URL", "Upload file"])
    with tab_url:
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            disabled=locked,
        )
    with tab_file:
        uploaded_file = st.file_uploader(
            "Video or audio file",
            type=["mp4", "mov", "webm", "mp3", "wav", "m4a"],
            disabled=locked,
        )

    st.caption("Maximum duration: 10 minutes · One video per session")

    if st.button("Analyze Video", type="primary", disabled=locked):
        handle_analyze(youtube_url, uploaded_file)

    if locked:
        st.info("This session is limited to one video.")

# ---------------------------------------------------------------------------
# UI — results
# ---------------------------------------------------------------------------
result = st.session_state.result
if result:
    st.header(result["title"])

    with st.container(border=True):
        st.subheader("Summary")
        st.markdown(result["summary"])

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("Action items")
            render_items(result["action_items"])
    with col2:
        with st.container(border=True):
            st.subheader("Key decisions")
            render_items(result["key_decisions"])
    with col3:
        with st.container(border=True):
            st.subheader("Open questions")
            render_items(result["open_questions"])

    with st.expander("View full transcript"):
        st.write(result["transcript"])

    # -----------------------------------------------------------------------
    # UI — chat
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Ask MeetMind")
    st.caption("Ask questions about your video using AI-powered retrieval.")

    remaining = MAX_QUESTIONS - st.session_state.question_count
    st.markdown(f"**Questions remaining: {remaining} / {MAX_QUESTIONS}**")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    pending = None
    if not st.session_state.messages and remaining > 0:
        cols = st.columns(2)
        for i, suggestion in enumerate(SUGGESTIONS):
            if cols[i % 2].button(suggestion, key=f"sugg_{i}", use_container_width=True):
                pending = suggestion

    if remaining <= 0:
        st.warning("**Question limit reached** — You've reached the 10-question limit for this session.")

    typed = st.chat_input(
        "Ask something about the meeting...",
        max_chars=MAX_QUESTION_LENGTH,
        disabled=remaining <= 0,
    )
    question = typed or pending
    if question and remaining > 0:
        handle_question(question)
