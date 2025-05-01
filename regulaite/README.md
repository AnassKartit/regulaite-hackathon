# RegulAIte – instant EU AI‑Act compliance reports for any codebase

> **Fast pitch for judges:** Drag‑and‑drop a regulation PDF, click **Scan**, and get a color‑coded risk heat‑map in 60 seconds.  Powered by GPT‑4.1 (RAG‑backed) + Azure AI Search.

---

## 🔧 Local quick‑start (5 min)

```bash
# 1 – clone & create an isolated env (Python 3.11+)
$ git clone https://github.com/AnassKartit/regulaite-hackathon.git && cd regulaite-hackathon
$ python3.11 -m venv .venv
$ source .venv/bin/activate  # On Unix/macOS
$ pip install --upgrade pip
$ pip install -r regulaite/requirements.txt -e "regulaite/src[dev]"  # Quotes prevent zsh glob expansion

# 2 – spin up Functions API
# First, install Azure Functions Core Tools if not already installed
$ npm install -g azure-functions-core-tools@4

# Make sure you're in the api directory
$ cd regulaite/api

# Set up Python virtual environment for the Functions
$ python3.11 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt

# Set up environment variables (after running azd up)
$ cd ..  # back to regulaite directory
$ eval "$(azd env get-values | sed 's/^/export /')"
$ cd api  # back to api directory

# Create local.settings.json with environment variables
$ cat > local.settings.json << EOL
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "none",
    "AZURE_OPENAI_ENDPOINT": "${AZURE_OPENAI_ENDPOINT}",
    "AZURE_OPENAI_KEY": "${AZURE_OPENAI_KEY}",
    "AZURE_SEARCH_ENDPOINT": "${AZURE_SEARCH_ENDPOINT}",
    "AZURE_SEARCH_INDEX": "eu_idx",
    "AZURE_SEARCH_KEY": "${AZURE_SEARCH_KEY}"
  }
}
EOL

# Create pdfs directory for storing compliance reports
$ mkdir -p pdfs

# Kill any existing process on port 7071 if needed
$ lsof -ti:7071 | xargs kill -9 2>/dev/null || true

# Start the Functions runtime
$ func start --verbose

# 3 – front‑end (Vite + React, hot‑reload)
# Navigate to the web directory (from the api directory)
$ cd ../src/web
# Install dependencies
$ npm install
# If the dev server is already running, restart it to apply config changes
$ npm run dev   # Opens http://localhost:5173 with hot-reload enabled
```

### CLI in one line
```bash
python regulaite/src/app.py --repo microsoft/semantic-kernel
```
This prints a JSON summary **and** writes a PDF report next to your terminal.

---

## ☁️ One‑click Azure deploy (10 min)

> **Requirements:** Azure CLI ≥ 2.58, [azd](https://aka.ms/az-dev-cli), Owner rights in a subscription.

```bash
azd up                          # full stack, *including* demo "non‑compliant" assets
# or, without demo assets
azd up --params-file infra/main.parameters.nodemo.json
```
The Bicep infra (see `infra/`) provisions:
* **OpenAI** (GPT‑4.1 + text‑embedding‑3‑large)
* **AI Search** (vector + semantic)
* **Function App** (Python 3.11, Consumption plan)
* **Static Web App** (built locally by `azd`)

All connection strings & keys are surfaced as env vars – run:
```bash
set -a; eval "$(azd env get-values)"; set +a
```
…and your local Functions + CLI will Just Work™.

> **Reset / teardown**: `azd down`

---

## ✅ Tests & CI

* **pytest** unit + live‑integration (`regulaite/tests/`)  
  Local: `pytest -q`  (coverage gate ≥ 90 %)
* **GitHub Actions**: `.github/workflows/ci.yml` recreates the above with 3 steps – checkout, install, pytest.

---

## 📂 Repo map

| Path | What's inside |
|------|---------------|
| `regulaite/src/` | Core Python package (agents, orchestrator, tools) |
| `regulaite/api/` | Azure Functions – `scan`, `upload-law`, etc. |
| `regulaite/src/web/` | React UI (Vite) – drag‑and‑drop, heat‑map |
| `infra/` | Bicep modules + parameter sets |
| `tools/` | one‑off helpers (add laws, Purview push, …) |

---

## 🛡️ Responsible AI notes

* **RAG transparency** – Search snippets surfaced to GPT are logged.
* **Demo assets** deliberately violate Article 5 – marked with tag `demo=demo` and provisioned *only* when `deployDemoAssets=true`.
* **Governance export** – `tools/purview_push.py` syncs risk scores into Microsoft Purview as custom types.

---

## 📝 Judging checklist

| ✅ | What to look at |
|----|---------------|
|  | Run `azd up` → hot‑seat demo URL prints at the end |
|  | UI: upload `docs/EU_AI_Act_2024.pdf` then click **Scan** |
|  | Observe live cost estimate & token saving (~‑80 %) |
|  | Download generated PDF report |
|  | Browse code: zero hard‑coded rules – policy is **100 % LLM** |

---

## 🙋 FAQ

* **Why GPT‑4.1 and not cheaper models?**  Legal text has subtle nuances; GPT‑4.1 consistently performed best in our ad‑hoc validation during development.
* **Secret keys in repo?!**  The ones you see are **dummy placeholders** generated for the hackathon; override via env vars.
* **Can I plug in US‑only laws?**  Yes – use `tools/add_law.py --pdf nist_rmf.pdf --label us`.

---

Made with ☕ + 🥐 in Paris – Anass Kartit