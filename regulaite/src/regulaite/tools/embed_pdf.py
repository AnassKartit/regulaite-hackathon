#!/usr/bin/env python
"""
embed_pdf.py – Embed PDF(s) in an Azure AI Search **hybrid** index (SDK ≥ 11.6)

Examples
--------
python embed_pdf.py --file docs/EU_AI_Act_2024.pdf  --label eu
python embed_pdf.py --folder docs                   --label laws
python embed_pdf.py --file docs/CPRA_2023.pdf       --estimate-only --ppm 0.02
"""
from __future__ import annotations
import argparse, os, pathlib, uuid, typing as t

import pdfplumber, tiktoken, tqdm.autonotebook as tqdm
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    # field + datatype helpers
    SearchField, SimpleField, SearchFieldDataType,
    # vector search
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    # semantic ranking
    SemanticConfiguration, SemanticField, SemanticPrioritizedFields,
    # top-level index
    SearchIndex,
)
from openai import AzureOpenAI

# ── CLI ────────────────────────────────────────────────────────────
ap  = argparse.ArgumentParser()
grp = ap.add_mutually_exclusive_group(required=True)
grp.add_argument("--file",   help="Single PDF")
grp.add_argument("--folder", help="Folder with PDFs")
ap.add_argument("--label", required=True, help="Prefix for index name (eu → eu_idx)")
ap.add_argument("--ppm", type=float, default=0.13,
                help="Price per million tokens ($/1M), default 0.13")
ap.add_argument("--estimate-only", action="store_true")
args = ap.parse_args()

# ── ENV ────────────────────────────────────────────────────────────
def _env(*candidates: str, required: bool = True) -> str:
    """
    Return the first defined environment variable from *candidates*.
    Raise a helpful error if none are found and *required* is True.
    """
    for c in candidates:
        val = os.getenv(c)
        if val:
            return val
    if required:
        raise SystemExit(
            f"❌ Missing environment variable. Tried: {', '.join(candidates)}\n"
            "Run `eval \"$(azd env get-values | sed 's/^/export /\")'` in your shell "
            "or set the variables manually."
        )
    return ""

endpoint  = _env("AZURE_SEARCH_ENDPOINT", "searchEndpoint", "SEARCH_ENDPOINT")
admin_key = _env("AZURE_SEARCH_KEY", "searchKey", "SEARCH_KEY")

oai = AzureOpenAI(
    azure_endpoint=_env("AZURE_OPENAI_ENDPOINT", "openaiEndpoint", "OPENAI_ENDPOINT"),
    api_key=_env("AZURE_OPENAI_KEY", "openaiKey", "OPENAI_KEY"),
    api_version="2024-04-01-preview",
)

# ── Embedding model helpers ────────────────────────────────────────
embed_model = os.getenv("AZURE_EMBED_MODEL", "text-embedding-3-large")
_MODEL_DIMS  = {
    "text-embedding-ada-002"   : 1536,
    "text-embedding-3-small"   : 1536,
    "text-embedding-3-large"   : 3072,
}
EMBED_DIMS   = _MODEL_DIMS.get(embed_model, 1536)
tok          = tiktoken.encoding_for_model("gpt-4")

# ── Gather PDFs ────────────────────────────────────────────────────
if args.file:
    paths = [pathlib.Path(args.file)]
else:
    paths = sorted(pathlib.Path(args.folder).glob("*.pdf"))
if not paths:
    raise SystemExit("❌ No PDF files found.")

# ── Create (or verify) the hybrid-ready index ──────────────────────
index_name = f"{args.label.lower()}_idx"
search     = SearchClient(endpoint, index_name, AzureKeyCredential(admin_key))

try:
    search.get_document_count()
except Exception:
    print(f"🆕 Creating index ‘{index_name}’ …")
    iclient = SearchIndexClient(endpoint, AzureKeyCredential(admin_key))

    # 1️⃣ vector search definition
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="hnsw")   # defaults are fine
        ],
        profiles=[
            VectorSearchProfile(name="default",
                                algorithm_configuration_name="hnsw")
        ]
    )

    # 2️⃣ semantic ranker definition (minimal: rank by “content”)
    semantic = SemanticConfiguration(
        name="default",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )

    idx = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(name="id",      type=SearchFieldDataType.String,
                        key=True),
            # keep as string but make it full-text searchable
            SearchField(name="content", type=SearchFieldDataType.String,
                        searchable=True, analyzer_name="en.microsoft"),
            SimpleField(name="source",  type=SearchFieldDataType.String,
                        filterable=True, facetable=True),
            # ✅ vector field — correct property names!
            SearchField(
                name="vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=EMBED_DIMS,
                vector_search_profile_name="default",
                retrievable=False          # vectors normally needn’t be returned
            ),
        ],
        vector_search=vector_search,
        semantic_settings={"configurations": [semantic]},
    )
    iclient.create_index(idx)

# ── Helpers ────────────────────────────────────────────────────────
def pdf_text(path: pathlib.Path) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)

def embed(text: str) -> list[float]:
    return oai.embeddings.create(model=embed_model, input=[text]).data[0].embedding

# ── Process each PDF ───────────────────────────────────────────────
for pdf in paths:
    text   = pdf_text(pdf)
    tokens = len(tok.encode(text))
    usd    = tokens / 1_000_000 * args.ppm
    print(f"\n📄 {pdf.name}: {tokens:,} tokens  →  ${usd:,.2f}")

    if args.estimate_only:
        continue

    # naive 800-word split; tweak as you like
    words   = text.split()
    chunks  = [" ".join(words[i:i + 800]) for i in range(0, len(words), 800)]
    uploads = []

    for chunk in tqdm.tqdm(chunks, desc="Embedding", unit="chunk"):
        uploads.append({
            "id":      str(uuid.uuid4()),
            "content": chunk,
            "vector":  embed(chunk),
            "source":  pdf.name,
        })

    # bulk upload (≤ 1 000 docs / request)
    for i in range(0, len(uploads), 1000):
        search.upload_documents(uploads[i:i + 1000])

    print(f"✓ {len(chunks)} chunks uploaded → ‘{index_name}’")

print("\n✅ Done.")
