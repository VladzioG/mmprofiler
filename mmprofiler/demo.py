import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mmprofiler.core import MMProfiler

import pandas as pd

df = pd.read_csv('train.csv')  
profiler = MMProfiler(df)
profiler.run(text_cols=["caption"], image_cols=["url"], numeric_cols=["price"], audio_cols=[], sample_images=20)
profiler.to_html("report_full.html")
