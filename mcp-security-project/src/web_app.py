# web_app.py
"""
FastAPI server for CAPEF Privacy Shield.

Integrates Figma-designed React frontend with CAPEF privacy layer backend.
"""

import os
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from capef_layer import capef_call, Mode

app = FastAPI()

# Enable CORS for development and frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze")
async def analyze(
    prompt: str = Form(...),
    mode: str = Form("redact"),
):
    """Analyze prompt with CAPEF layer and return structured result."""
    mode_typed: Mode = mode if mode in ("allow", "redact", "block") else "redact"
    
    result = capef_call(prompt, mode=mode_typed)
    
    # Determine action based on what happened
    if result.blocked:
        action = "BLOCKED"
    elif result.findings:
        action = "REDACTED" if mode_typed == "redact" else "ALLOWED"
    else:
        action = "ALLOWED"
    
    return JSONResponse({
        "sanitized_prompt": result.sanitized_prompt,
        "llm_response": result.response or "",
        "detections": [
            {
                "kind": d.kind,
                "value": d.value,
                "start": d.start,
                "end": d.end,
            }
            for d in result.findings
        ],
        "action": action,
        "mode": mode_typed,
    })


# Serve React frontend (built files)
# The frontend is built into this directory by Vite
frontend_dir = os.path.join(os.path.dirname(__file__), "AI Chat Interface Design", "build")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
else:
    # Development mode: frontend is served separately by Vite
    print("[web_app] Note: Built frontend not found. Run `npm run build` in the Figma chat folder.")

