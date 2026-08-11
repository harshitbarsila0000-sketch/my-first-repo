# Operation Silent Web — Research Prototype

A Streamlit prototype accompanying the paper *"Operation Silent Web: Semantic
Espionage & Asynchronous Covert Channels."* It simulates an asynchronous
AI-to-AI covert-channel transport model (Field Agent → Open Network → HQ
Decoder) and a proposed defense, the Semantic Integrity Firewall (SIF).

## Scope & Responsible Disclosure

- **No real steganographic encoding is implemented.** Module 1 links a
  payload to generated text via a SHA-256 session fingerprint stored in
  `st.session_state` ("Cryptographic Session Linking"), not by embedding bits
  in token choices. This is a metadata-linking simulation of the *concept*,
  not a working covert-channel encoder. See paper §5.5 for the distinction
  from production-grade arithmetic coding.
- **SIF's scoring is heuristic, not a trained classifier.** `sif_engine.py`
  computes a Semantic Risk Score from five lexical/structural proxy signals
  (coordinate-pattern detection, sentence-length rigidity, a covert-phrase
  keyword list, topic-drift vs. expected genre vocabulary, and punctuation
  density). This replaces the earlier "always paraphrase" behavior so SIF
  only sanitizes text that crosses a threshold — closing the gap between the
  Ch. 6.2 architecture description and the actual prototype behavior. It is
  not equivalent to a production semantic-analysis pipeline.
- **No exploit code, malware, or working exfiltration mechanism is present.**
  The app only calls the Groq chat completions endpoint to generate and
  paraphrase benign review-style text.
- **Key distribution / bootstrapping is out of scope.** The prototype
  assumes the encoding scheme is pre-agreed at compromise time (see paper
  §3.3); this project addresses asynchronous transport and detection, not
  key distribution.
- Do not enter real classified, personal, or sensitive information into any
  field — this is a public-facing demo app.

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Get a free API key from [console.groq.com](https://console.groq.com).
3. Copy the secrets template and add your key:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # edit .streamlit/secrets.toml and paste your key
   ```
   `secrets.toml` is git-ignored — never commit real keys.
4. Run locally:
   ```bash
   streamlit run app.py
   ```

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (secrets.toml stays out of the repo via
   `.gitignore`).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app
   pointing at `app.py`.
3. In the app's **Settings → Secrets**, paste:
   ```toml
   GROQ_API_KEY = "your-key-here"
   ```
4. Deploy.

## How it maps to the paper

| Paper section | File |
|---|---|
| §5.1 Module 1: Encoder / Session Linking | `app.py` — Field Agent tab |
| §5.2 Module 2: Public Network Simulation | `app.py` — Open Network tab |
| §5.3 Module 3: Decoder | `app.py` — HQ Decoder tab |
| §6.2–6.5 SIF architecture / SRS | `sif_engine.py` |

## Known limitations (see paper §8.2)

- Small-scale manual evaluation only; no formal detection/false-positive
  statistics are computed by the app itself.
- SRS weights (`WEIGHTS` in `sif_engine.py`) are illustrative, not learned
  from labeled data — treat them as a starting point for tuning.
- Module 3 is manual copy-paste rather than an automated scraping agent.
