## 🏗️ Architecture Overview

![RegulAIte high-level architecture](/docs/architecture.drawio.png)

| # | Component | Azure resource | Purpose | Key interactions |
|---|-----------|---------------|---------|------------------|
| 1 | **Static Web App (React)** | Static Web Apps | Zero-back-end UI – drag-and-drop PDF, run scan, download report | Calls Functions’ HTTPS endpoints |
| 2 | **Azure Functions API** | Function App (Y1) | Serverless API façade <br/>• `scan` → triggers Semantic Kernel pipeline <br/>• `upload_law` → embeds & indexes PDF <br/>• `downloadpdf` → streams generated report | Reads service keys from app-settings; talks to SK, Storage, Search, OAI |
| 3 | **Semantic Kernel Orchestrator** | Python package inside Functions | Chains three **agents**: <br/>① Discovery Agent <br/>② Policy Agent (GPT-4 + RAG) <br/>③ Documentation Agent (PDF) | Invoked by `scan` function; passes data between agents |
| 4 | **Azure OpenAI** | Cognitive Services (GPT-4.1 & text-embedding-3-large) | • Generates embeddings for law chunks <br/>• Classifies risk & suggests fixes | REST – key stored in Function settings |
| 5 | **Azure AI Search** | Search (Basic) | Hybrid index **`regulaite-laws`** stores embedded passages; provides vector + keyword retrieval for RAG | Queried directly by Policy Agent |
| 6 | **Storage Account** | Storage V2 (LRS) | • Raw uploaded PDFs <br/>• Generated `compliance_*.pdf` reports | SAS URL returned by `downloadpdf` |

### 🔄 End-to-end Flow

1. **Upload law PDF** → `upload_law`  
   *Chunks*, *embeds* (OpenAI), *indexes* (AI Search).

2. **Run Compliance Scan** → `scan`  
   *Semantic Kernel pipeline*  
   1. **Discovery** – find cloud / repo assets  
   2. **Policy** – RAG + GPT-4 → risk JSON  
   3. **Documentation** – colour-coded PDF saved to Storage

3. Web app receives JSON ➜ heat-map grid animates.  
   User clicks **Download Report** ➜ `downloadpdf` streams the PDF.

> **Serverless + pay-as-you-go:** Static Web Apps, Functions, AI Search & OpenAI – everything deployed with one Bicep file.  
> **Agentic design:** the orchestrator and each agent map 1-to-1 with the judging criteria for Azure AI Agent Service usage.
