"""
Chunk a PDF, embed with text-embedding-3-large, upload to Azure AI Search.
"""
import argparse, os, pdfplumber, tiktoken, requests, uuid, base64, hashlib, json
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def embed(text:str, endpoint:str, key:str):
    r = requests.post(f"{endpoint}/openai/deployments/text-embedding-ada-002/embeddings?api-version=2024-04-01-preview",
                      headers={"api-key":key}, json={"input":[text],"model":"text-embedding-3-large"})
    r.raise_for_status(); return r.json()["data"][0]["embedding"]

def chunks(doc:str, tokens=500):
    enc=tiktoken.get_encoding("cl100k_base"); words=doc.split()
    chunk, out=[],[]
    for w in words:
        if len(enc.encode(" ".join(chunk+[w])))>tokens:
            out.append(" ".join(chunk)); chunk=[w]
        else: chunk.append(w)
    out.append(" ".join(chunk)); return out

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("file"); ap.add_argument("--endpoint"); ap.add_argument("--key");
    ap.add_argument("--index"); args=ap.parse_args()

    client=SearchClient(args.endpoint, args.index, AzureKeyCredential(args.key))
    with pdfplumber.open(args.file) as pdf:
        text=" ".join(p.extract_text() or "" for p in pdf.pages)
    for i,c in enumerate(chunks(text)):
        vec=embed(c,args.endpoint,args.key)
        client.upload_documents([{
            "id":str(uuid.uuid4()),
            "content":c,
            "vector":vec
        }])
    print("Uploaded", i+1, "chunks →", args.index)