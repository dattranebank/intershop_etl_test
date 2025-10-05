from pathlib import Path
import pandas as pd
from dms_17.io_utils import save_output
from dms_17.handle import cast_dtypes, clean_columns
import time
import psutil
import os

process = psutil.Process(os.getpid())

def log_usage(label=""):
    mem = process.memory_info().rss / 1024**2  # MB
    cpu = process.cpu_percent(interval=0.1)    # %
    print(f"[{label}] RAM: {mem:.2f} MB | CPU: {cpu:.1f}%")


def main():
    start = time.time()
    log_usage("Trước khi chạy")

    input_dir = Path("D:/data/input")
    output_dir = Path("D:/data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "Output.csv"

    first = True

    for file in input_dir.glob("*.xlsx"):
        print(f"Đang đọc file: {file.name}")
        try:
            # Bước 1: đọc Excel thành DataFrame
            df_excel = pd.read_excel(
                file,
                sheet_name="DSDH",
                skiprows=2,
                header=0,
                dtype=str,
                engine="openpyxl"
            )

            # Ghi tạm ra CSV để stream lại bằng chunksize
            temp_csv = output_dir / f"temp_{file.stem}.csv"
            df_excel.to_csv(temp_csv, index=False, encoding="utf-8-sig")
            del df_excel  # giải phóng RAM sớm

            # Bước 2: đọc CSV theo chunk
            for chunk in pd.read_csv(temp_csv, chunksize=5000, dtype=str, encoding="utf-8-sig"):
                chunk["Nguồn file"] = file.name
                chunk = clean_columns(chunk)
                chunk = cast_dtypes(chunk)

                chunk.to_csv(
                    output_file,
                    mode="a",
                    index=False,
                    header=first,
                    encoding="utf-8-sig"
                )
                first = False
                log_usage(f"Chunk từ {file.name}")

            # Xóa file tạm
            temp_csv.unlink(missing_ok=True)

        except Exception as e:
            print(f"Lỗi khi xử lý {file}: {e}")

    log_usage("Sau khi chạy")
    end = time.time()
    print(f"⏱️ Thời gian chạy: {end - start:.2f} giây")
    print(f"✅ Đã xuất file: {output_file}")


if __name__ == "__main__":
    main()
