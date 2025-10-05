import pandas as pd
from pathlib import Path


def get_data(input_dir, sheet_name):
    """
    Đọc dữ liệu từ file Excel MISA, bỏ 2 dòng đầu, ép kiểu str.
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Không tìm thấy input_dir")

    df = pd.read_excel(input_dir, sheet_name=sheet_name, skiprows=2, header=0, dtype=str)
    print(f"Đọc thành công {len(df)} dòng từ {input_dir}")
    return df


def save_output(df, output_dir, file_name: str):
    """
    Xuất DataFrame ra Excel + CSV + TSV (UTF-8)
    """
    print("----- Đang xuất file Excel, CSV và TSV -----")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Đường dẫn
    output_excel = output_dir / f"{file_name}.xlsx"

    # Excel
    df.to_excel(output_excel, index=False)



    print(f"Đã xuất: {output_excel}")
