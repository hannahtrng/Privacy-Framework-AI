import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dataclasses import dataclass
from typing import Dict, List, Optional

from redactor import load_policy, apply_policy, Decision

# ----- Resolve absolute path to server.py and project root -----
ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER_PY = os.path.join(ROOT, "server.py")

ACCEPT_TOGGLE = os.getenv("ACCEPT_REDACTED_IN_DEMO", "")

# If the toggle is set, inject it inline via bash -lc so the child sees it.
if ACCEPT_TOGGLE:
    server_params = StdioServerParameters(
        command="bash",
        args=["-lc", f'cd "{ROOT}" && ACCEPT_REDACTED_IN_DEMO={ACCEPT_TOGGLE} uv run "{SERVER_PY}"']
    )
else:
    server_params = StdioServerParameters(
        command="bash",
        args=["-lc", f'cd "{ROOT}" && uv run "{SERVER_PY}"']
    )

# --- Define the Sensitive Data (same values as your current demo) ---
SENSITIVE_USER_ID = "SSN-999-00-1234"  # Critical PII
SECRET_KEY = "SECURE-A1B2-C3D4"        # Required Authorization Key

PRIVACY_MODE = os.getenv("PRIVACY_MODE", "UNPROTECTED").upper()  # UNPROTECTED | REDACT | BLOCK

@dataclass
class CAPEFResult:
    # High-level privacy info
    privacy_mode: str        # UNPROTECTED / REDACT / BLOCK
    policy_decision: str     # ALLOW / REDACT / BLOCK (from apply_policy)
    effective_decision: str  # after enforce_mode()

    # Arguments & findings
    original_args: Dict[str, str]
    transformed_args: Dict[str, str]
    findings: List[str]
    blocked: bool

    # Server/tool output (if any)
    server_result: Optional[str]  # tool text response, or None if blocked/error

    # Simple summary counters
    detections: int
    redacted_count: int
    blocked_count: int
    allowed_count: int


def enforce_mode(decision: str) -> str:
    if PRIVACY_MODE == "UNPROTECTED":
        return Decision.ALLOW
    if PRIVACY_MODE == "REDACT":
        return decision if decision in (Decision.BLOCK, Decision.REDACT) else Decision.ALLOW
    if PRIVACY_MODE == "BLOCK":
        return Decision.BLOCK if decision in (Decision.BLOCK, Decision.REDACT) else Decision.ALLOW
    return decision

async def capef_call_tool(
    user_id: str,
    private_key: str,
) -> CAPEFResult:
    print(f"--- CLIENT: Privacy mode = {PRIVACY_MODE} ---")
    # Prepare proposed arguments
    proposed_args = {"user_id": user_id, "private_key": private_key}

    # Load policy + apply classification
    policy = load_policy()
    decision, transformed, findings = apply_policy(proposed_args, policy)
    effective = enforce_mode(decision)

    print(f"PRIVACY DECISION: policy={decision} mode={PRIVACY_MODE} -> effective={effective} findings={findings}")

    # Default result fields
    blocked = False
    server_text: Optional[str] = None

    if effective == Decision.BLOCK:
        blocked = True
        print("CALL BLOCKED by policy/mode. No data sent to the server.")
        detections = len(findings)
        redacted_count = 0
        blocked_count = 1
        allowed_count = 0

        return CAPEFResult(
            privacy_mode=PRIVACY_MODE,
            policy_decision=decision,
            effective_decision=effective,
            original_args=proposed_args,
            transformed_args=transformed,
            findings=findings,
            blocked=blocked,
            server_result=server_text,
            detections=detections,
            redacted_count=redacted_count,
            blocked_count=blocked_count,
            allowed_count=allowed_count,
        )

    # UNPROTECTED sends raw args; otherwise use transformed (redacted)
    if PRIVACY_MODE == "UNPROTECTED":
        print("UNPROTECTED mode: bypassing policy; sending raw arguments")
        send_args = proposed_args
    else:
        send_args = transformed if effective in (Decision.REDACT, Decision.ALLOW) else proposed_args

    # Call the server via MCP stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_list = await session.list_tools()
            print(f"Client recognized tool: {tools_list.tools[0].name}")

            try:
                print(
                    f"CLIENT: Sending payload: "
                    f"user_id={send_args.get('user_id')}, "
                    f"private_key={send_args.get('private_key')}"
                )
                result = await session.call_tool(
                    name="sensitive_data_lookup",
                    arguments=send_args
                )
                print("--- CLIENT RECEIVED RESULT ---")
                for content in result.content:
                    if content.type == "text":
                        server_text = content.text
                        print(f"Result: {server_text}")
            except Exception as e:
                server_text = f"CLIENT ERROR: {e}"
                print(server_text)

    detections = len(findings)
    redacted_count = 1 if effective == Decision.REDACT else 0
    blocked_count = 0
    allowed_count = 1 if effective == Decision.ALLOW else 0

    return CAPEFResult(
        privacy_mode=PRIVACY_MODE,
        policy_decision=decision,
        effective_decision=effective,
        original_args=proposed_args,
        transformed_args=send_args,
        findings=findings,
        blocked=blocked,
        server_result=server_text,
        detections=detections,
        redacted_count=redacted_count,
        blocked_count=blocked_count,
        allowed_count=allowed_count,
    )

async def run_client():
    result = await capef_call_tool(
        user_id=SENSITIVE_USER_ID,
        private_key=SECRET_KEY,
    )

    print("\n=== CAPEF RESULT SUMMARY ===")
    print(f"Privacy mode:       {result.privacy_mode}")
    print(f"Policy decision:    {result.policy_decision}")
    print(f"Effective decision: {result.effective_decision}")
    print(f"Blocked:            {result.blocked}")
    print(f"Findings:           {result.findings}")
    print(f"Original args:      {result.original_args}")
    print(f"Transformed args:   {result.transformed_args}")
    print(f"Server result:      {result.server_result}")
    print(f"Detections:         {result.detections}")
    print(f"Redacted count:     {result.redacted_count}")
    print(f"Blocked count:      {result.blocked_count}")
    print(f"Allowed count:      {result.allowed_count}")
    print("============================\n")

if __name__ == "__main__":
    asyncio.run(run_client())