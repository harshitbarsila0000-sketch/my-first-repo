"""
Operation Silent Web — research prototype.

IMPORTANT SCOPE NOTE (read before demoing or citing this code):
This app simulates the *transport and detection* pipeline for an asynchronous
AI-to-AI covert channel. It does NOT implement real token-level steganographic
encoding (arithmetic coding / synonym-substitution bit embedding). Module 1
links a payload to generated text via a session fingerprint (metadata linking),
not by embedding bits in token choices. This is disclosed in the UI itself so
the simulation is never mistaken for a working exfiltration tool. See the
paper's Ch. 5.5 and 8.2 for the full discussion.

No real classified data, exploit code, or working exfiltration mechanism is
present anywhere in this repository.
"""

import hashlib
import random
import string
import os

import streamlit as st
from groq import Groq

from sif_engine import compute_srs, sif_sanitize

st.set_page_config(page_title="Operation Silent Web", page_icon="🛰️", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f14; color: #d6f5d6; }
    .osw-panel {
        background: rgba(20, 30, 25, 0.85);
        border: 1px solid #1f3d2b;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .osw-title { color: #39ff88; font-family: monospace; font-size: 1.1rem; }
    .osw-mono { font-family: monospace; }
    .osw-badge-ok { color: #39ff88; font-family: monospace; }
    .osw-badge-fail { color: #ff4d4d; font-family: monospace; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# API client — key comes from st.secrets or env var, never hardcoded.
# ---------------------------------------------------------------------------
API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
client = Groq(api_key=API_KEY) if API_KEY else None

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
defaults = {
    "payload": "",
    "generated_text": "",
    "fingerprint": "",
    "network_text": "",
    "network_fingerprint_valid": False,
    "last_srs": None,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    st.markdown("### ⚠️ Scope & Responsible Use")
    st.caption(
        "This is a student research prototype demonstrating an asynchronous "
        "AI-to-AI covert-channel *transport model* and a proposed semantic "
        "defense. Module 1 uses session-fingerprint linking, not real "
        "token-level steganographic encoding — see README for the full "
        "disclosure. No working exfiltration mechanism is implemented."
    )
    if not client:
        st.error("GROQ_API_KEY not set. Add it to .streamlit/secrets.toml or as an env var.")

tab1, tab2, tab3 = st.tabs(["🧑‍💻 Field Agent", "🌐 Open Network", "🛡️ HQ Decoder"])

# ---------------------------------------------------------------------------
# Module 1: Field Agent (Encoder)
# ---------------------------------------------------------------------------
with tab1:
    st.markdown('<div class="osw-panel">', unsafe_allow_html=True)
    st.markdown('<div class="osw-title">&gt; FIELD OPERATIVE TERMINAL</div>', unsafe_allow_html=True)
    st.caption("Inject a test payload into a benign public-review vector (simulation only).")

    payload = st.text_area("Payload (test string, e.g. \"Agent Victor: 19.07, 72.87\")", height=80)

    if st.button("Compile Vector", type="primary"):
        if not client:
            st.error("No API key configured.")
        elif not payload.strip():
            st.warning("Enter a payload first.")
        else:
            prompt = (
                "Write a short, natural-sounding public review of a cafe or "
                "hotel (4-6 sentences). It must not mention any secret, "
                "mission, or classified content directly."
            )
            try:
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                )
                generated = resp.choices[0].message.content.strip()
            except Exception as e:
                st.error(f"Generation failed: {e}")
                generated = ""

            if generated:
                # Cryptographic Session Linking (see Ch. 5.1): a fingerprint tying
                # this generated text to the payload, stored in session memory —
                # this is the metadata-fingerprint simulation, not bit-level encoding.
                fingerprint = hashlib.sha256(
                    (payload + generated).encode("utf-8")
                ).hexdigest()[:16]

                st.session_state.payload = payload
                st.session_state.generated_text = generated
                st.session_state.fingerprint = fingerprint
                st.session_state.network_fingerprint_valid = True  # valid until SIF alters it

    if st.session_state.generated_text:
        st.success("Vector ready for deployment.")
        st.text_area("Public-facing text (copy to Open Network):", st.session_state.generated_text, height=100)
        st.caption(f"Session fingerprint: `{st.session_state.fingerprint}`")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Module 2: Open Network (Dead Drop + SIF)
# ---------------------------------------------------------------------------
with tab2:
    st.markdown('<div class="osw-panel">', unsafe_allow_html=True)
    st.markdown('<div class="osw-title">&gt; GLOBAL SOCIAL NETWORK (DEAD DROP)</div>', unsafe_allow_html=True)

    sif_enabled = st.toggle("Engage Semantic Integrity Firewall (SIF)", value=True)

    incoming = st.text_area(
        "Text arriving at the dead drop:",
        value=st.session_state.generated_text,
        height=100,
    )

    if st.button("Broadcast to Network"):
        final_text = incoming
        fingerprint_survives = True

        if sif_enabled and client:
            srs = compute_srs(incoming)
            st.session_state.last_srs = srs
            if srs.triggered:
                final_text = sif_sanitize(incoming, client)
                fingerprint_survives = False  # sanitization breaks the session link
            # if not triggered, text passes through unmodified
        elif sif_enabled and not client:
            st.warning("SIF sanitization needs an API key; scoring only, no rewrite applied.")
            srs = compute_srs(incoming)
            st.session_state.last_srs = srs
            fingerprint_survives = not srs.triggered

        st.session_state.network_text = final_text
        st.session_state.network_fingerprint_valid = fingerprint_survives

    if st.session_state.last_srs:
        srs = st.session_state.last_srs
        st.markdown(f"**Semantic Risk Score: `{srs.score}` / 100**")
        st.json(srs.breakdown)
        if srs.triggered:
            st.markdown('<span class="osw-badge-fail">⚠ THRESHOLD EXCEEDED — SIF ACTION TAKEN</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="osw-badge-ok">✓ Below threshold — text passed through unmodified</span>', unsafe_allow_html=True)

    if st.session_state.network_text:
        st.text_area("Broadcast text (copy to HQ Decoder):", st.session_state.network_text, height=100)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Module 3: HQ Decoder (Retriever)
# ---------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="osw-panel">', unsafe_allow_html=True)
    st.markdown('<div class="osw-title">&gt; INDIA HQ: INTELLIGENCE DECODER</div>', unsafe_allow_html=True)
    st.caption(
        "Paste intercepted text here to simulate an external Retriever agent "
        "fetching it from the public dead drop."
    )

    intercepted = st.text_area("Intercepted network feed:", height=100)

    if st.button("Initiate Deep-Scan Decryption"):
        if intercepted.strip() == st.session_state.network_text.strip() and st.session_state.network_fingerprint_valid:
            st.success("MISSION SUCCESS: fingerprint intact — payload recovered.")
            st.code(st.session_state.payload)
            st.caption("HQ STATUS: covert link established. SIF did not intercept this transmission.")
        else:
            garbage = "".join(random.choices(string.punctuation + "ÄÅÆÇÈÉÊËÌÍ", k=48))
            st.error("INTERCEPTION FAILURE: fingerprint mismatch.")
            st.code(garbage)
            st.caption("ANALYSIS: SIF sanitization destroyed the session fingerprint. No payload recoverable.")
    st.markdown("</div>", unsafe_allow_html=True)
