import pandas as pd
from pathlib import Path


def get_data(file_path) -> pd.DataFrame:
    """
    Trích xuất dữ liệu sản phẩm từ file Excel interncare,
    bỏ qua hàng 1, 2 và dùng hàng 3, 4 làm header.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # Bỏ qua 3 hàng đầu, hàng 4 là header
    df = pd.read_excel(path, skiprows=3, header=0)

    print(f"Đọc thành công {len(df)} dòng từ {file_path}")
    print("Các cột:", df.columns.tolist())

    return df

# Test nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    input_path="D:\\intershop_data\\raw\\interncare\\interncare_product.xlsx"
    output_path="D:\\intershop_data\\processed\\product\\products_interncare_processed.xlsx"
    df_interncare = get_data(input_path)
    df_interncare.to_excel(output_path, index=False)
    print(df_interncare.head())
