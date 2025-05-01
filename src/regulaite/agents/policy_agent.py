"""
Fully LLM-driven PolicyAgent (zero hard-coded rules)
----------------------------------------------------
• Few-shot prompt teaches GPT-4.1 the mapping.
• If Search is down or returns nothing we *still* ask the model;
  we simply omit RAG_CONTEXT → model answers from prior knowledge.
"""

from __future__ import annotations
import os, json, logging
from typing import List
from pydantic import BaseModel
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorQuery
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from openai import AzureOpenAI
from ..core.models import Asset, RiskReport

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_FALLBACK_CONTEXT = "No matching passages were retrieved."

_EXAMPLES = """EXAMPLE 1
--- law snippets ---
Art 5 §1 d ... indiscriminate facial recognition in public spaces ...
--- asset ---
{"type":"service","name":"city-cctv","metadata":{"purpose":"face analytics"}}
--- answer ---
{"risk_level":"unacceptable","articles":["Art 5 §1 d"],"confidence":0.93,
 "suggestions":["Prohibit use in EU"]}

EXAMPLE 2
--- law snippets ---
Annex III §5 ... credit-scoring systems ...
--- asset ---
{"type":"model","name":"loan-risk","metadata":{"sector":"credit"}}
--- answer ---
{"risk_level":"high","articles":["Annex III §5"],"confidence":0.91,
 "suggestions":["Add human oversight"]}

EXAMPLE 3
--- law snippets ---
{"type":"service","name":"my-bot","metadata":{"purpose":"chatbot"}}
--- answer ---
{"risk_level":"medium","articles":["Annex III §4"],"confidence":0.9,
 "suggestions":["Disclose AI usage, log interactions"]}

 """


class _LLMCache(BaseModel):
    """Tiny in-memory cache so repeated tests don't burn tokens."""
    store: dict[str, RiskReport] = {}

CACHE = _LLMCache()


class PolicyAgent:
    def __init__(self) -> None:
        logger.info("Initializing PolicyAgent...")
        try:
            self.oai = AzureOpenAI(
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_key=os.environ["AZURE_OPENAI_KEY"],
                api_version="2024-04-01-preview",
            )
            self.chat_model  = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1")
            self.embed_model = os.getenv("AZURE_EMBED_MODEL", "text-embedding-3-large")
            logger.info(f"Using models: chat={self.chat_model}, embed={self.embed_model}")

            self.search = SearchClient(
                endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
                index_name=os.environ["AZURE_SEARCH_INDEX"],
                credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
            )
            logger.info(f"Connected to search index: {os.environ['AZURE_SEARCH_INDEX']}")
        except Exception as e:
            logger.error(f"Failed to initialize PolicyAgent: {e}")
            raise

    # ----------  Hybrid retrieval  ----------
    def _rag_passages(self, query: str) -> str:
        logger.info(f"Searching for relevant passages with query: {query}")
        try:
            # Get embeddings from OpenAI
            logger.info("Getting embeddings from OpenAI...")
            response = self.oai.embeddings.create(
                model=self.embed_model,
                input=[query]
            )
            embedding = response.data[0].embedding
            logger.info("Successfully generated embeddings")

            # Simple search without vector query first
            logger.info("Performing search...")
            hits = self.search.search(
                search_text=query,
                top=6,
                query_type="simple"
            )
            
            results = list(hits)
            if not results:
                logger.warning("No search results found")
                return _FALLBACK_CONTEXT
            
            logger.info(f"Found {len(results)} relevant passages")
            return "\n".join(h["content"] for h in results)

        except Exception as exc:
            logger.error(f"Search failed: {exc}", exc_info=True)
            return _FALLBACK_CONTEXT

    # ----------  Public API  ----------
    def analyse(self, asset: Asset) -> RiskReport:
        logger.info(f"Analyzing asset: {asset.asset_id}")
        
        # 1) quick cache
        sig = json.dumps(asset.dict(), sort_keys=True)
        if sig in CACHE.store:
            logger.info("Found cached result")
            return CACHE.store[sig]

        # 2) build prompt
        context = self._rag_passages(json.dumps(asset.metadata))
        logger.info("Building prompt with context and examples")
        prompt  = f"""You are an EU AI-governance expert. { _EXAMPLES }

USER
--- law snippets ---
{context}
--- asset ---
{asset.json()}
--- answer ---
Please provide a JSON response with a risk_level that must be one of: unacceptable, high, medium, or low."""

        logger.info("Making OpenAI API call...")
        resp = self.oai.chat.completions.create(
            model=self.chat_model,
            messages=[{"role":"system","content":"Answer in JSON only."},
                      {"role":"user","content":prompt}],
            temperature=0,
        ).choices[0].message.content.strip()
        logger.info(f"Received response: {resp}")

        try:
            data = json.loads(resp)
            # Ensure risk_level is valid
            if data.get("risk_level") not in ["unacceptable", "high", "medium", "low"]:
                logger.warning(f"Invalid risk_level: {data.get('risk_level')}, defaulting to medium")
                data["risk_level"] = "medium"  # default to medium if invalid
            
            report = RiskReport(asset_id=asset.asset_id, **data)
            CACHE.store[sig] = report
            logger.info(f"Generated report with risk level: {report.risk_level}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}", exc_info=True)
            # Return a default medium risk report
            default_report = RiskReport(
                asset_id=asset.asset_id,
                risk_level="medium",
                articles=["Default"],
                confidence=0.5,
                suggestions=["Further analysis required"]
            )
            logger.info("Returning default medium risk report")
            return default_report