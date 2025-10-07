import re

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import time, timedelta

from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import gc
import os
import psutil
from dms_17.handle import *
import pandas as pd


def clean_columns(df_all):
    """
    Chuẩn hoá tên cột:
    - Bỏ khoảng trắng thừa 2 đầu
    - Thay \n bằng space
    - Gom nhiều khoảng trắng/tab/newline thành 1 space
    """
    df = df_all.rename(columns=lambda x: re.sub(r"\s+", " ", str(x)).strip())
    return df



process = psutil.Process(os.getpid())


def log_usage(label=""):
    mem = process.memory_info().rss / 1024 ** 2  # MB
    cpu = process.cpu_percent(interval=0.1)
    print(f"[{label}] RAM: {mem:.2f} MB | CPU: {cpu:.1f}%")


def check(input_dir):
    """Hợp nhất schema có GIỮ THỨ TỰ:
       - lấy thứ tự cột file đầu tiên làm chuẩn
       - cột mới ở các file sau sẽ append vào cuối theo thứ tự gặp
       - 'Nguồn file' luôn ở cuối
    """
    print("🔍 Đang quét schema tất cả file Excel...")
    ordered_cols: list[str] = []
    seen = set()

    # Duyệt file theo thứ tự tên để kết quả ổn định
    for file in sorted(input_dir.glob("*.xlsx")):
        try:
            df = pd.read_excel(
                file,
                sheet_name="DSDH",
                skiprows=2,
                header=0,
                nrows=0,  # đọc header thôi là đủ
                engine="openpyxl"
            )
            for c in df.columns.tolist():  # giữ đúng thứ tự trong Excel
                if c not in seen:
                    seen.add(c)
                    ordered_cols.append(c)
        except Exception as e:
            print(f"⚠️ Không đọc được cột của {file.name}: {e}")

    # Đảm bảo 'Nguồn file' nằm cuối cùng
    if "Nguồn file" not in ordered_cols:
        ordered_cols.append("Nguồn file")

    print(f"📊 Tổng số cột sau khi union (giữ thứ tự): {len(ordered_cols)}\n")
    return ordered_cols


def process_to_parquet(input_dir, parquet_path, all_columns):
    """Đọc toàn bộ file Excel trong input_dir, chuẩn hóa schema, ghi thành 1 file Parquet."""
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    # 🔹 Nếu file output cũ tồn tại → xóa trước
    if parquet_path.exists():
        try:
            parquet_path.unlink()
            print(f"🧹 Đã xóa file cũ: {parquet_path}")
        except Exception as e:
            print(f"⚠️ Không thể xóa file cũ (có thể đang mở?): {e}")

    writer = None
    file_count = 0

    for file in input_dir.glob("*.xlsx"):
        print(f"📘 Đang xử lý file: {file.name}")
        try:
            df = pd.read_excel(
                file,
                sheet_name="DSDH",
                skiprows=2,
                header=0,
                dtype_backend="pyarrow",
                engine="openpyxl"
            )

            df["Nguồn file"] = file.name  # Thêm cột Nguồn file với giá trị lên tên file

            # Bổ sung cột còn thiếu
            for col in all_columns:
                if col not in df.columns:
                    df[col] = pd.NA
            df = df[all_columns]

            df = clean_columns(df)  # Làm sạch tên cột

            # Ép toàn bộ cột sang string để tránh lỗi schema mismatch
            for col in df.columns:
                df[col] = df[col].astype("string")

            # Chuyển sang Arrow Table
            table = pa.Table.from_pandas(df, preserve_index=False)

            # Ghi file Parquet (chỉ khởi tạo writer 1 lần)
            if writer is None:
                writer = pq.ParquetWriter(parquet_path, table.schema, compression="snappy")

            writer.write_table(table)
            file_count += 1

            log_usage(f"Sau khi ghi {file.name}")
            del df, table
            gc.collect()

        except Exception as e:
            print(f"❌ Lỗi khi xử lý {file.name}: {e}")

    # Đóng writer cuối cùng
    if writer:
        writer.close()
        print(f"✅ Hoàn tất ghi {file_count} file vào {parquet_path}")
    else:
        print("❌ Không có dữ liệu nào được ghi.")