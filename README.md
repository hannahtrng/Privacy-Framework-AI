# Final Course Project for ECE117 UCLA Fall 2025
## Team Members: | `Hannah Truong` | `Jason Vu` | `Preston Kim` | `Ryan Phua` | `Maddy Delos Reyes` | `Tingyu Gong` |

Below is the **full README in clean, copy-and-paste-ready Markdown format** exactly as you requested.

---

# 🚀 **CAPEF Privacy Shield**

**AI Assistant with Real-Time Privacy Protection**

CAPEF (Context-Aware Privacy Enforcement Framework) is a privacy firewall that sits **between the user and any LLM**, detecting sensitive personal information (PII) *before* the prompt reaches the model and enforcing configurable privacy policies:

* **Allow** – forward the raw prompt
* **Redact** – send a sanitized prompt with PII removed
* **Block** – completely prevent unsafe prompts

This project includes:

* A **FastAPI backend** implementing CAPEF + OpenAI calls
* A **React + Vite frontend** based on a custom Figma Make UI

---

# 📦 Project Structure

```text
ECE117-PRIVACY-MCP-FRAMEWORK/
│
├── mcp-security-project/        # Backend (FastAPI + CAPEF)
│   ├── src/
│   │   ├── capef_layer.py
│   │   ├── pii_detector.py
│   │   ├── redactor.py
│   │   ├── llm_client.py
│   │   ├── web_app.py
│   │   └── ...
│   └── pyproject.toml
│
└── frontend/                    # Frontend (React + Vite, Figma-based)
    ├── src/
    ├── index.html
    └── package.json
```

---

# ⚙️ 1. Backend (FastAPI + CAPEF)

## 1.1 Install dependencies

```bash
cd mcp-security-project
uv sync
```

---

## 1.2 Set your OpenAI key

```bash
export OPENAI_API_KEY="sk-YOUR-REAL-KEY"
```

Check:

```bash
echo $OPENAI_API_KEY
```

If unset → backend uses safe **stubbed responses**.

---

## 1.3 Run the backend

```bash
uv run uvicorn src.web_app:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:

* API Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**
* CAPEF endpoint: `POST http://localhost:8000/api/analyze`

Example JSON:

```json
{
  "prompt": "My SSN is 123-45-6789",
  "mode": "redact"
}
```

---

# 💻 2. Frontend (React + Vite)

## 2.1 Install deps

```bash
cd frontend
npm install
```

---

## 2.2 Run dev server

```bash
npm run dev
```

Open the URL Vite prints, usually:

```
http://localhost:5173
```

---

# 🧠 3. System Architecture

```
User → Frontend → CAPEF Layer → Sanitized Prompt → OpenAI → Response → Frontend
```

### CAPEF Modes:

| Mode       | Behavior                                          |
| ---------- | ------------------------------------------------- |
| **Allow**  | Original prompt goes to the LLM                   |
| **Redact** | PII replaced with tokens (e.g., `[REDACTED:SSN]`) |
| **Block**  | Request fully blocked; LLM not called             |

Frontend displays:

* Detected PII chips
* Sanitized prompt
* Active policy mode
* Action taken (Allowed / Redacted / Blocked)
* LLM response
* "Active Protection" status

---

# 🧪 4. Test Prompts (Recommended for Demo)

Use these to demonstrate detection, redaction, blocking, and OpenAI integration.

---

## 🔹 Basic (no PII)

* “Explain how gradient descent works.”
* “What are the benefits of using attention mechanisms?”
* “Give me examples of supervised learning.”

Expected:
No PII found; normal response.

---

## 🔹 Name + Email

```
I need help emailing my coworker John Smith at john.smith@company.com.
```

Expected:
Detects **NAME**, **EMAIL** → sanitizes accordingly.

---

## 🔹 Phone Number

```
Can you call me at (310) 555-8291?
```

Expected:
Detects PHONE.

---

## 🔹 Social Security Number

```
My SSN is 123-45-6789. Should I send this?
```

Expected:
Detects SSN → `[REDACTED:SSN]`

---

## 🔹 Credit Card Number

```
Here is my credit card: 4242 4242 4242 4242.
```

Expected:
Detects CREDIT_CARD.

---

## 🔹 API Key (Developer Secret)

```
My API key is sk-live-51bd8af9e83f. Can you store this?
```

Expected:
Detects API_KEY.

---

## 🔹 Mixed PII

```
Contact Sarah Lee at sarah.lee@ucla.edu or call 555-930-2233.
```

Expected:
Detects NAME, EMAIL, PHONE.

---

## 🔹 Address / Location

```
My home address is 1234 Sunset Blvd, Los Angeles CA 90026.
```

Expected:
Detects ADDRESS.

---

## 🔹 Block Mode Test

Switch mode → **Block**

```
My bank login is john.bank@gmail.com and password Hunter2.
```

Expected:
Blocked. LLM not called.

---

## 🔹 Redact Mode Test

Mode → **Redact**

```
My passport number is K12933844.
```

Expected:
Sanitized to `[REDACTED:PASSPORT]`.

---

## 🔹 Allow Mode Test

Mode → **Allow**

```
My name is Jennifer and my email is jen@abc.com. Can you help me write a message?
```

Expected:
Detected but forwarded unchanged.

---

# ☁️ 5. Running in GitHub Codespaces

### Terminal 1 (Backend):

```bash
cd mcp-security-project
cd src
export OPENAI_API_KEY="sk-"
uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 (Frontend):

```bash
cd "/workspaces/ECE117-PRIVACY-MCP-FRAMEWORK/mcp-security-project/src/AI Chat Interface Design" 
npm run build
```

Use forwarded ports to open UI.

---

# 🛡️ 6. Troubleshooting

### OpenAI Quota Errors (429)

```
RateLimitError: insufficient_quota
```

Add credits or increase usage caps:
[https://platform.openai.com/settings/organization/limits](https://platform.openai.com/settings/organization/limits)

---

### Frontend not receiving responses

Ensure backend is running on **8000** and your fetch URL matches:

```ts
fetch("http://localhost:8000/api/analyze")
```

---

### CORS issues

FastAPI is configured with permissive dev CORS:

```python
allow_origins=["*"]
```

---
