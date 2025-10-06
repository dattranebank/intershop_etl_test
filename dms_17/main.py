# main.py
from pathlib import Path
import pandas as pd
import time as time_module
import psutil
import os
import pyarrow as pa
import pyarrow.parquet as pq
import gc
from dms_17.handle import *


process = psutil.Process(os.getpid())


def log_usage(label=""):
    mem = process.memory_info().rss / 1024 ** 2  # MB
    cpu = process.cpu_percent(interval=0.1)
    print(f"[{label}] RAM: {mem:.2f} MB | CPU: {cpu:.1f}%")


def main():
    start = time_module.time()
    log_usage("Trước khi chạy")

    input_dir = Path("D:/data/input")
    output_dir = Path("D:/data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = output_dir / "dms17_2025.parquet"

    # Bước 1. Hợp nhất các cột từ các file excel bằng cách dùng list
    all_columns = check(input_dir)

    # 2️⃣ Ghi tất cả file Excel → Parquet duy nhất
    process_to_parquet(input_dir, parquet_path, all_columns)

    log_usage("Sau khi xuất parquet")
    end = time_module.time()
    print(f"⏱️ Thời gian chạy: {end - start:.2f} giây")


if __name__ == "__main__":
    main()
