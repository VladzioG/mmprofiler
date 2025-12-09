from PIL import Image
import numpy as np

def analyze_image_paths(series):
    valid_count = 0
    missing_count = 0
    broken_count = 0
    formats = {}
    widths = []
    heights = []
    brightness = []

    for path in series:
        try:
            with Image.open(path) as img:
                valid_count += 1
                formats[img.format] = formats.get(img.format, 0) + 1
                widths.append(img.width)
                heights.append(img.height)
                brightness.append(np.array(img).mean())
        except FileNotFoundError:
            missing_count += 1
        except Exception:
            broken_count += 1

    result = {
        "valid_files": valid_count,
        "missing_files": missing_count,
        "broken_files": broken_count,
        "formats": formats,
        "widths": widths,
        "heights": heights,
        "brightness": brightness,
        "min_width": min(widths) if widths else None,
        "max_width": max(widths) if widths else None,
        "avg_width": round(float(np.mean(widths)), 2) if widths else None,
        "min_height": min(heights) if heights else None,
        "max_height": max(heights) if heights else None,
        "avg_height": round(float(np.mean(heights)), 2) if heights else None,
        "avg_brightness": round(float(np.mean(brightness)), 2) if brightness else None
    }
    return result
