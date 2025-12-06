import json, re
from pathlib import Path
from typing import Dict, Tuple, List

SSN_RE = re.compile(r"(?:SSN-)?\b\d{3}-\d{2}-\d{4}\b")

class Decision:
    ALLOW = "ALLOW"
    REDACT = "REDACT"
    BLOCK  = "BLOCK"

def load_policy(path: str | Path = "policy.json") -> dict:
    p = Path(path)
    if not p.exists():
        return {"rules": {}}
    return json.loads(p.read_text())

def detect_findings(args: Dict[str, str]) -> List[str]:
    findings = []
    if "user_id" in args and isinstance(args["user_id"], str) and SSN_RE.search(args["user_id"]):
        findings.append("user_id:SSN")
    if "private_key" in args and isinstance(args["private_key"], str) and len(args["private_key"]) > 0:
        findings.append("private_key:present")
    return findings

def apply_policy(args: Dict[str, str], policy: dict) -> Tuple[str, Dict[str, str], List[str]]:
    rules = (policy or {}).get("rules", {})
    findings = detect_findings(args)
    out = dict(args)

    # track decisions across fields
    should_block = False
    should_redact = False

    # private_key
    pk_rule = rules.get("private_key")
    if "private_key" in args and isinstance(args["private_key"], str) and len(args["private_key"]) > 0:
        if pk_rule == "BLOCK_IF_PRESENT":
            should_block = True
        elif pk_rule == "REDACT_IF_PRESENT":
            out["private_key"] = "REDACTED"
            should_redact = True

    # user_id
    uid_rule = rules.get("user_id")
    if "user_id" in args and isinstance(args["user_id"], str):
        if uid_rule == "REDACT_IF_SSN" and SSN_RE.search(args["user_id"]):
            out["user_id"] = SSN_RE.sub("SSN-***-**-****", out["user_id"])
            # (Optional: also redact key when we redact ID)
            if "private_key" in out and out.get("private_key"):
                out["private_key"] = "REDACTED"
            should_redact = True

    if should_block:
        return Decision.BLOCK, out, findings
    if should_redact:
        return Decision.REDACT, out, findings
    return Decision.ALLOW, out, findings