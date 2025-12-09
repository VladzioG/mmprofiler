import re
from collections import Counter
import statistics
from typing import Any, Dict, Iterable

def simple_tokenize(s: str):
    return [t.lower() for t in re.findall(r"[A-Za-zА-Яа-яЇїІіЄєҐґ0-9]+", s)]

def analyze_text_column(series) -> Dict[str, Any]:
    texts = series.fillna("").astype(str).tolist()
    lengths = [len(t) for t in texts]
    stripped_empty = sum(1 for t in texts if not t.strip())
    token_counts = [len(simple_tokenize(t)) for t in texts]
 
    words = Counter()
    for t in texts:
        words.update(simple_tokenize(t))
    top = words.most_common(10)

    return {
        "total": len(texts),
        "non_empty": len(texts) - stripped_empty,
        "empty_rows": int(stripped_empty),
        "avg_length": round(statistics.mean(lengths), 2) if lengths else 0,
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
        "avg_tokens": round(statistics.mean(token_counts), 2) if token_counts else 0,
        "top_words": top
    }
