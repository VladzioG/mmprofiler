from typing import List, Dict, Any
import pandas as pd
from collections import Counter

def multimodal_consistency_checks(df: pd.DataFrame, text_cols: List[str], image_cols: List[str]) -> Dict[str, Any]:
    """
    Простий набір межмодальних перевірок:
    - відсоток записів з принаймні однією модальністю відсутньою
    - простий розподіл по label (якщо є колонка 'label' або 'target')
    """
    total = len(df)
    missing_modal_count = 0
    for idx, row in df.iterrows():
        has_text = any(row.get(c) and str(row.get(c)).strip() for c in text_cols)
        has_image = any(row.get(c) and str(row.get(c)).strip() for c in image_cols)
        if not (has_text or has_image):
            missing_modal_count += 1

    label_col = None
    for cand in ["label", "target", "class"]:
        if cand in df.columns:
            label_col = cand
            break

    label_distribution = None
    if label_col:
        label_distribution = dict(Counter(df[label_col].fillna("NULL").astype(str).tolist()))

    return {
        "total_rows": total,
        "missing_modalities_count": missing_modal_count,
        "missing_modalities_percent": round(100 * missing_modal_count / max(1, total), 2),
        "label_distribution": label_distribution
    }
