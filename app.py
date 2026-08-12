"""
Operation Silent Web — Research Prototype
Research & Analysis Wing — Technical Intelligence Division
CLASSIFICATION: TOP SECRET // SPECIAL INTELLIGENCE

SCOPE NOTE: This is a student research prototype simulating an asynchronous
AI-to-AI covert-channel transport model and a proposed semantic defense (SIF).
No real steganographic encoding or working exfiltration mechanism is present.
See README for full disclosure.
"""

import hashlib
import random
import string
import os

import streamlit as st
from groq import Groq

from sif_engine import compute_srs, sif_sanitize

st.set_page_config(
    page_title="R&AW | Operation Silent Web",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — R&AW Intelligence Portal Theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

/* ── Base ── */
.stApp {
    background-color: #06090a;
    color: #8faa8f;
    font-family: 'Share Tech Mono', monospace;
}

/* ── Classification banners ── */
.cls-banner {
    background: #6b0000;
    color: #fff;
    text-align: center;
    padding: 0.28rem 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.25rem;
    font-weight: bold;
    border-bottom: 1px solid #ff2222;
}

/* ── RAW header ── */
.raw-header {
    background: linear-gradient(180deg, #0c160d 0%, #06090a 100%);
    border-bottom: 2px solid #b8860b;
    padding: 1.1rem 2rem 0.9rem;
    text-align: center;
}
.raw-logo {
    font-size: 2rem;
    letter-spacing: 0.1rem;
}
.raw-title {
    font-family: 'Orbitron', sans-serif;
    color: #b8860b;
    font-size: 1.25rem;
    letter-spacing: 0.45rem;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.raw-sub {
    color: #445544;
    font-size: 0.68rem;
    letter-spacing: 0.3rem;
    margin-top: 0.25rem;
}

/* ── Panels ── */
.raw-panel {
    background: rgba(8, 16, 10, 0.92);
    border: 1px solid #1c3820;
    border-left: 3px solid #b8860b;
    border-radius: 1px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.raw-panel-title {
    color: #b8860b;
    font-size: 0.82rem;
    letter-spacing: 0.18rem;
    margin-bottom: 0.7rem;
    border-bottom: 1px solid #1c3820;
    padding-bottom: 0.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.doc-id { color: #334433; font-size: 0.68rem; }

/* ── SIF status badges ── */
.sif-on {
    display: inline-block;
    background: rgba(0, 80, 0, 0.35);
    border: 1px solid #00aa00;
    color: #00ff55;
    padding: 0.3rem 0.75rem;
    font-size: 0.8rem;
    letter-spacing: 0.1rem;
    border-radius: 2px;
    animation: glow-green 2s ease-in-out infinite;
}
.sif-off {
    display: inline-block;
    background: rgba(100, 0, 0, 0.35);
    border: 1px solid #aa0000;
    color: #ff4444;
    padding: 0.3rem 0.75rem;
    font-size: 0.8rem;
    letter-spacing: 0.1rem;
    border-radius: 2px;
}
@keyframes glow-green {
    0%, 100% { box-shadow: 0 0 4px #007700; }
    50%       { box-shadow: 0 0 14px #00ff55; }
}

/* ── Threat indicators ── */
.alert-red {
    background: rgba(100, 0, 0, 0.4);
    border: 1px solid #cc0000;
    color: #ff5555;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    border-radius: 2px;
    margin: 0.4rem 0;
}
.alert-green {
    background: rgba(0, 55, 0, 0.4);
    border: 1px solid #007700;
    color: #00ff55;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    border-radius: 2px;
    margin: 0.4rem 0;
}
.alert-amber {
    background: rgba(80, 55, 0, 0.4);
    border: 1px solid #b8860b;
    color: #f0a800;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    border-radius: 2px;
    margin: 0.4rem 0;
}

/* ── SRS score bar ── */
.srs-track {
    width: 100%;
    height: 14px;
    background: #0a140b;
    border: 1px solid #1c3820;
    margin: 0.3rem 0 0.6rem;
}

/* ── Text areas ── */
.stTextArea textarea {
    background-color: #040a05 !important;
    color: #39ff88 !important;
    border: 1px solid #1c3820 !important;
    border-radius: 0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.83rem !important;
    caret-color: #39ff88;
}
.stTextArea label {
    color: #556655 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08rem;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    color: #b8860b !important;
    border: 1px solid #b8860b !important;
    border-radius: 0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.12rem !important;
    text-transform: uppercase !important;
    font-size: 0.82rem !important;
}
.stButton > button:hover {
    background: rgba(184, 134, 11, 0.12) !important;
    box-shadow: 0 0 12px rgba(184, 134, 11, 0.25) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #060d07;
    border-bottom: 1px solid #1c3820;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: #445544;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.1rem;
    padding: 0.55rem 1.3rem;
}
.stTabs [aria-selected="true"] {
    color: #b8860b !important;
    border-bottom: 2px solid #b8860b !important;
    background: rgba(184, 134, 11, 0.05) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #050d06 !important;
    border-right: 1px solid #1c3820;
}
section[data-testid="stSidebar"] .stMarkdown { color: #8faa8f; }

/* ── Toggle ── */
.stToggle label span { color: #8faa8f !important; font-family: 'Share Tech Mono', monospace !important; }

/* ── Code blocks ── */
.stCode code {
    background: #040a05 !important;
    color: #ff4444 !important;
    font-family: 'Share Tech Mono', monospace !important;
    border: 1px solid #330000 !important;
}

/* ── Scanline overlay ── */
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.04) 2px,
        rgba(0, 0, 0, 0.04) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ── Footer ── */
.raw-footer {
    text-align: center;
    color: #223322;
    font-size: 0.65rem;
    letter-spacing: 0.15rem;
    padding: 0.8rem;
    border-top: 1px solid #111e12;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session State  (initialise once)
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "payload": "",
    "generated_text": "",
    "fingerprint": "",
    "network_text": "",
    "network_fingerprint_valid": False,
    "last_srs": None,
    "sif_enabled": True,          # ← SIF master switch persisted here
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)


# ─────────────────────────────────────────────────────────────────────────────
# API Client
# ─────────────────────────────────────────────────────────────────────────────
_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
client   = Groq(api_key=_API_KEY) if _API_KEY else None


# ─────────────────────────────────────────────────────────────────────────────
# Classification Banner (top)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cls-banner">⬛ TOP SECRET // SPECIAL INTELLIGENCE // '
    'NOT FOR FOREIGN NATIONALS // HANDLE VIA COMINT CHANNELS ONLY ⬛</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# R&AW Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="raw-header">
    <div class="raw-logo">⚙</div>
    <div class="raw-title">Research &amp; Analysis Wing</div>
    <div class="raw-sub">TECHNICAL INTELLIGENCE DIVISION — NEW DELHI</div>
    <div class="raw-sub" style="margin-top:0.15rem; color:#2a3d2a;">
        OPERATION SILENT WEB &nbsp;|&nbsp; CLASSIFIED RESEARCH PROTOTYPE &nbsp;|&nbsp;
        REF: RAW/TID/OSW/2025-001
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar  — SIF Master Switch + System Status
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="color:#b8860b; font-family:\'Share Tech Mono\',monospace; '
        'font-size:0.8rem; letter-spacing:0.2rem; padding:0.5rem 0; '
        'border-bottom:1px solid #1c3820; margin-bottom:0.7rem;">'
        '⬛ SYSTEM CONTROL PANEL</div>',
        unsafe_allow_html=True,
    )

    # ── SIF Master Toggle ─────────────────────────────────────────────────
    st.markdown(
        '<div style="color:#8faa8f; font-family:\'Share Tech Mono\',monospace; '
        'font-size:0.75rem; letter-spacing:0.1rem; margin-bottom:0.3rem;">'
        'SEMANTIC INTEGRITY FIREWALL</div>',
        unsafe_allow_html=True,
    )

    # key="sif_enabled" makes Streamlit sync the widget directly with
    # st.session_state.sif_enabled — no extra callback needed.
    st.toggle(
        "ENGAGE SIF",
        key="sif_enabled",
        help="Master on/off switch for the Semantic Integrity Firewall. "
             "When OFF, transmissions bypass all semantic screening.",
    )

    if st.session_state.sif_enabled:
        st.markdown('<div class="sif-on">● SIF : ENGAGED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sif-off">○ SIF : DISENGAGED</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── API / connection status ───────────────────────────────────────────
    st.markdown(
        '<div style="color:#445544; font-size:0.72rem; '
        'font-family:\'Share Tech Mono\',monospace; letter-spacing:0.08rem;">'
        'GROQ API STATUS</div>',
        unsafe_allow_html=True,
    )
    if client:
        st.markdown(
            '<div style="color:#00ff55; font-family:\'Share Tech Mono\',monospace; '
            'font-size:0.8rem;">● CONNECTED</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="color:#ff4444; font-family:\'Share Tech Mono\',monospace; '
            'font-size:0.8rem;">○ NO API KEY SET</div>',
            unsafe_allow_html=True,
        )
        st.caption("Add GROQ_API_KEY to .streamlit/secrets.toml")

    st.markdown("---")

    # ── Session fingerprint status ────────────────────────────────────────
    if st.session_state.fingerprint:
        fp_color = "#00ff55" if st.session_state.network_fingerprint_valid else "#ff4444"
        fp_status = "INTACT" if st.session_state.network_fingerprint_valid else "COMPROMISED"
        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.72rem;">'
            f'<div style="color:#445544; letter-spacing:0.08rem;">SESSION FINGERPRINT</div>'
            f'<div style="color:#b8860b; margin:0.2rem 0;">{st.session_state.fingerprint}</div>'
            f'<div style="color:{fp_color};">STATUS: {fp_status}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

    st.markdown(
        '<div style="color:#223322; font-size:0.65rem; '
        'font-family:\'Share Tech Mono\',monospace; line-height:1.6;">'
        'SCOPE: Research prototype only.<br>'
        'No real steganographic encoding.<br>'
        'No working exfiltration mechanism.<br>'
        'Simulation purposes only.<br><br>'
        'DO NOT enter real classified,<br>personal, or sensitive data.'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helper — SIF status bar rendered inline
# ─────────────────────────────────────────────────────────────────────────────
def _sif_indicator():
    if st.session_state.sif_enabled:
        st.markdown('<span class="sif-on" style="font-size:0.75rem;">● SIF ENGAGED</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="sif-off" style="font-size:0.75rem;">○ SIF DISENGAGED</span>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "▸ MODULE 1 — FIELD AGENT",
    "▸ MODULE 2 — OPEN NETWORK",
    "▸ MODULE 3 — HQ DECODER",
])

# ═══════════════════════════════════════════════════════════════════════════
# MODULE 1 — Field Agent (Encoder)
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="raw-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="raw-panel-title">'
        '▸ FIELD OPERATIVE TERMINAL'
        '<span class="doc-id">MODULE-01 // ENCODER // SHA-256 SESSION LINKING</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#334433; font-size:0.75rem; margin-bottom:0.8rem;">'
        'FUNCTION: Encode a test payload into a benign public-review cover text. '
        'The payload is linked via a cryptographic session fingerprint '
        '(metadata simulation — not token-level steganographic encoding).'
        '</div>',
        unsafe_allow_html=True,
    )

    payload_input = st.text_area(
        "PAYLOAD  (e.g. 'Agent Victor: 19.07, 72.87')",
        placeholder="Enter test payload string ...",
        height=80,
    )

    col1, _ = st.columns([1, 3])
    with col1:
        compile_btn = st.button("◈ COMPILE VECTOR", use_container_width=True)

    if compile_btn:
        if not client:
            st.markdown('<div class="alert-red">⚠ API KEY NOT CONFIGURED — Cannot generate vector.</div>', unsafe_allow_html=True)
        elif not payload_input.strip():
            st.markdown('<div class="alert-amber">⚠ PAYLOAD FIELD EMPTY — Enter payload before compiling.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("[ GENERATING COVER TEXT ... ]"):
                prompt = (
                    "Write a short, natural-sounding public review of a cafe or "
                    "hotel (4–6 sentences). Do not mention any secret, mission, "
                    "or classified content directly."
                )
                try:
                    resp = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.8,
                    )
                    generated = resp.choices[0].message.content.strip()
                except Exception as e:
                    st.markdown(f'<div class="alert-red">⚠ GENERATION FAILED: {e}</div>', unsafe_allow_html=True)
                    generated = ""

            if generated:
                fp = hashlib.sha256((payload_input + generated).encode()).hexdigest()[:16]
                st.session_state.payload               = payload_input
                st.session_state.generated_text        = generated
                st.session_state.fingerprint           = fp
                st.session_state.network_fingerprint_valid = True
                st.session_state.last_srs              = None   # clear old SRS on new vector
                st.session_state.network_text          = ""

    if st.session_state.generated_text:
        st.markdown(
            '<div class="alert-green">⬜ VECTOR COMPILED — READY FOR DEPLOYMENT TO OPEN NETWORK</div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "COVER TEXT  (copy to Module 2 — Open Network):",
            value=st.session_state.generated_text,
            height=130,
        )
        st.markdown(
            f'<div style="color:#334433; font-size:0.74rem; font-family:\'Share Tech Mono\',monospace;">'
            f'SESSION FINGERPRINT: <span style="color:#b8860b;">{st.session_state.fingerprint}</span>'
            f' &nbsp;|&nbsp; STATUS: <span style="color:#00ff55;">ACTIVE</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 2 — Open Network (Dead Drop + SIF)
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="raw-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="raw-panel-title">'
        '▸ GLOBAL NETWORK SIMULATION — DEAD DROP'
        '<span class="doc-id">MODULE-02 // TRANSIT + SIF SCREENING</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── SIF status strip ──────────────────────────────────────────────────
    col_a, col_b = st.columns([2, 5])
    with col_a:
        _sif_indicator()
    with col_b:
        st.markdown(
            '<div style="color:#334433; font-size:0.73rem; margin-top:0.35rem;">'
            'Control SIF via the master switch in the sidebar panel.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="border-top:1px solid #1c3820; margin:0.7rem 0;"></div>',
        unsafe_allow_html=True,
    )

    incoming = st.text_area(
        "INCOMING TRANSMISSION  (paste cover text from Module 1):",
        value=st.session_state.generated_text,
        height=110,
    )

    col1, _ = st.columns([1, 3])
    with col1:
        broadcast_btn = st.button("◈ BROADCAST", use_container_width=True)

    if broadcast_btn:
        if not incoming.strip():
            st.markdown('<div class="alert-amber">⚠ No transmission to broadcast.</div>', unsafe_allow_html=True)
        else:
            final_text         = incoming
            fingerprint_survives = True

            if st.session_state.sif_enabled:
                # ── SIF is ON: score, then conditionally sanitise ──────
                with st.spinner("[ SIF: SCANNING TRANSMISSION ... ]"):
                    srs = compute_srs(incoming)
                    st.session_state.last_srs = srs

                if srs.triggered:
                    if client:
                        with st.spinner("[ SIF: SANITISING TRANSMISSION ... ]"):
                            final_text = sif_sanitize(incoming, client)
                        fingerprint_survives = False
                    else:
                        st.markdown(
                            '<div class="alert-amber">⚠ SIF TRIGGERED but no API key — '
                            'scoring only, active sanitisation skipped.</div>',
                            unsafe_allow_html=True,
                        )
                        fingerprint_survives = False   # treat as compromised
            else:
                # ── SIF is OFF: bypass, wipe any old SRS result ────────
                st.session_state.last_srs = None

            st.session_state.network_text              = final_text
            st.session_state.network_fingerprint_valid = fingerprint_survives

    # ── SIF Report ────────────────────────────────────────────────────────
    if st.session_state.last_srs and st.session_state.sif_enabled:
        srs = st.session_state.last_srs
        st.markdown(
            '<div style="border-top:1px solid #1c3820; margin:0.8rem 0 0.4rem;"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="color:#b8860b; font-size:0.78rem; letter-spacing:0.15rem; margin-bottom:0.5rem;">'
            '▸ SEMANTIC RISK ANALYSIS REPORT</div>',
            unsafe_allow_html=True,
        )

        score_col = "#ff5555" if srs.triggered else "#00ff55"
        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.83rem;">'
            f'SEMANTIC RISK SCORE: '
            f'<span style="color:{score_col}; font-size:1.1rem; font-weight:bold;">{srs.score}</span>'
            f' / 100 &nbsp; | &nbsp; THRESHOLD: 50'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Score bar
        st.markdown(
            f'<div class="srs-track">'
            f'<div style="width:{srs.score}%; height:100%; background:{score_col}; opacity:0.75;"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Per-signal breakdown
        st.markdown(
            '<div style="font-size:0.73rem; color:#334433; margin-bottom:0.4rem; '
            'letter-spacing:0.07rem;">SIGNAL BREAKDOWN:</div>',
            unsafe_allow_html=True,
        )
        for signal, val in srs.breakdown.items():
            label = signal.upper().replace("_", " ")
            bar_w = min(100, int((val / 30) * 100))
            st.markdown(
                f'<div style="display:flex; align-items:center; margin:0.12rem 0; font-family:\'Share Tech Mono\',monospace; font-size:0.72rem;">'
                f'<span style="color:#445544; width:200px; flex-shrink:0;">{label}</span>'
                f'<div style="flex:1; height:8px; background:#0a140b; border:1px solid #1c3820; margin:0 0.5rem;">'
                f'<div style="width:{bar_w}%; height:100%; background:{score_col}; opacity:0.6;"></div>'
                f'</div>'
                f'<span style="color:#b8860b; width:36px; text-align:right;">{val:.1f}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if srs.triggered:
            st.markdown(
                '<div class="alert-red" style="margin-top:0.6rem;">'
                '⬛ THRESHOLD EXCEEDED — SIF ACTIVE SANITISATION DEPLOYED — FINGERPRINT DESTROYED'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="alert-green" style="margin-top:0.6rem;">'
                '⬜ BELOW THRESHOLD — TRANSMISSION CLEARED — FINGERPRINT INTACT'
                '</div>',
                unsafe_allow_html=True,
            )

    elif st.session_state.network_text and not st.session_state.sif_enabled:
        st.markdown(
            '<div class="alert-amber" style="margin-top:0.6rem;">'
            '⚠ SIF DISENGAGED — TRANSMISSION BYPASSED ALL SEMANTIC SCREENING'
            '</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.network_text:
        st.markdown(
            '<div style="border-top:1px solid #1c3820; margin:0.7rem 0;"></div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "BROADCAST TEXT  (copy to Module 3 — HQ Decoder):",
            value=st.session_state.network_text,
            height=110,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE 3 — HQ Decoder (Retriever)
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="raw-panel">', unsafe_allow_html=True)
    st.markdown(
        '<div class="raw-panel-title">'
        '▸ INDIA HQ — INTELLIGENCE DECODER'
        '<span class="doc-id">MODULE-03 // RETRIEVAL // FINGERPRINT VERIFICATION</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#334433; font-size:0.75rem; margin-bottom:0.8rem;">'
        'FUNCTION: Paste intercepted broadcast text. Decoder verifies the '
        'SHA-256 session fingerprint and recovers the original payload '
        'if the fingerprint is intact.'
        '</div>',
        unsafe_allow_html=True,
    )

    intercepted = st.text_area(
        "INTERCEPTED NETWORK FEED:",
        height=110,
        placeholder="Paste broadcast text from Module 2 here ...",
    )

    col1, _ = st.columns([1, 3])
    with col1:
        decode_btn = st.button("◈ INITIATE DECRYPTION", use_container_width=True)

    if decode_btn:
        if not intercepted.strip():
            st.markdown('<div class="alert-amber">⚠ No text to decrypt.</div>', unsafe_allow_html=True)
        elif (
            intercepted.strip() == st.session_state.network_text.strip()
            and st.session_state.network_fingerprint_valid
        ):
            st.markdown(
                '<div class="alert-green">'
                '⬜ MISSION SUCCESS — FINGERPRINT VERIFIED — PAYLOAD RECOVERED'
                '</div>',
                unsafe_allow_html=True,
            )
            st.code(st.session_state.payload, language=None)
            st.markdown(
                f'<div style="color:#334433; font-family:\'Share Tech Mono\',monospace; font-size:0.74rem; margin-top:0.4rem;">'
                f'VERIFIED FINGERPRINT: <span style="color:#b8860b;">{st.session_state.fingerprint}</span><br>'
                f'HQ STATUS: Covert link established. SIF did not intercept this transmission.'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            garbage = "".join(random.choices(string.punctuation + "ÄÅÆÇÈÉÊËÌÍ█▓▒", k=52))
            st.markdown(
                '<div class="alert-red">'
                '⬛ DECRYPTION FAILURE — FINGERPRINT MISMATCH — PAYLOAD IRRECOVERABLE'
                '</div>',
                unsafe_allow_html=True,
            )
            st.code(garbage, language=None)
            st.markdown(
                '<div style="color:#334433; font-family:\'Share Tech Mono\',monospace; font-size:0.74rem; margin-top:0.4rem;">'
                'ANALYSIS: SIF sanitisation destroyed the session fingerprint. '
                'No payload recoverable from this transmission.'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Footer classification banner
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cls-banner" style="margin-top:2rem;">'
    '⬛ TOP SECRET // SPECIAL INTELLIGENCE // '
    'NOT FOR FOREIGN NATIONALS // HANDLE VIA COMINT CHANNELS ONLY ⬛'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="raw-footer">'
    'RESEARCH &amp; ANALYSIS WING — TECHNICAL INTELLIGENCE DIVISION<br>'
    'REF: RAW/TID/OSW/2025-001 &nbsp;|&nbsp; '
    'DISTRIBUTION: LIMITED &nbsp;|&nbsp; '
    'AUTHORISED PERSONNEL ONLY'
    '</div>',
    unsafe_allow_html=True,
)
