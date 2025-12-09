# mmprofiler/report.py
import html
import json
import os
from typing import Any

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Data Profiler MM Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 30px; }}
    h1 {{ color: #222; }}
    .card {{ border: 1px solid #ddd; padding: 16px; margin-bottom: 18px; border-radius: 8px; }}
    pre {{ background: #f7f7f7; padding: 10px; overflow: auto; }}
    table {{ border-collapse: collapse; }}
    td, th {{ border: 1px solid #ddd; padding: 6px 8px; }}
  </style>
</head>
<body>
  <h1>Data Profiler MM Report</h1>

  <div class="card">
    <h2>General</h2>
    <pre>{general}</pre>
  </div>

  <div class="card">
    <h2>Text analysis</h2>
    <pre>{text}</pre>
  </div>

  <div class="card">
    <h2>Image analysis</h2>
    <pre>{images}</pre>
  </div>

  <div class="card">
    <h2>Numeric analysis</h2>
    <pre>{numeric}</pre>
  </div>

  <div class="card">
    <h2>Multimodal checks</h2>
    <pre>{multimodal}</pre>
  </div>

  <div class="card">
    <h2>Recommendations</h2>
    <pre>{recs}</pre>
  </div>

</body>
</html>
"""

def generate_html_report(result, out_path="report.html"):
    """result: instance of ProfileResult (dataclass) or dict-like"""
    # Normalize dataclass or dict
    if hasattr(result, "__dict__") or hasattr(result, "__annotations__"):
        data = {
            "general": getattr(result, "general", {}),
            "text": getattr(result, "text", {}),
            "images": getattr(result, "images", {}),
            "numeric": getattr(result, "numeric", {}),
            "multimodal": getattr(result, "multimodal", {}),
            "recs": getattr(result, "recommendations", {}) or {}
        }
    else:
        # assume dict-like
        data = {
            "general": result.get("general", {}),
            "text": result.get("text", {}),
            "images": result.get("images", {}),
            "numeric": result.get("numeric", {}),
            "multimodal": result.get("multimodal", {}),
            "recs": result.get("recommendations", {}) or result.get("recs", {})
        }

    general = json.dumps(data["general"], ensure_ascii=False, indent=2)
    text = json.dumps(data["text"], ensure_ascii=False, indent=2)
    images = json.dumps(data["images"], ensure_ascii=False, indent=2)
    numeric = json.dumps(data["numeric"], ensure_ascii=False, indent=2)
    multimodal = json.dumps(data["multimodal"], ensure_ascii=False, indent=2)
    recs = json.dumps(data["recs"], ensure_ascii=False, indent=2)

    html_content = HTML_TEMPLATE.format(
        general=html.escape(general),
        text=html.escape(text),
        images=html.escape(images),
        numeric=html.escape(numeric),
        multimodal=html.escape(multimodal),
        recs=html.escape(recs)
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
