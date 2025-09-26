import pandas as pd
from pathlib import Path


def get_data(file_path) -> pd.DataFrame:
    """
    Trích xuất dữ liệu sản phẩm từ file Excel DMS.
    - Xóa hẳn hàng đầu tiên trong file.
    - Lấy hàng kế tiếp làm header.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # Đọc toàn bộ file, chưa coi hàng nào là header
    df_raw = pd.read_excel(path, header=None, engine="xlrd")

    # Bỏ dòng đầu tiên
    df_raw = df_raw.drop(index=0).reset_index(drop=True)

    # Dùng dòng đầu tiên (sau khi drop) làm header
    df_raw.columns = df_raw.iloc[0]
    df = df_raw.drop(index=0).reset_index(drop=True)

    print(f"Đọc thành công {len(df)} dòng từ {file_path}")
    print("Các cột:", df.columns.tolist())

    return df

# Test nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    path="D:/intershop-data/DMS_Product.xls"
    df_misa = get_data(path)
    df_misa.to_excel("D:/intershop-data/products_dms_processed.xlsx", index=False)
    print(df_misa.head())
