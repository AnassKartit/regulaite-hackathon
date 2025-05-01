import re, pdfplumber, itertools

KEYWORDS = [
    # EU AI Act
    r"article\s+5[^0-9]", r"annex\s+iii",
    # CPRA / CPPA
    r"§\s*1798\.",
    # NIST
    r"risk\s+management\s+framework",
]

def extract_relevant_chunks(path, window=5):
    """
    Yield paragraphs containing keywords plus N ± window lines for context.
    Reduces token count by ~80 %.
    """
    full=[]
    if path.suffix.lower()=='.pdf':
        with pdfplumber.open(path) as pdf:
            full = [p.extract_text() or '' for p in pdf.pages]
    else:
        full = path.read_text().splitlines()

    # Flatten & search
    joined = list(itertools.chain.from_iterable(page.splitlines() for page in full))
    hits=[]
    for i,line in enumerate(joined):
        if any(re.search(k, line, re.IGNORECASE) for k in KEYWORDS):
            start=max(0,i-window); end=min(len(joined), i+window)
            hits.append("\n".join(joined[start:end]))

    # Deduplicate
    return list(dict.fromkeys(hits))