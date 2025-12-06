# mcp-security-project/src/llm_client.py
"""
Real OpenAI chat client for CAPEF.

- Takes the sanitized prompt from capef_layer.capef_call(...)
- Sends it to OpenAI Chat Completions (gpt-4.1-mini by default)
- Returns the model's text response.
"""

from typing import Optional
import os

from openai import OpenAI, RateLimitError  # requires openai>=1.x


# --- Client setup ---------------------------------------------------------

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("[llm_client] WARNING: OPENAI_API_KEY not set. Using stubbed responses.")
    _client: Optional[OpenAI] = None
else:
    _client = OpenAI(api_key=API_KEY)
    print("[llm_client] OpenAI client initialized.")


DEFAULT_MODEL = "gpt-4.1-mini"


def _stub_response(prompt: str) -> str:
    # Fallback when no API key is set (still useful for demos)
    preview = prompt.replace("\n", " ")[:150]
    return (
        "[STUBBED LLM RESPONSE]\n"
        "No OPENAI_API_KEY configured, so this is a fake answer.\n"
        f"Sanitized prompt preview: \"{preview}\""
    )


# --- Public function used by capef_layer ---------------------------------


def call_llm(prompt: str, model: Optional[str] = None) -> str:
    """
    Send the (sanitized) prompt to OpenAI and return the response text.

    This is called from capef_layer.capef_call(prompt, mode=...),
    so `prompt` is already sanitized according to CAPEF policy.
    """
    # If you somehow forgot the key, don't crash – just stub.
    if _client is None:
        return _stub_response(prompt)

    model_name = model or DEFAULT_MODEL

    try:
        # Use Chat Completions API (simpler, stable shape)
        resp = _client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        if not resp.choices:
            return "[LLM ERROR] No choices returned from model."

        message = resp.choices[0].message
        content = message.content

        # In most cases `content` is a plain string
        if isinstance(content, str):
            return content or "[LLM ERROR] Empty response content."

        # If it's a list of parts (some newer SDK modes), join text fields
        if isinstance(content, list):
            parts = []
            for part in content:
                # part may be dict-like or object-like
                text = getattr(part, "text", None)
                if text is None and isinstance(part, dict):
                    text = part.get("text")
                if text:
                    parts.append(text)
            if parts:
                return "".join(parts)

        # Fallback: just stringify
        return str(content)

    except RateLimitError as e:
        print(f"[llm_client] Rate limit / quota error: {e}")
        return (
            "[LLM ERROR] Rate limit or quota exceeded. "
            "CAPEF still sanitized your prompt, but the upstream model is unavailable right now."
        )
    except Exception as e:
        print(f"[llm_client] Unexpected LLM error: {e}")
        return (
            "[LLM ERROR] Unexpected error calling the model. "
            "CAPEF still ran, but the model response could not be retrieved."
        )
