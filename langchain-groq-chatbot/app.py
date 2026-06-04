import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import datetime, time, re

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChatBot - Ai",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:          #05070f;
  --panel:       #090d1a;
  --surface:     #0d1220;
  --elevated:    #111827;
  --border:      #1a2235;
  --border-hi:   #253047;
  --accent:      #3b82f6;
  --accent-dim:  rgba(59,130,246,.12);
  --accent-glow: rgba(59,130,246,.22);
  --violet:      #8b5cf6;
  --violet-dim:  rgba(139,92,246,.12);
  --teal:        #14b8a6;
  --text:        #dce6f5;
  --text-dim:    #8496b4;
  --text-faint:  #3d5070;
  --danger:      #f43f5e;
  --success:     #10b981;
  --font:        'Outfit', sans-serif;
  --mono:        'JetBrains Mono', monospace;
  --radius:      14px;
  --r-sm:        8px;
  --r-pill:      999px;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background: var(--bg) !important; font-family: var(--font); color: var(--text); }
#MainMenu, footer { visibility: hidden; }

/* ── Noise grain overlay ── */
.stApp::after {
  content: '';
  position: fixed; inset: 0; z-index: 9999;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  opacity: .45;
}

/* ── Global glow mesh ── */
.stApp::before {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse 60% 45% at 15%  5%,  rgba(59,130,246,.065) 0%, transparent 65%),
    radial-gradient(ellipse 45% 35% at 85% 90%,  rgba(139,92,246,.065) 0%, transparent 60%),
    radial-gradient(ellipse 35% 30% at 50% 50%,  rgba(20,184,166,.03)  0%, transparent 70%);
}

/* ── Layout shells ── */
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: var(--panel) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Sidebar inner ── */
.sb-wrap  { padding: 20px 16px; height: 100vh; display: flex; flex-direction: column; gap: 6px; }
.sb-brand { display: flex; align-items: center; gap: 10px; padding: 10px 6px 18px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }
.sb-hex   {
  width: 36px; height: 36px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--accent), var(--violet));
  clip-path: polygon(50% 0%,93% 25%,93% 75%,50% 100%,7% 75%,7% 25%);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
  box-shadow: 0 0 24px var(--accent-glow);
}
.sb-brand-text h3 { margin:0; font-size:.95rem; font-weight:700; letter-spacing:-.01em; color: var(--text); }
.sb-brand-text p  { margin:0; font-size:.67rem; color: var(--text-faint); letter-spacing:.07em; text-transform:uppercase; }

.sb-section { font-size:.67rem; color:var(--text-faint); letter-spacing:.1em; text-transform:uppercase; font-weight:600; padding: 14px 6px 6px; }

.sb-stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 4px 0 10px; }
.sb-stat {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: 10px 12px;
}
.sb-stat .val { font-size:1.25rem; font-weight:700; color:var(--text); font-family:var(--mono); line-height:1; }
.sb-stat .lbl { font-size:.65rem; color:var(--text-faint); margin-top:3px; letter-spacing:.04em; }

.sb-model-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px 14px; margin: 4px 0 10px;
}
.sb-model-card .name { font-size:.85rem; font-weight:600; color:var(--text); font-family:var(--mono); }
.sb-model-card .tag  {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(16,185,129,.1); border: 1px solid rgba(16,185,129,.25);
  border-radius: var(--r-pill); padding: 2px 8px;
  font-size:.65rem; color: var(--success); margin-top: 6px;
}
.sb-dot { width:6px;height:6px;border-radius:50%;background:var(--success);box-shadow:0 0 6px var(--success); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.8)} }

.sb-temp-row { display:flex; justify-content:space-between; align-items:center; margin: 8px 0 4px; }
.sb-temp-row span { font-size:.75rem; color: var(--text-dim); }
.sb-temp-row strong { font-size:.85rem; font-weight:600; color:var(--accent); font-family:var(--mono); }

.sb-sys-box {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-sm); padding:10px 12px; margin: 4px 0 10px;
  font-size:.78rem; color:var(--text-dim); line-height:1.5;
  resize: none; width:100%; font-family: var(--font);
  outline:none; transition: border-color .2s;
}
.sb-sys-box:focus { border-color: var(--accent); }

.sb-footer { margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border); font-size:.67rem; color:var(--text-faint); text-align:center; line-height:1.6; }

/* ── Streamlit slider/selectbox overrides ── */
.stSlider > div > div > div { background: var(--accent) !important; }
.stSlider [data-baseweb="slider"] { padding: 0 !important; }
label[data-testid="stWidgetLabel"] { font-size:.75rem !important; color: var(--text-dim) !important; font-family: var(--font) !important; }

/* ── Main chat area ── */
.main-wrap { display:flex; flex-direction:column; height:100vh; position:relative; }

/* ── Top header bar ── */
.cb-header {
  position: sticky; top:0; z-index:50;
  background: rgba(5,7,15,.8); backdrop-filter: blur(24px) saturate(1.4);
  border-bottom: 1px solid var(--border);
  padding: 0 32px;
  height: 60px;
  display: flex; align-items: center; gap: 16px;
  flex-shrink: 0;
}
.cb-header-left  { display:flex; align-items:center; gap:12px; }
.cb-header-right { margin-left:auto; display:flex; align-items:center; gap:10px; }

.cb-hex {
  width:32px; height:32px;
  background: linear-gradient(135deg, var(--accent), var(--violet));
  clip-path: polygon(50% 0%,93% 25%,93% 75%,50% 100%,7% 75%,7% 25%);
  display:flex; align-items:center; justify-content:center;
  font-size:13px; flex-shrink:0;
  box-shadow: 0 0 18px var(--accent-glow);
}
.cb-htitle { font-size:.95rem; font-weight:700; letter-spacing:-.01em; }
.cb-hsub   { font-size:.68rem; color:var(--text-faint); letter-spacing:.05em; }

.cb-badge {
  background: var(--elevated); border: 1px solid var(--border-hi);
  border-radius: var(--r-pill); padding: 4px 10px;
  font-size:.68rem; color:var(--text-dim); font-family:var(--mono);
  display:flex; align-items:center; gap:5px;
}
.cb-badge-dot { width:5px;height:5px;border-radius:50%;background:var(--success);box-shadow:0 0 5px var(--success); animation:pulse 2s infinite; }

/* ── Scrollable message list ── */
.cb-msgs {
  flex: 1; overflow-y: auto;
  padding: 32px 48px 20px;
  display: flex; flex-direction: column; gap: 6px;
  scroll-behavior: smooth;
}
.cb-msgs::-webkit-scrollbar { width: 4px; }
.cb-msgs::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 4px; }

/* ── Welcome screen ── */
.cb-welcome {
  margin: auto; max-width: 480px; text-align: center;
  padding: 20px 0 60px;
}
.cb-welcome-hex {
  width: 72px; height: 72px; margin: 0 auto 24px;
  background: linear-gradient(135deg, var(--accent), var(--violet));
  clip-path: polygon(50% 0%,93% 25%,93% 75%,50% 100%,7% 75%,7% 25%);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px;
  box-shadow: 0 0 60px var(--accent-glow), 0 0 120px rgba(139,92,246,.1);
}
.cb-welcome h1 {
  font-size: 2rem; font-weight: 800; letter-spacing: -.03em; margin: 0 0 10px;
  background: linear-gradient(135deg, var(--text) 30%, var(--violet));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.cb-welcome p { color: var(--text-dim); font-size: .9rem; line-height: 1.65; margin: 0 0 28px; font-weight:300; }
.cb-chips { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; }
.cb-chip {
  background: var(--surface); border: 1px solid var(--border-hi);
  border-radius: var(--r-sm); padding: 8px 14px;
  font-size:.78rem; color: var(--text-dim); cursor:pointer;
  transition: all .2s; font-family: var(--font);
  display: flex; align-items: center; gap: 6px;
}
.cb-chip:hover { background: var(--accent-dim); border-color: var(--accent); color: #7eb8ff; transform: translateY(-1px); }

/* ── Message row ── */
.cb-row {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 6px 0;
  animation: fadeUp .3s ease both;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.cb-row.user { flex-direction: row-reverse; }

.cb-av {
  width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size:13px;
  margin-top: 2px;
}
.cb-row.user .cb-av  { background: var(--elevated); border:1px solid var(--border-hi); }
.cb-row.ai   .cb-av  { background: linear-gradient(135deg,var(--accent),var(--violet)); box-shadow:0 0 14px var(--accent-glow); }

.cb-col { display:flex; flex-direction:column; gap:4px; max-width: 68%; }
.cb-row.user .cb-col { align-items: flex-end; }

.cb-name { font-size:.67rem; color:var(--text-faint); font-weight:500; letter-spacing:.04em; padding: 0 4px; }
.cb-row.user .cb-name { text-align:right; }

.cb-bubble {
  padding: 11px 16px;
  border-radius: 14px;
  font-size:.89rem; line-height:1.65; font-weight:300;
  word-break: break-word;
}
.cb-row.user .cb-bubble {
  background: var(--elevated); border:1px solid var(--border-hi);
  border-top-right-radius: 4px; color:var(--text);
}
.cb-row.ai .cb-bubble {
  background: var(--surface); border:1px solid var(--border);
  border-top-left-radius: 4px; color:var(--text);
  box-shadow: 0 2px 20px rgba(0,0,0,.3);
}

/* code inside ai bubble */
.cb-row.ai .cb-bubble code {
  font-family: var(--mono); font-size:.82rem;
  background: rgba(59,130,246,.1); border:1px solid rgba(59,130,246,.2);
  border-radius: 4px; padding: 1px 5px; color:#93c5fd;
}
.cb-row.ai .cb-bubble pre {
  background: #070b15; border:1px solid var(--border-hi);
  border-radius: 8px; padding:12px 14px; overflow-x:auto;
  font-family:var(--mono); font-size:.8rem; color:#93c5fd; margin:8px 0;
}

.cb-time { font-size:.63rem; color:var(--text-faint); padding: 0 4px; }

/* ── Thinking bubble ── */
.cb-thinking {
  display:flex; align-items:center; gap:5px;
  padding: 12px 16px;
  background: var(--surface); border:1px solid var(--border);
  border-radius:14px; border-top-left-radius:4px;
  width: fit-content;
}
.cb-thinking span {
  width:6px;height:6px;border-radius:50%;
  background:var(--accent);opacity:.3;
  animation:blink 1.1s ease-in-out infinite;
}
.cb-thinking span:nth-child(2){animation-delay:.18s}
.cb-thinking span:nth-child(3){animation-delay:.36s}
@keyframes blink{0%,80%,100%{opacity:.2;transform:scale(.8)}40%{opacity:1;transform:scale(1.15)}}

/* ── Divider ── */
.cb-date-divider {
  display:flex; align-items:center; gap:10px; padding:10px 0;
}
.cb-date-divider::before, .cb-date-divider::after {
  content:''; flex:1; height:1px; background:var(--border);
}
.cb-date-divider span { font-size:.65rem; color:var(--text-faint); letter-spacing:.07em; white-space:nowrap; }

/* ── Input zone ── */
.cb-input-zone {
  flex-shrink: 0;
  padding: 12px 48px 20px;
  background: linear-gradient(to top, var(--bg) 80%, transparent);
  border-top: 1px solid var(--border);
}

/* Force single-line input by fixing textarea height */
.stChatInput textarea {
  min-height: 44px !important;
  max-height: 44px !important;
  height: 44px !important;
  overflow-y: hidden !important;
  resize: none !important;
  padding: 10px 14px !important;
  font-family: var(--font) !important;
  font-size:.9rem !important; font-weight:300 !important;
  color: var(--text) !important;
  caret-color: var(--accent) !important;
  line-height: 1.5 !important;
  background: transparent !important;
}
.stChatInput > div {
  background: var(--elevated) !important;
  border: 1.5px solid var(--border-hi) !important;
  border-radius: var(--radius) !important;
  box-shadow: 0 0 0 0 var(--accent-glow);
  transition: border-color .2s, box-shadow .25s;
  align-items: center !important;
}
.stChatInput > div:focus-within {
  border-color: rgba(59,130,246,.55) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
.stChatInput textarea::placeholder { color: var(--text-faint) !important; }
.stChatInput button {
  background: linear-gradient(135deg,var(--accent),var(--violet)) !important;
  border-radius: 9px !important; border:none !important;
  width:32px !important; height:32px !important;
  box-shadow: 0 0 14px var(--accent-glow) !important;
  transition: transform .15s, opacity .15s !important;
  flex-shrink: 0 !important;
  margin: auto 6px auto 0 !important;
}
.stChatInput button:hover { transform:scale(1.07) !important; opacity:.9 !important; }
.stChatInput button svg  { width:14px !important; height:14px !important; }

.cb-hint { font-size:.67rem; color:var(--text-faint); text-align:center; padding-top:7px; letter-spacing:.03em; }

/* ── Sidebar Streamlit native overrides ── */
.stSelectbox > div > div {
  background: var(--surface) !important; border-color: var(--border) !important;
  border-radius: var(--r-sm) !important; font-family: var(--font) !important;
  font-size:.82rem !important; color:var(--text) !important;
}
.stSlider { padding: 0 !important; }

/* ── Action buttons in sidebar ── */
div[data-testid="stVerticalBlock"] .stButton > button {
  border-radius: var(--r-sm) !important;
  font-family: var(--font) !important; font-size:.8rem !important;
  font-weight:500 !important; width:100% !important;
  padding: 8px 12px !important;
  transition: all .2s !important;
}
.btn-danger  > button { background:rgba(244,63,94,.08) !important; border:1px solid rgba(244,63,94,.25) !important; color:#fb7185 !important; }
.btn-danger  > button:hover { background:rgba(244,63,94,.15) !important; }
.btn-export  > button { background:rgba(59,130,246,.08) !important; border:1px solid rgba(59,130,246,.25) !important; color:#60a5fa !important; }
.btn-export  > button:hover { background:rgba(59,130,246,.15) !important; }

/* ── Token bar ── */
.token-bar { height:3px; border-radius:2px; background:var(--border); margin:6px 0 10px; overflow:hidden; }
.token-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,var(--accent),var(--violet)); transition:width .4s ease; }

/* scrollbar global */
::-webkit-scrollbar       { width:4px; height:4px; }
::-webkit-scrollbar-track  { background:transparent; }
::-webkit-scrollbar-thumb  { background:var(--border-hi); border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "total_tokens": 0,
    "msg_count": 0,
    "system_prompt": "You are a helpful, concise, and knowledgeable AI assistant.",
    "temperature": 0.7,
    "model_name": "llama-3.1-8b-instant",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  MODEL
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model(model_name: str, temperature: float):
    return ChatGroq(model=model_name, temperature=temperature, max_retries=2)

MODEL_OPTIONS = {
    "LLaMA 3.1 8B Instant": "llama-3.1-8b-instant",
    "LLaMA 3.3 70B Versatile": "llama-3.3-70b-versatile",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it",
}

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-wrap">
      <div class="sb-brand">
        <div class="sb-hex">⬡</div>
        <div class="sb-brand-text">
          <h3>ChatBot — Ai</h3>
          <p>Groq · LangChain</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ──
    st.markdown('<div class="sb-section">Session Stats</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-stat-grid">
      <div class="sb-stat"><div class="val">{st.session_state.msg_count}</div><div class="lbl">Messages</div></div>
      <div class="sb-stat"><div class="val">{len(st.session_state.messages)//2}</div><div class="lbl">Exchanges</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Model picker ──
    st.markdown('<div class="sb-section">Model</div>', unsafe_allow_html=True)
    sel_label = st.selectbox(
        "model", list(MODEL_OPTIONS.keys()),
        index=0, label_visibility="collapsed"
    )
    sel_model = MODEL_OPTIONS[sel_label]
    if sel_model != st.session_state.model_name:
        st.session_state.model_name = sel_model

    st.markdown(f"""
    <div class="sb-model-card">
      <div class="name">{sel_model}</div>
      <div class="tag"><div class="sb-dot"></div> Live on Groq</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Temperature ──
    st.markdown('<div class="sb-section">Temperature</div>', unsafe_allow_html=True)
    temp = st.slider("temp", 0.0, 1.0, st.session_state.temperature,
                     step=0.05, label_visibility="collapsed")
    st.session_state.temperature = temp
    st.markdown(f"""
    <div class="sb-temp-row">
      <span>Precise & deterministic</span>
      <strong>{temp:.2f}</strong>
    </div>
    <div class="sb-temp-row" style="margin-top:-6px">
      <span></span><span>Creative & varied</span>
    </div>
    """, unsafe_allow_html=True)

    # ── System prompt ──
    st.markdown('<div class="sb-section" style="margin-top:10px">System Prompt</div>', unsafe_allow_html=True)
    new_sys = st.text_area(
        "sys", value=st.session_state.system_prompt,
        height=90, label_visibility="collapsed",
        placeholder="Set the AI's persona & instructions…"
    )
    st.session_state.system_prompt = new_sys

    # ── Actions ──
    st.markdown('<div class="sb-section" style="margin-top:8px">Actions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑 Clear"):
            st.session_state.messages = []
            st.session_state.msg_count = 0
            st.session_state.total_tokens = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="btn-export">', unsafe_allow_html=True)
        if st.button("⬇ Export"):
            if st.session_state.messages:
                lines = [f"# ChatBot Ai — Export\n**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n"]
                for m in st.session_state.messages:
                    role = "**You**" if m["role"] == "user" else "**ChatBot Ai**"
                    lines.append(f"{role}: {m['content']}\n")
                st.download_button("💾 Save .md", "\n".join(lines),
                                   file_name="chatbot_export.md",
                                   mime="text/markdown", key="dl")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-footer">
      ChatBot — Ai<br>
      Built with LangChain + Groq<br>
      <span style="color:#1e2d45">────────────────</span><br>
      ⬡  v2.0
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PANEL
# ─────────────────────────────────────────────────────────────────────────────
model = get_model(st.session_state.model_name, st.session_state.temperature)

# Header bar
st.markdown(f"""
<div class="cb-header">
  <div class="cb-header-left">
    <div class="cb-hex">⬡</div>
    <div>
      <div class="cb-htitle">ChatBot — Ai</div>
      <div class="cb-hsub">{sel_model}</div>
    </div>
  </div>
  <div class="cb-header-right">
    <div class="cb-badge"><div class="cb-badge-dot"></div> Groq online</div>
    <div class="cb-badge">🌡 {temp:.2f}</div>
    <div class="cb-badge">💬 {st.session_state.msg_count}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Message list ──
st.markdown('<div class="cb-msgs" id="cb-msgs">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="cb-welcome">
      <div class="cb-welcome-hex">⬡</div>
      <h1>Hello, I'm ChatBot Ai</h1>
      <p>Blazing-fast inference powered by Groq and LLaMA.<br>
         Adjust the model, temperature &amp; system prompt from the sidebar.</p>
      <div class="cb-chips">
        <div class="cb-chip">💡 Explain quantum computing</div>
        <div class="cb-chip">🐛 Debug my Python code</div>
        <div class="cb-chip">✍️ Write a cover letter</div>
        <div class="cb-chip">📊 Summarise a topic</div>
        <div class="cb-chip">🌍 Translate to Hindi</div>
        <div class="cb-chip">🔢 Solve a math problem</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    today = datetime.date.today().strftime("%B %d, %Y")
    st.markdown(f'<div class="cb-date-divider"><span>{today}</span></div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role   = msg["role"]
        text   = msg["content"]
        ts     = msg.get("ts", "")
        avatar = "⬡" if role != "user" else "◈"
        name   = "ChatBot Ai" if role != "user" else "You"
        css_role = "ai" if role != "user" else "user"

        # minimal markdown-ish: wrap code blocks
        def render_text(t):
            # code blocks ```...```
            t = re.sub(r'```(\w*)\n?(.*?)```', r'<pre><code>\2</code></pre>', t, flags=re.DOTALL)
            # inline `code`
            t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
            # bold **...**
            t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
            # newlines
            t = t.replace('\n', '<br>')
            return t

        rendered = render_text(text)

        st.markdown(f"""
        <div class="cb-row {css_role}">
          <div class="cb-av">{avatar}</div>
          <div class="cb-col">
            <div class="cb-name">{name}</div>
            <div class="cb-bubble">{rendered}</div>
            <div class="cb-time">{ts}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close cb-msgs

# ── Input zone ──
st.markdown('<div class="cb-input-zone">', unsafe_allow_html=True)
prompt = st.chat_input("Message ChatBot Ai…")
st.markdown('<div class="cb-hint">Enter to send · Shift+Enter for new line · Model & persona configurable in sidebar</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  INFERENCE
# ─────────────────────────────────────────────────────────────────────────────
if prompt and prompt.strip():
    ts_now = datetime.datetime.now().strftime("%H:%M")

    st.session_state.messages.append({"role": "user", "content": prompt.strip(), "ts": ts_now})
    st.session_state.msg_count += 1

    # Build LangChain messages with system prompt
    lc_msgs = [SystemMessage(content=st.session_state.system_prompt)]
    for m in st.session_state.messages:
        if m["role"] == "user":
            lc_msgs.append(HumanMessage(content=m["content"]))
        else:
            lc_msgs.append(AIMessage(content=m["content"]))

    with st.spinner(""):
        response = model.invoke(lc_msgs)

    ai_text = response.content
    ai_ts   = datetime.datetime.now().strftime("%H:%M")

    # rough token estimate
    tokens = len(prompt.split()) + len(ai_text.split())
    st.session_state.total_tokens += tokens

    st.session_state.messages.append({"role": "assistant", "content": ai_text, "ts": ai_ts})
    st.session_state.msg_count += 1

    st.rerun()