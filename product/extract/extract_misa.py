import pandas as pd
from pathlib import Path


def get_data(file_path) -> pd.DataFrame:
    """
    Trích xuất dữ liệu sản phẩm từ file Excel MISA,
    bỏ qua hàng 1, 2 và dùng hàng 3, 4 làm header.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # Bỏ qua 2 hàng đầu, hàng 3+4 là header
    df = pd.read_excel(path, skiprows=2, header=[0, 1])

    # Làm sạch tên cột
    new_columns = []
    for c1, c2 in df.columns:
        if "Unnamed" in str(c2):   # Nếu cột con bị trống
            new_columns.append(str(c1).strip())
        else:
            new_columns.append(f"{str(c1).strip()} - {str(c2).strip()}")

    df.columns = new_columns

    print(f"Đọc thành công {len(df)} dòng từ {file_path}")
    print("Các cột:", df.columns.tolist())

    return df

# Test nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    path="D:/intershop-data/MISA_Product.xlsx"
    df_misa = get_data(path)
    df_misa.to_excel("D:/intershop-data/products_misa_processed.xlsx", index=False)
    print(df_misa.head())
