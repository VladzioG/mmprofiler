# data_profilermm (MVP)

Простий Python-пакет для базового профайлінгу мультимодальних датасетів (text + image).

## Інсталяція
python -m venv venv
source venv/bin/activate  # або venv\Scripts\activate на Windows
pip install -r requirements.txt

## Використання
1) Через Python:
from data_profilermm import MMProfiler
prof = MMProfiler(df)
prof.run(text_cols=['caption'], image_cols=['image_path'])
prof.to_html('report.html')

2) Через CLI:
python -m data_profilermm.cli --csv data.csv --text-cols caption --image-cols image_path --out report.html

## Що реалізовано (MVP)
- Text profiling: avg length, top words, empty rows
- Image profiling: counts, formats, widths/heights, brightness
- Multimodal checks: % записів без модальностей
- Рекомендації прості на основі виявлених проблем
- HTML звіт

## Розширення (ідеї)
- аудіо-аналіз, інтерактивні графіки, hash-детекція дублікатів зображень, інтеграція з MLflow/DVC
