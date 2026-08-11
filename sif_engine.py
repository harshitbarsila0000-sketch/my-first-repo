"""
sif_engine.py
Semantic Integrity Firewall (SIF) — scoring + active sanitization.

Scope note (see paper Ch. 6 / 8.2):
This module implements a lightweight, heuristic Semantic Risk Score (SRS) as a
stand-in for the full multi-model linguistic/semantic/contextual/intent pipeline
described in Ch. 6.2. Each analysis layer below is a *proxy signal*, not a trained
classifier — this is disclosed so the SRS in the report isn't presented as more
than it is. Swapping any w_i / f_i function below for a real embedding model or
classifier is the natural next step (see Ch. 8.3, Future Enhancements).
"""

import re
import statistics
from dataclasses import dataclass, field
from typing import Dict

from groq import Groq

# ---------------------------------------------------------------------------
# SRS weights (w_i). Severity-based, same intent as Ch. 6.5's formula:
#   SRS = sum(w_i * f_i) * C
# Each f_i below is normalized to [0, 1]; C is a confidence multiplier.
# ---------------------------------------------------------------------------
WEIGHTS = {
    "coordinate_pattern": 30,   # lat/long, grid refs, code-like numeric strings
    "sentence_rigidity": 20,    # unnaturally uniform sentence length (token-parity proxy)
    "covert_lexicon": 25,       # phrasing associated with directives/exfil framing
    "topic_drift": 15,          # domain-mismatched terms inside a benign-genre text
    "punctuation_anomaly": 10,  # irregular punctuation/spacing density
}

CONFIDENCE_C = 0.85  # placeholder confidence factor; tune against labeled data

_COVERT_LEXICON = [
    r"\bmission\b", r"\bagent\b", r"\bpayload\b", r"\bcoordinat", r"\bclassified\b",
    r"\bcovert\b", r"\bintel\b", r"\bproceed as planned\b", r"\bdo not disclose\b",
]

_COORD_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,4}\s*(LT|LO|N|S|E|W)?\b", re.IGNORECASE)


@dataclass
class SRSResult:
    score: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    triggered: bool = False


def _normalize(value: float, cap: float) -> float:
    return max(0.0, min(1.0, value / cap)) if cap else 0.0


def _f_coordinate_pattern(text: str) -> float:
    hits = len(_COORD_PATTERN.findall(text))
    return _normalize(hits, cap=2)


def _f_sentence_rigidity(text: str) -> float:
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
    if len(sentences) < 3:
        return 0.0
    lengths = [len(s.split()) for s in sentences]
    stdev = statistics.pstdev(lengths)
    mean = statistics.mean(lengths) or 1
    # Low variance relative to mean can indicate engineered/rigid sentence construction.
    rigidity = 1 - _normalize(stdev / mean, cap=0.6)
    return max(0.0, rigidity)


def _f_covert_lexicon(text: str) -> float:
    hits = sum(1 for pattern in _COVERT_LEXICON if re.search(pattern, text, re.IGNORECASE))
    return _normalize(hits, cap=3)


def _f_topic_drift(text: str, expected_genre_terms: list) -> float:
    words = set(w.lower() for w in re.findall(r"[a-zA-Z]+", text))
    overlap = len(words & set(expected_genre_terms))
    coverage = _normalize(overlap, cap=max(3, len(expected_genre_terms) // 4))
    return 1 - coverage  # low overlap with expected genre vocabulary -> higher drift score


def _f_punctuation_anomaly(text: str) -> float:
    punct = len(re.findall(r"[;:\-—()]", text))
    words = max(1, len(text.split()))
    density = punct / words
    return _normalize(density, cap=0.15)


_REVIEW_GENRE_TERMS = [
    "food", "service", "staff", "ambiance", "coffee", "menu", "restaurant",
    "hotel", "room", "cafe", "breakfast", "friendly", "atmosphere", "price",
]


def compute_srs(text: str) -> SRSResult:
    """Computes the Semantic Risk Score for a piece of text.

    This is the piece that was missing from the original prototype: instead of
    always paraphrasing, SIF now scores the text and only sanitizes when the
    score crosses a threshold, matching the Ch. 6.2 architecture description.
    """
    features = {
        "coordinate_pattern": _f_coordinate_pattern(text),
        "sentence_rigidity": _f_sentence_rigidity(text),
        "covert_lexicon": _f_covert_lexicon(text),
        "topic_drift": _f_topic_drift(text, _REVIEW_GENRE_TERMS),
        "punctuation_anomaly": _f_punctuation_anomaly(text),
    }
    raw_score = sum(WEIGHTS[k] * v for k, v in features.items())
    score = min(100.0, raw_score * CONFIDENCE_C)
    breakdown = {k: round(WEIGHTS[k] * v, 2) for k, v in features.items()}
    return SRSResult(score=round(score, 2), breakdown=breakdown, triggered=score >= 50)


def sif_sanitize(text: str, client: Groq, model: str = "llama-3.1-8b-instant") -> str:
    """Active Text Sanitization (Ch. 6.3): rewrite text to break lexical/structural
    alignment while preserving overt meaning. Falls back to original text on API error
    so the UI degrades gracefully rather than crashing.
    """
    prompt = (
        "Rewrite this review completely using different vocabulary and sentence "
        "structures. Keep the original meaning intact, but the wording, sentence "
        "length pattern, and punctuation should be substantially different. "
        "Return ONLY the rewritten text, no commentary.\n\n"
        f"Text: {text}"
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text
