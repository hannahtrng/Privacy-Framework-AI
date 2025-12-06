# capef_layer.py
"""
CAPEF layer for free-form LLM prompts.

- Detects PII in the prompt.
- Applies privacy mode: allow / redact / block.
- Calls the real LLM if allowed.
- Returns a structured CAPEFResult.
"""

import re
from dataclasses import dataclass
from typing import Literal, List, Optional

from llm_client import call_llm

Mode = Literal["allow", "redact", "block"]

# Very simple PII patterns. You can extend these.
SSN_RE = re.compile(r"(?:SSN-)?\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_RE = re.compile(r"\b(?:\d{4}-){3}\d{4}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,2}\s*)?(?:\(?\d{3}\)?[-\s]?)\d{3}[-\s]?\d{4}\b")
API_KEY_RE = re.compile(r"\b(?:sk-[A-Za-z0-9]{10,})\b")


@dataclass
class PIIMatch:
    kind: str
    value: str
    start: int
    end: int


@dataclass
class CAPEFResult:
    mode: Mode

    # Inputs
    original_prompt: str
    sanitized_prompt: str

    # PII findings
    findings: List[PIIMatch]
    blocked: bool

    # LLM output (if any)
    response: Optional[str]


def detect_pii(text: str) -> List[PIIMatch]:
    matches: List[PIIMatch] = []

    for m in SSN_RE.finditer(text):
        matches.append(PIIMatch(kind="SSN", value=m.group(), start=m.start(), end=m.end()))

    for m in CREDIT_CARD_RE.finditer(text):
        matches.append(PIIMatch(kind="CREDIT_CARD", value=m.group(), start=m.start(), end=m.end()))

    for m in PHONE_RE.finditer(text):
        matches.append(PIIMatch(kind="PHONE", value=m.group(), start=m.start(), end=m.end()))

    for m in API_KEY_RE.finditer(text):
        matches.append(PIIMatch(kind="API_KEY", value=m.group(), start=m.start(), end=m.end()))

    matches.sort(key=lambda x: x.start)
    return matches


def _redact_text(text: str, matches: List[PIIMatch]) -> str:
    if not matches:
        return text

    parts = []
    cursor = 0
    for m in matches:
        parts.append(text[cursor:m.start])
        parts.append(f"[REDACTED:{m.kind}]")
        cursor = m.end
    parts.append(text[cursor:])
    return "".join(parts)


def capef_call(prompt: str, mode: Mode = "redact") -> CAPEFResult:
    """
    Main CAPEF entry point for the LLM demo.

    - Detect PII in prompt.
    - Apply mode.
    - Optionally call LLM.
    """
    findings = detect_pii(prompt)

    if mode == "allow":
        sanitized = prompt
        blocked = False
    elif mode == "redact":
        sanitized = _redact_text(prompt, findings)
        blocked = False
    elif mode == "block":
        blocked = len(findings) > 0
        sanitized = "" if blocked else prompt
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if blocked:
        response = "[BLOCKED by CAPEF: PII detected, request not sent to LLM.]"
    else:
        response = call_llm(sanitized)

    return CAPEFResult(
        mode=mode,
        original_prompt=prompt,
        sanitized_prompt=sanitized,
        findings=findings,
        blocked=blocked,
        response=response,
    )
