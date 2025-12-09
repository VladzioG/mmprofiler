# mmprofiler/detectors_numeric.py
from typing import Dict, Any
import pandas as pd
import math

def analyze_numeric_column(series: pd.Series) -> Dict[str, Any]:
    s = pd.to_numeric(series, errors="coerce")
    count = int(s.count())
    total = int(len(s))
    missing = total - count
    missing_percent = round(missing / max(1, total) * 100, 2)
    zeros = int((s == 0).sum())
    desc = s.describe(percentiles=[0.25, 0.5, 0.75]).to_dict()
    try:
        skew = float(s.skew()) if count >= 3 else None
    except Exception:
        skew = None

    return {
        "count": count,
        "total": total,
        "missing": missing,
        "missing_percent": missing_percent,
        "zeros": zeros,
        "mean": None if pd.isna(desc.get("mean")) else float(desc.get("mean")),
        "std": None if pd.isna(desc.get("std")) else float(desc.get("std")),
        "min": None if pd.isna(desc.get("min")) else float(desc.get("min")),
        "25%": None if pd.isna(desc.get("25%")) else float(desc.get("25%")),
        "50%": None if pd.isna(desc.get("50%")) else float(desc.get("50%")),
        "75%": None if pd.isna(desc.get("75%")) else float(desc.get("75%")),
        "max": None if pd.isna(desc.get("max")) else float(desc.get("max")),
        "skew": skew
    }

def summarize_numeric_columns(df):
    result = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            result[col] = analyze_numeric_column(df[col])
    return result
