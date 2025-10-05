import pandas as pd
import json
from pathlib import Path

def suggest_dtype(file_path, sheet_name=None, n_rows=500):
    """
    Phân tích kiểu dữ liệu gợi ý cho từng cột trong file Excel.
    Chỉ đọc n_rows đầu tiên để tiết kiệm thời gian.
    """

    print(f"🔍 Đang phân tích {file_path} ...")
    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=n_rows)

    dtype_suggestions = {}

    for col in df.columns:
        s = df[col]
        non_null = s.dropna()

        # Nếu cột trống hoàn toàn
        if non_null.empty:
            dtype_suggestions[col] = "string"
            continue

        # Nếu toàn số nguyên
        if pd.api.types.is_integer_dtype(non_null):
            dtype_suggestions[col] = "Int64"  # có thể chứa NaN
        # Nếu toàn số thực
        elif pd.api.types.is_float_dtype(non_null):
            dtype_suggestions[col] = "float32"
        # Nếu cột là datetime
        elif pd.api.types.is_datetime64_any_dtype(non_null):
            dtype_suggestions[col] = "datetime64[ns]"
        # Nếu dạng text mà giá trị lặp lại ít (VD: mã, tên, ghi chú)
        elif non_null.nunique() > len(non_null) * 0.5:
            dtype_suggestions[col] = "string"
        # Nếu dạng text nhưng có ít giá trị lặp lại (VD: tỉnh, chi nhánh, trạng thái)
        else:
            dtype_suggestions[col] = "category"

    return dtype_suggestions


def save_json(dtype_map, output_path):
    """Ghi file dtype_map ra JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dtype_map, f, ensure_ascii=False, indent=4)
    print(f"✅ Đã lưu dtype_map vào {output_path}")


def main():
    input_file = "D:\\data\\input\\T1.2025.xlsx"

    dtype_map = suggest_dtype(input_file, "DSDH")
    save_json(dtype_map, "dtype_map.json")

    print("\n📋 Kết quả gợi ý dtype:")
    for k, v in dtype_map.items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()
