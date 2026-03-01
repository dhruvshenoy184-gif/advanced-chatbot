"""
╔══════════════════════════════════════════════════════╗
║   G R O Q  ·  C H A T B O T                         ║
║   Powered by Groq API  ·  Built with Streamlit       ║
╚══════════════════════════════════════════════════════╝
Run:
    pip install -r requirements.txt
    export GROQ_API_KEY=gsk_...
    streamlit run chatbot_app.py
"""

import streamlit as st
import time
import os
from groq import Groq

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GROQ · CHAT",
    page_icon="▸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,600;0,700;1,400&family=Familjen+Grotesk:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:         #08090a;
  --bg2:        #0e1012;
  --bg3:        #141618;
  --border:     #1f2226;
  --border2:    #2a2d33;
  --amber:      #f0a500;
  --amber-dim:  #7a5200;
  --amber-glow: rgba(240,165,0,0.12);
  --green:      #2aff8f;
  --text:       #c8cdd4;
  --text-dim:   #4a5060;
  --text-bright:#edf0f4;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Familjen Grotesk', sans-serif;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; visibility: hidden !important; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--amber-dim); }

[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: 'IBM Plex Mono', monospace !important; }

[data-testid="stMain"],
[data-testid="stMainBlockContainer"] { background: var(--bg) !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Header ── */
.gq-header {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 28px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--bg2);
  position: sticky; top: 0; z-index: 200;
}
.gq-logo {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.1rem; font-weight: 700; color: var(--amber);
  border: 1px solid var(--amber-dim); padding: 4px 10px;
  border-radius: 4px; letter-spacing: 0.06em;
  box-shadow: 0 0 14px var(--amber-glow);
  animation: amber-pulse 3s ease-in-out infinite; white-space: nowrap;
}
@keyframes amber-pulse {
  0%,100%{ box-shadow: 0 0 14px var(--amber-glow); }
  50%    { box-shadow: 0 0 28px rgba(240,165,0,0.25); }
}
.gq-header-title { font-size: 0.72rem; font-family: 'IBM Plex Mono', monospace; color: var(--text-dim); line-height: 1.5; }
.gq-header-title strong { color: var(--text); display: block; font-size: 0.85rem; }
.gq-online {
  margin-left: auto; display: flex; align-items: center; gap: 7px;
  font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: var(--green); letter-spacing: 0.06em;
}
.online-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px var(--green); animation: blink-dot 2.4s ease-in-out infinite; }
@keyframes blink-dot { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ── Chat ── */
.chat-scroll-area { padding: 28px 28px 12px; display: flex; flex-direction: column; gap: 22px; min-height: calc(100vh - 200px); }

.msg-row { display: flex; gap: 12px; align-items: flex-start; animation: msg-appear 0.28s cubic-bezier(0.22,1,0.36,1) both; }
.msg-row.user { flex-direction: row-reverse; }
@keyframes msg-appear { from{opacity:0;transform:translateY(10px) scale(0.98)} to{opacity:1;transform:translateY(0) scale(1)} }

.av { width: 36px; height: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; font-weight: 700; flex-shrink: 0; }
.av.ai  { background: #0d0e10; border: 1px solid var(--amber-dim); color: var(--amber); box-shadow: 0 0 10px rgba(240,165,0,0.15); }
.av.user{ background: #0a1410; border: 1px solid #1a3a28; color: var(--green); }

.bubble { max-width: 70%; padding: 13px 17px 10px; line-height: 1.7; font-size: 0.9rem; }
.bubble.ai   { background: var(--bg2); border: 1px solid var(--border); border-left: 2px solid var(--amber-dim); border-radius: 2px 10px 10px 10px; color: var(--text-bright); }
.bubble.user { background: #0d1610; border: 1px solid #1a2e20; border-right: 2px solid #1a5a38; border-radius: 10px 2px 10px 10px; color: #b8f0d0; }

.bubble pre { background: #05060a; border: 1px solid var(--border2); border-left: 2px solid var(--amber); border-radius: 4px; padding: 11px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.76rem; overflow-x: auto; margin: 10px 0 4px; color: #ffd580; line-height: 1.55; }
.bubble code { background: #111318; padding: 1px 5px; border-radius: 3px; font-family: 'IBM Plex Mono', monospace; font-size: 0.8em; color: var(--amber); }

.bubble-meta { margin-top: 5px; font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; color: var(--text-dim); display: flex; align-items: center; gap: 5px; }
.msg-row.user .bubble-meta { justify-content: flex-end; }

/* Typing */
.typing-wrap { display: flex; gap: 12px; align-items: flex-start; }
.typing-bubble { background: var(--bg2); border: 1px solid var(--border); border-left: 2px solid var(--amber-dim); border-radius: 2px 10px 10px 10px; padding: 14px 18px; display: flex; align-items: center; gap: 5px; }
.t-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--amber); opacity: 0.5; animation: t-bounce 1.1s ease-in-out infinite; }
.t-dot:nth-child(2){animation-delay:.18s} .t-dot:nth-child(3){animation-delay:.36s}
@keyframes t-bounce { 0%,80%,100%{transform:translateY(0);opacity:.4} 40%{transform:translateY(-6px);opacity:1} }

/* Input */
[data-testid="stChatInput"] { background: var(--bg2) !important; border: 1px solid var(--border2) !important; border-radius: 8px !important; }
[data-testid="stChatInput"]:focus-within { border-color: var(--amber-dim) !important; box-shadow: 0 0 0 3px var(--amber-glow) !important; }
[data-testid="stChatInput"] textarea { color: var(--text-bright) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.85rem !important; caret-color: var(--amber) !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-dim) !important; }
[data-testid="stChatInputSubmitButton"] svg { fill: var(--amber) !important; }

/* Sidebar */
.sb-header { padding: 12px 4px 18px; border-bottom: 1px solid var(--border); margin-bottom: 16px; }
.sb-label { font-size: 0.58rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--amber); margin-bottom: 7px; margin-top: 14px; }
.sb-divider { border: none; border-top: 1px solid var(--border); margin: 10px 0; }

[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #0a0b0d !important; border-color: var(--border2) !important; color: var(--text) !important; }
[data-testid="stSidebar"] [data-testid="stTextArea"] textarea { background: #0a0b0d !important; border-color: var(--border2) !important; color: var(--text) !important; font-size: 0.74rem !important; border-radius: 6px !important; }
[data-testid="stSidebar"] [data-testid="stTextArea"] textarea:focus { border-color: var(--amber-dim) !important; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input { background: #0a0b0d !important; border-color: var(--border2) !important; color: var(--text) !important; border-radius: 6px !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: var(--text-dim) !important; font-size: 0.74rem !important; }

.stButton > button { background: transparent !important; border: 1px solid var(--border2) !important; color: var(--text-dim) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.7rem !important; border-radius: 6px !important; transition: all 0.18s !important; }
.stButton > button:hover { border-color: var(--amber-dim) !important; color: var(--amber) !important; background: var(--amber-glow) !important; }

.stat-chip { background: var(--bg3); border: 1px solid var(--border); border-radius: 4px; padding: 4px 9px; font-size: 0.64rem; color: var(--text-dim); font-family: 'IBM Plex Mono', monospace; display: inline-block; margin: 3px 3px 0 0; }
.stat-chip span { color: var(--amber); }
.speed-bar-bg { height: 3px; background: var(--border); border-radius: 2px; overflow: hidden; margin-top: 8px; }
.speed-bar-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, var(--amber), #ff6b00); transition: width 0.5s; }

/* Empty */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 20px; gap: 14px; text-align: center; }
.empty-glyph { font-family: 'IBM Plex Mono', monospace; font-size: 3rem; color: var(--border2); animation: float 4s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
.empty-title { font-size: 1.3rem; font-weight: 800; color: var(--border2); }
.empty-hint  { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: var(--text-dim); }
.em-chip { border: 1px solid var(--border); border-radius: 4px; padding: 3px 9px; font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: var(--text-dim); display: inline-block; margin: 3px; }
</style>
""", unsafe_allow_html=True)


# ─── Constants ────────────────────────────────────────────────────────────────

GROQ_MODELS = {
    "llama-3.3-70b-versatile": "Llama 3.3 · 70B Versatile",
    "llama-3.1-8b-instant":    "Llama 3.1 · 8B Instant",
    "llama3-70b-8192":         "Llama 3 · 70B 8k",
    "llama3-8b-8192":          "Llama 3 · 8B 8k",
    "mixtral-8x7b-32768":      "Mixtral · 8x7B 32k",
    "gemma2-9b-it":            "Gemma 2 · 9B",
}

SYSTEM_PRESETS = {
    "Default":     "You are a fast, helpful AI assistant powered by Groq. Be concise, clear, and accurate.",
    "Code Expert": "You are a senior software engineer. Write clean, well-commented, production-ready code with explanations.",
    "Creative":    "You are a creative writer. Use vivid language, imaginative ideas, and narrative flair.",
    "Analyst":     "You are a data analyst. Be structured, reason carefully, and present findings clearly.",
    "Tutor":       "You are a patient, encouraging tutor. Break down concepts step by step with examples.",
    "Custom":      "",
}


# ─── Session state ────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "messages":      [],
        "model":         "llama-3.3-70b-versatile",
        "system_prompt": SYSTEM_PRESETS["Default"],
        "temperature":   0.7,
        "max_tokens":    1024,
        "stream":        True,
        "total_tokens":  0,
        "api_key":       os.environ.get("GROQ_API_KEY", ""),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def ts():
    return time.strftime("%H:%M:%S")

def render_msg(role: str, content: str, delay_idx: int = 0):
    av_label  = "GQ"  if role == "assistant" else "YOU"
    av_class  = "ai"  if role == "assistant" else "user"
    bub_class = "ai"  if role == "assistant" else "user"
    row_class = ""    if role == "assistant" else "user"
    model_tag = f" · {GROQ_MODELS.get(st.session_state.model,'')}" if role == "assistant" else ""
    st.markdown(f"""
    <div class="msg-row {row_class}" style="animation-delay:{delay_idx*0.04}s">
      <div class="av {av_class}">{av_label}</div>
      <div>
        <div class="bubble {bub_class}">{content}</div>
        <div class="bubble-meta">{ts()}{model_tag}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sb-header">
      <div style="font-size:0.6rem;letter-spacing:.14em;text-transform:uppercase;color:#4a5060;margin-bottom:2px;">GROQ · INTERFACE</div>
      <div style="font-size:1.05rem;font-weight:800;color:#f0a500;letter-spacing:.04em;">▸ GROQ CHAT</div>
    </div>
    """, unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="sb-label">API KEY</div>', unsafe_allow_html=True)
    api_input = st.text_input(
        "api_key_input", value=st.session_state.api_key,
        type="password", placeholder="gsk_...",
        label_visibility="collapsed"
    )
    if api_input:
        st.session_state.api_key = api_input

    st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

    # Model
    st.markdown('<div class="sb-label">MODEL</div>', unsafe_allow_html=True)
    selected_model = st.selectbox(
        "model_select",
        list(GROQ_MODELS.keys()),
        format_func=lambda k: GROQ_MODELS[k],
        index=list(GROQ_MODELS.keys()).index(st.session_state.model),
        label_visibility="collapsed"
    )
    st.session_state.model = selected_model

    st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

    # System Prompt
    st.markdown('<div class="sb-label">PERSONA</div>', unsafe_allow_html=True)
    preset_sel = st.selectbox("preset_sel", list(SYSTEM_PRESETS.keys()), label_visibility="collapsed")
    if preset_sel != "Custom":
        st.session_state.system_prompt = SYSTEM_PRESETS[preset_sel]

    sp_val = st.text_area(
        "sys_prompt", value=st.session_state.system_prompt,
        height=100, label_visibility="collapsed", placeholder="System instructions…"
    )
    st.session_state.system_prompt = sp_val

    st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

    # Params
    st.markdown('<div class="sb-label">PARAMETERS</div>', unsafe_allow_html=True)
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.05)
    st.session_state.max_tokens  = st.slider("Max Tokens", 128, 4096, st.session_state.max_tokens, 128)
    st.session_state.stream      = st.toggle("Stream response", value=st.session_state.stream)

    st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

    # Stats
    n_msgs   = len(st.session_state.messages)
    tok_used = st.session_state.total_tokens
    tok_pct  = min(100, int(tok_used / 32768 * 100))
    st.markdown(f"""
    <div class="sb-label">SESSION STATS</div>
    <div>
      <div class="stat-chip">msgs <span>{n_msgs}</span></div>
      <div class="stat-chip">~tokens <span>{tok_used:,}</span></div>
    </div>
    <div class="speed-bar-bg"><div class="speed-bar-fill" style="width:{tok_pct}%"></div></div>
    <div style="font-size:0.58rem;color:#2a3040;font-family:'IBM Plex Mono',monospace;margin-top:4px;">{tok_pct}% context used</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑 Clear"):
            st.session_state.messages = []
            st.session_state.total_tokens = 0
            st.rerun()
    with c2:
        if st.button("↺ Reset"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ─── MAIN ────────────────────────────────────────────────────────────────────

model_display = GROQ_MODELS.get(st.session_state.model, st.session_state.model)
st.markdown(f"""
<div class="gq-header">
  <div class="gq-logo">▸ GROQ</div>
  <div class="gq-header-title">
    <strong>GROQ CHAT</strong>
    Ultra-fast LLM inference
  </div>
  <div class="gq-online">
    <div class="online-dot"></div>
    LIVE &nbsp;·&nbsp; {model_display}
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-scroll-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    chips = "".join(f'<div class="em-chip">{v.split("·")[0].strip()}</div>' for v in GROQ_MODELS.values())
    st.markdown(f"""
    <div class="empty-state">
      <div class="empty-glyph">▸</div>
      <div class="empty-title">GROQ IS READY</div>
      <div class="empty-hint">Ultra-fast inference. Select a model and start chatting.</div>
      <div style="margin-top:10px">{chips}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        render_msg(msg["role"], msg["content"], i)

st.markdown('</div>', unsafe_allow_html=True)


# ─── Input ────────────────────────────────────────────────────────────────────

if user_input := st.chat_input("Ask anything…  ⚡ Groq-powered"):

    if not st.session_state.api_key:
        st.error("⚠ No API key. Set GROQ_API_KEY env variable or enter it in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    render_msg("user", user_input, len(st.session_state.messages))

    api_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    client   = Groq(api_key=st.session_state.api_key)

    typing_ph   = st.empty()
    response_ph = st.empty()

    typing_ph.markdown("""
    <div class="typing-wrap">
      <div class="av ai">GQ</div>
      <div class="typing-bubble">
        <div class="t-dot"></div><div class="t-dot"></div><div class="t-dot"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    full_text    = ""
    usage_tokens = 0
    t_start      = time.time()

    try:
        sys_msgs = [{"role": "system", "content": st.session_state.system_prompt}] + api_msgs

        if st.session_state.stream:
            stream = client.chat.completions.create(
                model=st.session_state.model,
                messages=sys_msgs,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_text += delta
                typing_ph.empty()
                elapsed = round(time.time() - t_start, 1)
                tok_est = len(full_text.split())
                tps     = round(tok_est / max(elapsed, 0.01))
                response_ph.markdown(f"""
                <div class="msg-row">
                  <div class="av ai">GQ</div>
                  <div>
                    <div class="bubble ai">{full_text}<span style="color:#f0a500;animation:blink-dot .8s infinite;">▋</span></div>
                    <div class="bubble-meta">generating… {tps} tok/s · {elapsed}s</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            elapsed = round(time.time() - t_start, 2)
            response_ph.markdown(f"""
            <div class="msg-row">
              <div class="av ai">GQ</div>
              <div>
                <div class="bubble ai">{full_text}</div>
                <div class="bubble-meta">{ts()} · {GROQ_MODELS.get(st.session_state.model,'')} · ⚡ {elapsed}s</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            usage_tokens = len(full_text.split())

        else:
            response = client.chat.completions.create(
                model=st.session_state.model,
                messages=sys_msgs,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
            )
            full_text    = response.choices[0].message.content
            usage_tokens = getattr(response.usage, "total_tokens", len(full_text.split()))
            elapsed      = round(time.time() - t_start, 2)
            typing_ph.empty()
            response_ph.markdown(f"""
            <div class="msg-row">
              <div class="av ai">GQ</div>
              <div>
                <div class="bubble ai">{full_text}</div>
                <div class="bubble-meta">{ts()} · {GROQ_MODELS.get(st.session_state.model,'')} · ⚡ {elapsed}s</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        typing_ph.empty()
        err = str(e)
        if "auth" in err.lower() or "401" in err:
            msg = "⚠ Invalid API key. Check your Groq API key in the sidebar."
        elif "model" in err.lower():
            msg = f"⚠ Model not found: {err}"
        elif "rate" in err.lower():
            msg = "⚠ Rate limit hit — wait a moment and try again."
        else:
            msg = f"⚠ Error: {err}"
        response_ph.markdown(f"""
        <div class="msg-row">
          <div class="av ai" style="border-color:#5a1a1a;color:#ff6b6b;">GQ</div>
          <div><div class="bubble ai" style="border-left-color:#5a1a1a;color:#ff9090;">{msg}</div></div>
        </div>
        """, unsafe_allow_html=True)
        full_text = msg

    st.session_state.messages.append({"role": "assistant", "content": full_text})
    st.session_state.total_tokens += usage_tokens
