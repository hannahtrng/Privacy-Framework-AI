# Figma Chat Interface Integration

## Overview
The Figma-designed chat interface has been integrated with the CAPEF privacy backend without major changes to the backend logic.

## Structure
- **Frontend**: React + TypeScript chat UI built from Figma  
  Location: `src/AI Chat Interface Design/`
- **Backend**: FastAPI server with CAPEF privacy layer  
  Location: `src/web_app.py`
- **Integration**: Hook (`useCapefIntegration`) connects frontend to backend API

## How It Works

1. **User types a prompt** in the ChatPanel
2. **Frontend calls `/api/analyze`** (POST) with the prompt and privacy mode
3. **Backend processes** through CAPEF layer:
   - Detects PII in the prompt
   - Applies privacy mode (allow/redact/block)
   - Calls LLM if allowed
4. **Frontend displays** results:
   - Chat message with LLM response
   - PII detections in DefensesDashboard
   - Sanitized prompt version
   - Action taken (ALLOWED/REDACTED/BLOCKED)

## Build & Run

### Development Mode

**Terminal 1 - Frontend dev server:**
```bash
cd src/AI\ Chat\ Interface\ Design
npm install
npm run dev
# Opens at http://localhost:5173 (proxies /api to backend)
```

**Terminal 2 - Backend server:**
```bash
cd src
export SILICONFLOW_API_KEY=your_key  # Optional: for LLM responses
uvicorn web_app:app --reload
# API at http://localhost:8000
```

### Production Mode

1. **Build frontend:**
```bash
cd src/AI\ Chat\ Interface\ Design
npm install
npm run build
# Output: build/ directory
```

2. **Run backend (serves frontend + API):**
```bash
cd src
uvicorn web_app:app --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

## API Endpoint

### POST `/api/analyze`
**Request:**
```
Content-Type: application/x-www-form-urlencoded
- prompt: string (required)
- mode: string (required: 'allow', 'redact', or 'block')
```

**Response:**
```json
{
  "sanitized_prompt": "I need help scheduling a meeting...",
  "llm_response": "I can help you with that!",
  "detections": [
    {"kind": "Email", "value": "john@company.com", "start": 45, "end": 62}
  ],
  "action": "REDACTED",
  "mode": "redact"
}
```

## Key Components

- **ChatPanel**: Chat interface + sends prompts to backend
- **DefensesDashboard**: Displays PII detections, sanitized prompts, privacy mode
- **useCapefIntegration**: React hook that handles API calls to `/api/analyze`

## No Backend Changes
The CAPEF layer, LLM client, and redactor remain unchanged. Only `web_app.py` was updated to:
1. Provide the `/api/analyze` JSON endpoint
2. Serve the React frontend

## Troubleshooting

- **Frontend doesn't load**: Check that `npm run build` completed and `build/` exists
- **API errors**: Verify `uvicorn web_app:app` is running on port 8000
- **LLM responses not showing**: Set `SILICONFLOW_API_KEY` or check backend logs
- **CORS errors in dev**: Already configured via middleware in `web_app.py`
