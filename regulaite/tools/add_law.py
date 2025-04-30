"""
python tools/add_law.py --pdf canada_bill_c27.pdf --label ca
"""
import argparse, os, uuid, pdfplumber
from build_embeddings import embed
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

ap = argparse.ArgumentParser(); ap.add_argument("--pdf"); ap.add_argument("--label")
args = ap.parse_args()

idx = f"{args.label}_idx"
client = SearchClient(os.getenv("AZURE_SEARCH_ENDPOINT"),
                      idx, AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")))
with pdfplumber.open(args.pdf) as pdf:
    text = "\n".join(p.extract_text() for p in pdf.pages)
for chunk in text.split("\n\n"):
    vec = embed(chunk, os.getenv("AZURE_OPENAI_ENDPOINT"),
                os.getenv("AZURE_OPENAI_KEY"))
    client.upload_documents([{"id": str(uuid.uuid4()),
                              "content": chunk,
                              "vector": vec}])
print("Indexed", idx)