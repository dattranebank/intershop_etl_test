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
    df = pd.read_excel(path, skiprows=2, header=0)

    print(f"Đọc thành công {len(df)} dòng từ {file_path}")
    print("Các cột:", df.columns.tolist())

    return df


def transform_data(df_dms):
    # Gộp 2 cột lại và chuẩn hoá thành datetime ISO 8601
    df_dms["Ngày đặt hàng"] = pd.to_datetime(
        df_dms["Ngày đặt hàng"].astype(str) + " " + df_dms["Giờ đặt hàng"].astype(str),
        format="%d/%m/%Y %H:%M:%S"   # vì ngày gốc của bạn đang là dd/mm/yyyy
    )


    # Đổi tên cột Giờ đặt hàng thành Ngày giờ đặt hàng
    df_dms = df_dms.rename(columns={"Ngày đặt hàng": "Ngày giờ đặt hàng"})

    # Xóa cột Ngày đặt hàng
    df_dms = df_dms.drop(columns=["Ngày đặt hàng"])
    return df_dms