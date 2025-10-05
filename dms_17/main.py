from pathlib import Path
import pandas as pd
from dms_17.handle import cast_dtypes, clean_columns
import time
import psutil
import os
import pyarrow as pa
import pyarrow.parquet as pq
import gc

process = psutil.Process(os.getpid())

def log_usage(label=""):
    mem = process.memory_info().rss / 1024**2  # MB
    cpu = process.cpu_percent(interval=0.1)
    print(f"[{label}] RAM: {mem:.2f} MB | CPU: {cpu:.1f}%")

def main():
    start = time.time()
    log_usage("Trước khi chạy")

    input_dir = Path("D:/data/input")
    output_dir = Path("D:/data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = output_dir / "Output_Staging.parquet"
    writer = None
    file_count = 0

    for file in input_dir.glob("*.xlsx"):
        print(f"📘 Đang đọc file: {file.name}")
        try:
            # Đọc Excel (skip 2 dòng đầu)
            df = pd.read_excel(
                file,
                sheet_name="DSDH",
                skiprows=2,
                header=0,
                dtype_backend="pyarrow",  # Giảm RAM
                engine="openpyxl"
            )

            df["Nguồn file"] = file.name
            df = clean_columns(df)
            df = cast_dtypes(df)

            # === Đảm bảo schema thống nhất giữa các file ===
            expected_cols = [
                "Năm", "Tháng", "Ngày", "Ngày đặt", "Giờ tạo", "Kênh", "Mã Vùng", "Tên Vùng",
                "Mã Route", "Mã Nhân Viên", "Tên nhân viên", "Mã KH", "Tên Khách Hàng",
                "Tên Người Liên Hệ", "ID Khách Hàng", "Loại KH", "Tỉnh Thành phố", "Quận Huyện",
                "Phường xã", "Địa chỉ", "Trạng thái đơn hàng", "Tài Khoản Duyệt Đơn",
                "Tên Người Duyệt Đơn", "Loại hợp đồng", "Mã Phiếu Gộp", "Mã Đơn Hàng",
                "Mã đơn hàng Tham chiếu", "Tài khoản tạo", "Tên người tạo", "Ngày Duyệt đơn",
                "Mã Sản Phẩm", "Tên Sản Phẩm", "Nhãn Hàng", "Số lượng", "Loại hàng", "Đơn giá",
                "Doanh số trước chiết khấu (+VAT)", "Doanh số trước chiết khấu (-VAT)",
                "Chiết khấu bằng tiền (+VAT)", "Chiết khấu bằng tiền (-VAT)",
                "Doanh số sau chiết khấu (-VAT)", "Tiền VAT", "Thanh Toán", "% Thuế VAT",
                "Chiết khấu bằng hàng (-VAT)", "Mã CTKM", "Tên CTKM",
                "Ghi Chú của NVBH", "Trạng thái Misa", "Loại đơn",
                "Đơn giá NB (+VAT)", "Doanh số Gross Sales",
                "Được áp dụng TL",  # có thể thiếu ở một số file
                "Nguồn file"
            ]

            # Thêm các cột còn thiếu và đảm bảo thứ tự
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = pd.NA  # tạo cột rỗng

            df = df[expected_cols]

            # 🔧 Fix lỗi kiểu dữ liệu không tương thích Arrow
            for col in df.columns:
                if str(df[col].dtype) == "category":
                    df[col] = df[col].astype("string")

            table = pa.Table.from_pandas(df, preserve_index=False)

            # Khởi tạo writer lần đầu tiên
            if writer is None:
                writer = pq.ParquetWriter(parquet_path, table.schema, compression="snappy")

            # Ghi nối tiếp
            writer.write_table(table)

            file_count += 1
            log_usage(f"Sau khi ghi {file.name}")

            # Giải phóng bộ nhớ
            del df, table
            gc.collect()

        except Exception as e:
            print(f"❌ Lỗi khi xử lý {file}: {e}")

    if writer is not None:
        writer.close()
        print(f"✅ Đã xuất file Parquet: {parquet_path}")
    else:
        print("❌ Không có dữ liệu nào được ghi.")

    log_usage("Sau khi xuất parquet")
    end = time.time()
    print(f"⏱️ Thời gian chạy: {end - start:.2f} giây")
    print(f"📦 Tổng số file Excel đã xử lý: {file_count}")

if __name__ == "__main__":
    main()
