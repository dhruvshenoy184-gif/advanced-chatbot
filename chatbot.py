import streamlit as st
import anthropic
import time
import random

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS · AI Chat",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e6f0;
    font-family: 'Syne', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #3a3a5c; border-radius: 2px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d0d18 !important;
    border-right: 1px solid #1e1e32 !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #a0a0c8 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Main container ── */
[data-testid="stMain"] { background: #0a0a0f !important; }
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Header ── */
.nexus-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 32px 16px;
    border-bottom: 1px solid #1e1e32;
    background: linear-gradient(180deg, #0d0d18 0%, #0a0a0f 100%);
    position: sticky; top: 0; z-index: 100;
}
.nexus-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #6c63ff, #a855f7);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; animation: pulse-logo 3s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes pulse-logo {
    0%, 100% { box-shadow: 0 0 0 0 rgba(108,99,255,0.4); }
    50% { box-shadow: 0 0 20px 8px rgba(108,99,255,0.15); }
}
.nexus-title { font-size: 1.4rem; font-weight: 800; letter-spacing: -0.02em; }
.nexus-title span { color: #6c63ff; }
.nexus-status {
    margin-left: auto; display: flex; align-items: center; gap: 8px;
    font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #6c63ff;
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #4ade80;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
}

/* ── Chat container ── */
.chat-wrapper {
    padding: 24px 32px;
    display: flex; flex-direction: column; gap: 20px;
    min-height: calc(100vh - 180px);
}

/* ── Message bubbles ── */
.msg-row {
    display: flex; gap: 14px; align-items: flex-start;
    animation: slide-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.msg-row.user { flex-direction: row-reverse; }
@keyframes slide-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Avatars */
.avatar {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0; font-weight: 700;
    border: 2px solid transparent;
}
.avatar.ai {
    background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
    border-color: #6c63ff;
    box-shadow: 0 0 12px rgba(108,99,255,0.3);
    color: #a78bfa;
}
.avatar.user {
    background: linear-gradient(135deg, #1a2a1e, #2a4a2e);
    border-color: #4ade80;
    color: #86efac;
}

/* Bubble */
.bubble {
    max-width: 72%;
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 0.92rem;
    line-height: 1.65;
    position: relative;
}
.bubble.ai {
    background: #111126;
    border: 1px solid #2a2a4e;
    border-radius: 4px 16px 16px 16px;
    color: #d4d0f0;
}
.bubble.user {
    background: linear-gradient(135deg, #1c1c3a, #242448);
    border: 1px solid #3a3a6a;
    border-radius: 16px 4px 16px 16px;
    color: #e8e6f8;
}

/* Bubble meta */
.bubble-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: #4a4a6a;
    margin-top: 6px;
    display: flex; align-items: center; gap: 6px;
}
.msg-row.user .bubble-meta { justify-content: flex-end; }

/* Code blocks inside bubbles */
.bubble pre {
    background: #0d0d18;
    border: 1px solid #2a2a4e;
    border-left: 3px solid #6c63ff;
    border-radius: 8px;
    padding: 12px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    overflow-x: auto;
    margin: 10px 0;
    color: #a78bfa;
}
.bubble code {
    background: #1a1a2e;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Space Mono', monospace;
    font-size: 0.82em;
    color: #c4b5fd;
}

/* ── Typing indicator ── */
.typing-indicator {
    display: flex; align-items: center; gap: 5px;
    padding: 14px 18px;
    background: #111126;
    border: 1px solid #2a2a4e;
    border-radius: 4px 16px 16px 16px;
    width: fit-content;
}
.typing-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #6c63ff;
    animation: typing-bounce 1.2s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
    40% { transform: translateY(-6px); opacity: 1; }
}

/* ── Input area ── */
.input-area {
    position: sticky; bottom: 0;
    padding: 16px 32px 20px;
    background: linear-gradient(0deg, #0a0a0f 80%, transparent 100%);
    border-top: 1px solid #1e1e32;
}
[data-testid="stChatInput"] {
    background: #111126 !important;
    border: 1px solid #2a2a4e !important;
    border-radius: 12px !important;
    color: #e8e6f0 !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e8e6f0 !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: #6c63ff !important; }

/* ── Sidebar elements ── */
.sidebar-section {
    background: #111126;
    border: 1px solid #1e1e32;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.sidebar-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #6c63ff;
    margin-bottom: 8px;
}

/* Selectbox & slider overrides */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSlider"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
}
.stSelectbox [data-baseweb="select"] > div {
    background: #0d0d18 !important;
    border-color: #2a2a4e !important;
    color: #a0a0c8 !important;
}
[data-testid="stTextArea"] textarea {
    background: #0d0d18 !important;
    border-color: #2a2a4e !important;
    color: #a0a0c8 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #6c63ff !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid #2a2a4e !important;
    color: #a0a0c8 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #6c63ff !important;
    color: #a78bfa !important;
    background: rgba(108,99,255,0.08) !important;
}

/* Token counter */
.token-bar-bg {
    height: 4px; background: #1e1e32; border-radius: 2px; overflow: hidden;
}
.token-bar-fill {
    height: 100%; border-radius: 2px;
    background: linear-gradient(90deg, #6c63ff, #a855f7);
    transition: width 0.4s ease;
}

/* Empty state */
.empty-state {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-height: 50vh;
    gap: 16px; color: #2a2a4e; text-align: center;
}
.empty-hex {
    font-size: 64px;
    animation: float 4s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-12px); }
}
.empty-title { font-size: 1.5rem; font-weight: 800; color: #3a3a5c; }
.empty-sub { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #2a2a4e; }

/* Divider */
.nexus-divider { border: none; border-top: 1px solid #1e1e32; margin: 8px 0; }

/* Toast / badge */
.model-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1a1a2e; border: 1px solid #3a3a5c;
    border-radius: 20px; padding: 4px 10px;
    font-family: 'Space Mono', monospace; font-size: 0.65rem;
    color: #6c63ff;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────

MODELS = {
    "claude-opus-4-5": "Opus 4.5 · Most Capable",
    "claude-sonnet-4-5": "Sonnet 4.5 · Balanced",
    "claude-haiku-4-5": "Haiku 4.5 · Fastest",
}

SYSTEM_PRESETS = {
    "Default Assistant": "You are NEXUS, an advanced AI assistant. Be concise, insightful, and helpful.",
    "Code Expert": "You are a senior software engineer and code reviewer. Provide detailed, production-ready code with explanations.",
    "Creative Writer": "You are a creative writing assistant. Be imaginative, vivid, and narratively engaging.",
    "Data Analyst": "You are a data analyst. Provide structured analysis, suggest visualizations, and explain statistical concepts clearly.",
    "Custom": "",
}

def get_timestamp():
    return time.strftime("%H:%M")

def count_tokens(messages):
    """Rough token estimate."""
    text = " ".join(m["content"] for m in messages)
    return len(text.split()) * 1.3

def render_message(role, content, idx=0):
    """Render a single chat message as HTML."""
    avatar_ai   = "⬡"
    avatar_user = "U"
    ts = get_timestamp()

    if role == "assistant":
        html = f"""
        <div class="msg-row" style="animation-delay:{idx*0.05}s">
          <div class="avatar ai">{avatar_ai}</div>
          <div>
            <div class="bubble ai">{content}</div>
            <div class="bubble-meta">⬡ NEXUS &nbsp;·&nbsp; {ts}</div>
          </div>
        </div>
        """
    else:
        html = f"""
        <div class="msg-row user" style="animation-delay:{idx*0.05}s">
          <div class="avatar user">{avatar_user}</div>
          <div>
            <div class="bubble user">{content}</div>
            <div class="bubble-meta">{ts} &nbsp;·&nbsp; You</div>
          </div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "claude-sonnet-4-5"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = SYSTEM_PRESETS["Default Assistant"]
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 1024
if "streaming" not in st.session_state:
    st.session_state.streaming = True


# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px">
        <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                    text-transform:uppercase;letter-spacing:.12em;color:#4a4a6a;
                    margin-bottom:4px;">Navigation</div>
        <div style="font-size:1.1rem;font-weight:800;color:#e8e6f0;">⬡ NEXUS</div>
    </div>
    """, unsafe_allow_html=True)

    # Model selector
    st.markdown('<div class="sidebar-label">Model</div>', unsafe_allow_html=True)
    model_key = st.selectbox(
        "model_select", list(MODELS.keys()),
        format_func=lambda k: MODELS[k],
        label_visibility="collapsed",
        index=list(MODELS.keys()).index(st.session_state.model)
    )
    st.session_state.model = model_key

    st.markdown('<hr class="nexus-divider"/>', unsafe_allow_html=True)

    # System prompt
    st.markdown('<div class="sidebar-label">Persona</div>', unsafe_allow_html=True)
    preset = st.selectbox(
        "preset", list(SYSTEM_PRESETS.keys()),
        label_visibility="collapsed"
    )
    if preset != "Custom":
        st.session_state.system_prompt = SYSTEM_PRESETS[preset]

    system_prompt_val = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt,
        height=110,
        label_visibility="collapsed",
        placeholder="Enter system instructions…"
    )
    st.session_state.system_prompt = system_prompt_val

    st.markdown('<hr class="nexus-divider"/>', unsafe_allow_html=True)

    # Parameters
    st.markdown('<div class="sidebar-label">Parameters</div>', unsafe_allow_html=True)
    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.temperature, 0.05
    )
    st.session_state.max_tokens = st.slider(
        "Max Tokens", 256, 4096, st.session_state.max_tokens, 128
    )
    st.session_state.streaming = st.toggle("Stream response", value=st.session_state.streaming)

    st.markdown('<hr class="nexus-divider"/>', unsafe_allow_html=True)

    # Stats
    token_est = int(count_tokens(st.session_state.messages))
    token_pct = min(100, int(token_est / 200000 * 100))
    st.markdown(f"""
    <div class="sidebar-label">Context Window</div>
    <div style="font-family:'Space Mono',monospace;font-size:0.68rem;
                color:#a0a0c8;margin-bottom:6px;">
        ~{token_est:,} tokens used
    </div>
    <div class="token-bar-bg">
        <div class="token-bar-fill" style="width:{token_pct}%"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        msg_count = len(st.session_state.messages)
        st.markdown(f"""
        <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                    color:#4a4a6a;padding-top:8px;text-align:center;">
            {msg_count} messages
        </div>
        """, unsafe_allow_html=True)


# ─── Main Area ───────────────────────────────────────────────────────────────
# Header
st.markdown(f"""
<div class="nexus-header">
  <div class="nexus-logo">⬡</div>
  <div>
    <div class="nexus-title">NEX<span>US</span></div>
    <div style="font-family:'Space Mono',monospace;font-size:0.62rem;color:#4a4a6a;">
        Advanced AI Interface
    </div>
  </div>
  <div class="nexus-status">
    <div class="status-dot"></div>
    ONLINE &nbsp;·&nbsp;
    <span class="model-badge">⬡ {MODELS[st.session_state.model]}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Chat messages
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-hex">⬡</div>
      <div class="empty-title">NEXUS is ready.</div>
      <div class="empty-sub">Start a conversation below ↓</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        render_message(msg["role"], msg["content"], i)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Chat Input ──────────────────────────────────────────────────────────────
if prompt := st.chat_input("Message NEXUS…"):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt, len(st.session_state.messages))

    # Build message list for API
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Typing indicator + response
    client = anthropic.Anthropic()

    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div style="display:flex;gap:14px;align-items:flex-start;padding:0 0 8px;">
      <div class="avatar ai">⬡</div>
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    response_placeholder = st.empty()
    full_response = ""

    try:
        if st.session_state.streaming:
            with client.messages.stream(
                model=st.session_state.model,
                max_tokens=st.session_state.max_tokens,
                system=st.session_state.system_prompt,
                messages=api_messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    typing_placeholder.empty()
                    # Live update with cursor blink effect
                    response_placeholder.markdown(f"""
                    <div class="msg-row">
                      <div class="avatar ai">⬡</div>
                      <div>
                        <div class="bubble ai">{full_response}<span style="animation:blink 1s infinite;color:#6c63ff;">▋</span></div>
                        <div class="bubble-meta">⬡ NEXUS &nbsp;·&nbsp; {get_timestamp()}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            # Final render without cursor
            response_placeholder.markdown(f"""
            <div class="msg-row">
              <div class="avatar ai">⬡</div>
              <div>
                <div class="bubble ai">{full_response}</div>
                <div class="bubble-meta">⬡ NEXUS &nbsp;·&nbsp; {get_timestamp()}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            typing_placeholder.empty()
            response = client.messages.create(
                model=st.session_state.model,
                max_tokens=st.session_state.max_tokens,
                system=st.session_state.system_prompt,
                messages=api_messages,
            )
            full_response = response.content[0].text
            render_message("assistant", full_response, len(st.session_state.messages) + 1)

    except anthropic.AuthenticationError:
        typing_placeholder.empty()
        response_placeholder.markdown("""
        <div class="msg-row">
          <div class="avatar ai" style="border-color:#f87171;">⬡</div>
          <div>
            <div class="bubble ai" style="border-color:#3a1a1a;color:#f87171;">
              ⚠ Authentication failed. Set your <code>ANTHROPIC_API_KEY</code> environment variable.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        full_response = "⚠ Authentication error."

    except Exception as e:
        typing_placeholder.empty()
        response_placeholder.markdown(f"""
        <div class="msg-row">
          <div class="avatar ai" style="border-color:#f87171;">⬡</div>
          <div>
            <div class="bubble ai" style="border-color:#3a1a1a;color:#f87171;">
              ⚠ Error: {str(e)}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        full_response = f"⚠ {str(e)}"

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
