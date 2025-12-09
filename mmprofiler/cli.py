import argparse
import pandas as pd
import sys
from .core import MMProfiler

def main(argv=None):
    parser = argparse.ArgumentParser(prog="data_profilermm", description="Simple multimodal data profiler (MVP).")
    parser.add_argument("--csv", required=True, help="Path to CSV file with dataset (paths to images can be in columns).")
    parser.add_argument("--text-cols", nargs="*", help="List of text column names", default=None)
    parser.add_argument("--image-cols", nargs="*", help="List of image column names", default=None)
    parser.add_argument("--out", help="Output HTML report path", default="report.html")
    args = parser.parse_args(argv)

    df = pd.read_csv(args.csv)
    profiler = MMProfiler(df)
    profiler.run(text_cols=args.text_cols, image_cols=args.image_cols)
    profiler.to_html(args.out)
    print(f"Report written to {args.out}")

if __name__ == "__main__":
    main()
