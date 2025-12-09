# mmprofiler/detectors_audio.py
from typing import Dict, Any
import pandas as pd
import os

def analyze_audio_column(series: pd.Series) -> Dict[str, Any]:
    """
    Швидка перевірка аудіоколонки:
      - local existing files count
      - remote URLs count (http/https)
      - missing entries
    (Детальніше аудіо-аналіз можна додати окремо з librosa)
    """
    total = len(series)
    local_exists = 0
    remote_count = 0
    missing = 0

    for v in series.fillna("").astype(str):
        if not v.strip():
            missing += 1
            continue
        if v.lower().startswith("http://") or v.lower().startswith("https://"):
            remote_count += 1
        else:
            if os.path.exists(v):
                local_exists += 1
            else:
                missing += 1

    return {
        "total": total,
        "local_exists": int(local_exists),
        "remote_count": int(remote_count),
        "missing_files": int(missing)
    }
