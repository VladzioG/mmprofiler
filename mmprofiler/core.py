# mmprofiler/core.py
import os
import tempfile
import shutil
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import pandas as pd

from .detectors_text import analyze_text_column
from .detectors_image import analyze_image_paths
from .detectors_numeric import analyze_numeric_column, summarize_numeric_columns
from .detectors_audio import analyze_audio_column
from .multimodal import multimodal_consistency_checks
from .report import generate_html_report
try:
    import requests 
except Exception:
    requests = None  


@dataclass
class ProfileResult:
    general: Dict[str, Any]
    text: Dict[str, Any]
    images: Dict[str, Any]
    audio: Dict[str, Any]
    numeric: Dict[str, Any]
    multimodal: Dict[str, Any]
    recommendations: Dict[str, Any]


class MMProfiler:
    """
   Profiler:
      - run(...) — повний прогін (text, image, numeric, audio)
      - analyze_text(column)
      - analyze_images(column, sample_images=...)
      - analyze_audio(column)
      - analyze_numeric(column)
      - summarize_tabular(...)
      - to_html / generate_html_report
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.result: Optional[ProfileResult] = None
        self._tmp_dir: Optional[str] = None

    def _ensure_tmp(self):
        if self._tmp_dir is None:
            self._tmp_dir = tempfile.mkdtemp(prefix="mmprofiler_")

    def _cleanup_tmp(self):
        if self._tmp_dir and os.path.exists(self._tmp_dir):
            try:
                shutil.rmtree(self._tmp_dir)
            except Exception:
                pass
        self._tmp_dir = None

    def analyze_text(self, column_name: str) -> Dict[str, Any]:
        return self._analyze_text_single(column_name)

    def analyze_images(self, column_name: str, sample_images: int = 200, download_remote: bool = True) -> Dict[str, Any]:
        return self._analyze_images_single(column_name, sample_images=sample_images, download_remote=download_remote)

    def analyze_audio(self, column_name: str) -> Dict[str, Any]:
        return self._analyze_audio_single(column_name)

    def analyze_numeric(self, column_name: str) -> Dict[str, Any]:
        return self._analyze_numeric_single(column_name)

    def generate_html_report(self, output_file: str = "report.html"):
        """Сумісність зі старим API"""
        if self.result is None:
            
            self.run()
        return self.to_html(output_file)
    # internal single-column analyzers (use detector modules)
    def _analyze_text_single(self, column_name: str) -> Dict[str, Any]:
        try:
            info = analyze_text_column(self.df[column_name])
        except Exception as e:
            info = {"error": str(e)}
        # ensure result exists and store
        if self.result is None:
            self.result = ProfileResult(general={"total_rows": len(self.df)},
                                        text={column_name: info},
                                        images={},
                                        audio={},
                                        numeric={},
                                        multimodal={},
                                        recommendations={})
        else:
            self.result.text[column_name] = info
        return info
    

    def _analyze_images_single(self, column_name: str, sample_images: int = 200, download_remote: bool = True) -> Dict[str, Any]:
        # prepare local series (detectors_image supports local paths)
        series = self.df[column_name] if column_name in self.df.columns else pd.Series(dtype=object)

        for i, v in enumerate(series.fillna("").astype(str)):
            if not v:
                continue
            if v.lower().startswith("http://") or v.lower().startswith("https://"):
                if not download_remote:
                    continue
                try:
                    import requests
                except Exception:
                    return {"error": "requests not installed (needed to download image URLs). Install with pip install requests."}
       
                self._ensure_tmp()
                try:
                    r = requests.get(v, timeout=6)
                    r.raise_for_status()
                    ext = os.path.splitext(v.split("?")[0])[1] or ".jpg"
                    fname = f"img_{i}{ext}"
                    local_path = os.path.join(self._tmp_dir, fname)
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    local_paths.append(local_path)
                except Exception:
                    # skip broken url
                    continue
            else:
                if os.path.exists(v):
                    local_paths.append(v)
                else:
                    continue
            if sample_images is not None and len(local_paths) >= sample_images:
                break

        try:
            img_info = analyze_image_paths(pd.Series(local_paths))
        except Exception as e:
            img_info = {"error": str(e)}
        # cleanup tmp files
        self._cleanup_tmp()

        if self.result is None:
            self.result = ProfileResult(general={"total_rows": len(self.df)},
                                        text={},
                                        images={column_name: img_info},
                                        audio={},
                                        numeric={},
                                        multimodal={},
                                        recommendations={})
        else:
            self.result.images[column_name] = img_info
        return img_info

    def _analyze_audio_single(self, column_name: str) -> Dict[str, Any]:
        try:
            info = analyze_audio_column(self.df[column_name])
        except Exception as e:
            info = {"error": str(e)}
        if self.result is None:
            self.result = ProfileResult(general={"total_rows": len(self.df)},
                                        text={},
                                        images={},
                                        audio={column_name: info},
                                        numeric={},
                                        multimodal={},
                                        recommendations={})
        else:
            self.result.audio[column_name] = info
        return info

    def _analyze_numeric_single(self, column_name: str) -> Dict[str, Any]:
        try:
            info = analyze_numeric_column(self.df[column_name])
        except Exception as e:
            info = {"error": str(e)}
        if self.result is None:
            self.result = ProfileResult(general={"total_rows": len(self.df)},
                                        text={},
                                        images={},
                                        audio={},
                                        numeric={column_name: info},
                                        multimodal={},
                                        recommendations={})
        else:
            self.result.numeric[column_name] = info
        return info

    # Tabular summary
    def summarize_tabular(self, include_numeric: bool = True) -> Dict[str, Any]:
        summary = {}
        for col in self.df.columns:
            series = self.df[col]
            dtype = str(series.dtype)
            missing = int(series.isna().sum())
            unique = int(series.nunique(dropna=True))
            summary[col] = {"dtype": dtype, "missing": missing, "unique": unique}
            if include_numeric and pd.api.types.is_numeric_dtype(series):
                summary[col]["numeric_summary"] = analyze_numeric_column(series)
                # also store into self.result
                if self.result is None:
                    self.result = ProfileResult(general={"total_rows": len(self.df)},
                                                text={},
                                                images={},
                                                audio={},
                                                numeric={col: summary[col]["numeric_summary"]},
                                                multimodal={},
                                                recommendations={})
                else:
                    self.result.numeric[col] = summary[col]["numeric_summary"]
        return summary

    # Main run + output
    def run(self,
            text_cols: Optional[List[str]] = None,
            image_cols: Optional[List[str]] = None,
            numeric_cols: Optional[List[str]] = None,
            audio_cols: Optional[List[str]] = None,
            sample_images: int = 50,
            download_remote_images: bool = True) -> ProfileResult:

        if text_cols is None:
            text_cols = [c for c in self.df.columns if self.df[c].dtype == object]
        if image_cols is None:
            image_cols = [c for c in self.df.columns if 'img' in c.lower() or 'image' in c.lower() or 'url' in c.lower()]
        if numeric_cols is None:
            numeric_cols = [c for c in self.df.columns if pd.api.types.is_numeric_dtype(self.df[c])]
        if audio_cols is None:
            audio_cols = [c for c in self.df.columns if 'audio' in c.lower()]

        general = {"total_rows": len(self.df), "columns": list(self.df.columns)}
        text_report = {}
        image_report = {}
        audio_report = {}
        numeric_report = {}

        # text
        for col in text_cols:
            try:
                text_report[col] = analyze_text_column(self.df[col])
            except Exception as e:
                text_report[col] = {"error": str(e)}

        # image
        for col in image_cols:
            image_report[col] = self._analyze_images_single(col, sample_images=sample_images, download_remote=download_remote_images)

        # audio
        for col in audio_cols:
            audio_report[col] = self._analyze_audio_single(col)

        # numeric
        for col in numeric_cols:
           try:
              numeric_report[col] = self.analyze_numeric(col)
           except Exception as e:
              numeric_report[col] = {"error": str(e)}

        # multimodal checks
        mm_checks = multimodal_consistency_checks(self.df, text_cols=text_cols, image_cols=image_cols)

        # recommendations
        recs = self._make_recommendations(text_report, image_report, mm_checks, numeric_report, audio_report)

        self.result = ProfileResult(
            general=general,
            text=text_report,
            images=image_report,
            audio=audio_report,
            numeric=numeric_report,
            multimodal=mm_checks,
            recommendations=recs
        )
        return self.result

    def to_html(self, output_file: str = "report.html"):
        if self.result is None:
            raise RuntimeError("Run profiling before exporting report. Call profiler.run() first.")
        generate_html_report(self.result, output_file)
        return output_file

    # Recommendations
    def _make_recommendations(self, text_report, image_report, mm_checks, numeric_report, audio_report):
        recs: Dict[str, Any] = {"text": {}, "images": {}, "multimodal": [], "numeric": {}, "audio": {}}

        # text
        for col, info in text_report.items():
            if "error" in info:
                recs["text"][col] = ["cannot analyze column (error)"]
                continue
            s = []
            if info.get("empty_rows", 0) > 0:
                s.append(f"Є {info['empty_rows']} пустих рядків — розглянути заповнення або видалення.")
            if info.get("avg_length", 0) < 20:
                s.append("Середня довжина мала (<20) — подумати над додатковими ознаками.")
            recs["text"][col] = s or ["Ок."]

        # images
        for col, info in image_report.items():
            if "error" in info:
                recs["images"][col] = ["cannot analyze image column (error)"]
                continue
            s = []
            if info.get("missing_files", 0) > 0:
                s.append(f"У вибірці відсутні {info['missing_files']} файлів.")
            if info.get("valid_files", 0) == 0:
                s.append("Нема валідних зображень у вибірці — перевірити URL/шляхи або збільшити sample_images.")
            recs["images"][col] = s or ["Ок."]

        # multimodal
        if mm_checks.get("missing_modalities_percent", 0) > 0:
            recs["multimodal"].append("Є записи з відсутніми модальностями — уточнити політику пропусків.")
        if mm_checks.get("label_distribution"):
            dist = mm_checks["label_distribution"]
            if isinstance(dist, dict):
                counts = list(dist.values())
                if len(counts) > 1 and max(counts) / max(1, min(counts)) > 8:
                    recs["multimodal"].append("Сильний дисбаланс класів — розглянути ресемплінг або зважування.")

        # numeric
        for col, info in numeric_report.items():
            if isinstance(info, dict) and info.get("missing_percent", 0) > 30:
                recs["numeric"][col] = ["Великий відсоток пропусків (>30%)."]
            elif isinstance(info, dict) and info.get("skew") is not None and abs(info.get("skew", 0)) > 2:
                recs["numeric"].setdefault(col, []).append("Сильна асиметрія розподілу (skew>2). Розглянути лог-трансформацію.")

        # audio
    
        for col, info in audio_report.items():
            if isinstance(info, dict) and info.get("missing_files", 0) > 0:
                recs["audio"][col] = [f"Відсутні {info['missing_files']} аудіофайлів."]
            else:
                recs["audio"][col] = ["Ок."]

        return recs

