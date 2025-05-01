#!/usr/bin/env python3
"""
estimate_embed_cost.py – Estimate the cost of embedding a PDF with
OpenAI’s **text‑embedding‑3‑large** model.

Usage examples
--------------
python estimate_embed_cost.py --file report.pdf
python estimate_embed_cost.py --url https://arxiv.org/pdf/1234.5678.pdf
python estimate_embed_cost.py --price-per-million 0.13 --file doc.pdf
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from typing import IO, Union

import pdfplumber
import requests
import tiktoken

# April 2025 pricing for text‑embedding‑3‑large (USD / 1M tokens)
PRICE_DEFAULT: float = 0.13


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pdf_text(path_or_url: str) -> str:
    """Return raw text extracted from every page of the PDF.

    Parameters
    ----------
    path_or_url : str
        Local file path or *http(s)* URL to a PDF.

    Returns
    -------
    str
        Newline‑separated page text (empty string for pages without text).
    """

    if path_or_url.startswith(("http://", "https://")):
        resp = requests.get(path_or_url, timeout=60)
        resp.raise_for_status()
        pdf_file: Union[IO[bytes], io.BytesIO] = io.BytesIO(resp.content)
    else:
        pdf_file = open(os.path.expanduser(path_or_url), "rb")

    with pdfplumber.open(pdf_file) as pdf:
        pages_text = [(page.extract_text() or "") for page in pdf.pages]

    return "\n".join(pages_text)


def count_tokens(text: str) -> int:
    """Tokenise *text* with the same tokenizer used by text‑embedding‑3‑large."""

    try:
        enc = tiktoken.encoding_for_model("text-embedding-3-large")
    except KeyError:
        # Fallback for older tiktoken versions
        enc = tiktoken.get_encoding("cl100k_base")

    return len(enc.encode(text, disallowed_special=()))


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate the USD cost to embed a PDF with text‑embedding‑3‑large."
    )

    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--file", metavar="PATH", help="Path to local PDF file")
    src_group.add_argument("--url", metavar="URL", help="HTTP(S) URL of a PDF")

    parser.add_argument(
        "--price-per-million",
        type=float,
        default=PRICE_DEFAULT,
        help="Price in USD per million tokens (default: %(default)s)",
    )

    args = parser.parse_args()
    source = args.file or args.url  # mutually exclusive – exactly one is non‑None

    try:
        text = pdf_text(source)
    except Exception as exc:  # pragma: no‑cover
        print(f"❌ Error reading PDF: {exc}", file=sys.stderr)
        sys.exit(2)

    tokens = count_tokens(text)
    cost = tokens / 1_000_000 * args.price_per_million

    print(f"PDF: {source}")
    print(f"Tokens: {tokens:,}")
    print(f"Estimated cost (@ ${args.price_per_million:.4f} per 1M): ${cost:,.4f}")


if __name__ == "__main__":
    main()
