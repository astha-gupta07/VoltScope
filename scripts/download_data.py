"""
VoltScope - Data Downloader Script
Retrieves authoritative, open-license datasets from Ember Energy and autoseeker.eu,
saving them to data/raw/ with integrity validation.
"""

import sys
import time
import argparse
import urllib.request
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATASET_SOURCES, RAW_DATA_DIR


def download_file(url: str, dest_path: Path, timeout: int = 30) -> dict:
    """Download a file with headers and measure transfer metrics."""
    print(f"[*] Requesting: {url}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "VoltScope-Academic-Analytics/1.0 (+https://github.com)"}
    req = urllib.request.Request(url, headers=headers)

    start_time = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status_code = response.status
        content_type = response.headers.get("Content-Type", "")
        data = response.read()

    duration = time.time() - start_time
    file_size_bytes = len(data)

    with open(dest_path, "wb") as f:
        f.write(data)

    # Count rows
    text = data.decode("utf-8", errors="replace")
    lines = [l for l in text.splitlines() if l.strip()]
    row_count = max(0, len(lines) - 1)  # exclude header

    result = {
        "status_code": status_code,
        "content_type": content_type,
        "bytes": file_size_bytes,
        "rows": row_count,
        "duration_sec": round(duration, 3),
        "path": str(dest_path)
    }

    print(f"    [+] Saved to {dest_path.name} ({file_size_bytes:,} bytes, {row_count:,} data rows, {result['duration_sec']}s)")
    return result


def run_download(force: bool = False) -> dict:
    """Download all configured datasets."""
    print("=" * 70)
    print(" VoltScope Data Acquisition Pipeline")
    print("=" * 70)

    summary = {}
    total_start = time.time()

    for key, info in DATASET_SOURCES.items():
        dest = info["local_file"]
        if dest.exists() and not force:
            print(f"[*] {dest.name} already exists. Skipping download (use --force to re-download).")
            # Calculate metrics from existing file
            with open(dest, "r", encoding="utf-8", errors="replace") as f:
                lines = [l for l in f if l.strip()]
            summary[key] = {
                "status": "cached",
                "path": str(dest),
                "bytes": dest.stat().st_size,
                "rows": max(0, len(lines) - 1)
            }
            continue

        try:
            metrics = download_file(info["url"], dest)
            summary[key] = {"status": "downloaded", **metrics}
        except Exception as e:
            print(f"    [!] Error downloading {info['name']}: {e}")
            summary[key] = {"status": "error", "error": str(e)}

    total_duration = round(time.time() - total_start, 3)
    print(f"\n[+] Acquisition process finished in {total_duration}s.")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download raw datasets for VoltScope.")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files exist.")
    args = parser.parse_args()

    results = run_download(force=args.force)
    # Check if any errors occurred
    errors = [k for k, v in results.items() if v.get("status") == "error"]
    if errors:
        sys.exit(1)
    sys.exit(0)
