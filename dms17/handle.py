import numpy as np
import pandas as pd
from pathlib import Path
from datetime import time, timedelta


def get_data(file_path):
    """
    Trích xuất dữ liệu sản phẩm từ file Excel MISA,
    bỏ qua hàng 1, 2 và dùng hàng 3, 4 làm header.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # Bỏ qua 2 hàng đầu, hàng 3 là header
    df = pd.read_excel(path, skiprows=2, header=0)

    print(f"Đọc thành công {len(df)} dòng từ {file_path}")
    print("Các cột:", df.columns.tolist())

    return df


def merge_date_time(df, col_date, col_time, new_col_name=None):
    """
    Gộp 2 cột ngày và giờ thành 1 cột datetime ISO 8601.

    Args:
        df (pd.DataFrame): DataFrame gốc
        col_date (str): tên cột ngày
        col_time (str): tên cột giờ
        new_col_name (str, optional): tên cột mới.
            Nếu None -> tự động đặt = "Ngày giờ " + col_date

    Returns:
        pd.DataFrame: DataFrame đã gộp cột
    """
    if new_col_name is None:
        new_col_name = "Ngày giờ " + col_date

    # Gộp cột ngày + giờ, convert datetime
    df[col_date] = pd.to_datetime(
        df[col_date].astype(str) + " " + df[col_time].astype(str),
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"  # nếu bị NaN -> thành NaT
    )

    # Đổi tên cột
    df = df.rename(columns={col_date: new_col_name})

    # Xóa cột giờ
    df = df.drop(columns=[col_time])

    return df


def xu_ly_ngay_gio(dt, thu):
    if thu in ["T2", "T3", "T4", "T5", "T6"]:
        if dt.time() <= time(8, 30):
            return pd.Timestamp.combine(dt.date(), time(8, 30))
        elif dt.time() > time(17, 30):
            return pd.Timestamp.combine(dt.date() + timedelta(days=1), time(8, 30))
        else:
            return dt
    elif thu == "T7":
        # Thứ 7 -> chuyển sang thứ 2 tuần kế tiếp
        return pd.Timestamp.combine(dt.date() + timedelta(days=2), time(8, 30))
    elif thu == "T8":
        # Chủ nhật -> chuyển sang thứ 2 tuần kế tiếp
        return pd.Timestamp.combine(dt.date() + timedelta(days=1), time(8, 30))
    return dt


def td_to_text(td):
    if pd.isna(td): return None
    days = td.days
    h, r = divmod(td.seconds, 3600)
    m, s = divmod(r, 60)
    return f"{days} ngày {h:02d}:{m:02d}:{s:02d}"


def hours_to_hms(hours):
    if pd.isna(hours):
        return None
    h = int(hours)
    m = int((hours - h) * 60)
    s = int(round(((hours - h) * 60 - m) * 60))
    return f"{h:02d}:{m:02d}:{s:02d}"


def transform_data(df_dms):
    # Gộp Ngày đặt hàng và Giờ đặt hàng
    df_dms = merge_date_time(df_dms, "Ngày đặt hàng", "Giờ đặt hàng", "Ngày giờ đặt hàng")

    # Gộp Ngày cập nhật và Giờ cập nhật
    df_dms = merge_date_time(df_dms, "Ngày cập nhật", "Giờ cập nhật", "Ngày giờ cập nhật")

    # Gộp Ngày tạo phiếu vận chuyển và Giờ tạo phiếu vận chuyển
    df_dms = merge_date_time(df_dms, "Ngày tạo \nphiếu vận chuyển", "Giờ tạo \nphiếu vận chuyển",
                             "Ngày giờ tạo phiếu vận chuyển")

    # Gộp Ngày tạo phiếu vận chuyển và Giờ tạo phiếu vận chuyển
    df_dms = merge_date_time(df_dms, "Ngày giao hàng thành công", "Giờ giao hàng thành công",
                             "Ngày giờ giao hàng thành công")

    # Thêm cột Thứ số và Thứ (1=Mon, ..., 7=Sun)
    df_dms["Thứ số"] = df_dms["Ngày giờ đặt hàng"].dt.isocalendar().day
    df_dms["Thứ"] = df_dms["Thứ số"].map({
        1: "T2",
        2: "T3",
        3: "T4",
        4: "T5",
        5: "T6",
        6: "T7",
        7: "T8"
    })

    # Tạo cột mới "Ngày giờ đặt hàng chuẩn hóa"
    df_dms["Ngày giờ đặt hàng chuẩn hóa"] = df_dms.apply(
        lambda row: xu_ly_ngay_gio(row["Ngày giờ đặt hàng"], row["Thứ"]),
        axis=1
    )

    # Điều kiện 1: Mã đơn hàng bắt đầu bằng "T"
    cond1 = df_dms["Mã\nđơn hàng"].astype(str).str.startswith("T")

    # Điều kiện 2: Ghi chú trên đơn hàng bắt đầu bằng "AN_"
    cond2 = df_dms["Ghi chú \ntrên đơn hàng"].astype(str).str.startswith("AN_")

    # Gán giá trị "Đơn trả thưởng" cho cột Loại đơn hàng khi thỏa 1 trong 2 điều kiện
    df_dms.loc[cond1 | cond2, "Loại đơn hàng"] = "Đơn trả thưởng"

    # DWH
    # Danh sách cột bạn muốn ưu tiên đưa ra đầu
    priority_cols = [
        "Ngày giờ đặt hàng",
        "Thứ số",
        "Thứ",
        "Ngày giờ đặt hàng chuẩn hóa",
        "Ngày giờ cập nhật",
        "Ngày giờ tạo phiếu vận chuyển",
        "Ngày giờ giao hàng thành công"
    ]

    # Các cột còn lại (trừ những cột ưu tiên)
    other_cols = [c for c in df_dms.columns if c not in priority_cols]

    # Đặt lại thứ tự cột
    df_dms_dwh = df_dms[priority_cols + other_cols]

    ## CS
    # Tạo cột Thời gian duyệt đơn CS
    df_dms["Thời gian duyệt đơn CS"] = df_dms["Ngày giờ cập nhật"] - df_dms["Ngày giờ đặt hàng"]

    delta = df_dms["Ngày giờ cập nhật"] - df_dms["Ngày giờ đặt hàng"]

    # Đổi timedelta -> số ngày thập phân (có thể âm, float)
    df_dms= df_dms.rename(columns={"Thời gian duyệt đơn CS": "Số ngày duyệt đơn CS"})

    # Đổi timedelta -> số ngày (float)
    df_dms["Số ngày duyệt đơn CS"] = delta / pd.Timedelta(days=1)

    # Đổi sang giờ và làm tròn 3 số thập phân
    df_dms["Số giờ duyệt đơn CS"] = (df_dms["Số ngày duyệt đơn CS"] * 24) \
        .astype("float64").round(2)
    df_dms["Số ngày duyệt đơn CS"] = df_dms["Số ngày duyệt đơn CS"].astype("float64").round(2)


    ## Kho
    # Tạo cột Ngày giờ xử lý của kho
    df_dms["Ngày giờ xử lý của kho"] = df_dms["Ngày giờ tạo phiếu vận chuyển"] - df_dms["Ngày giờ cập nhật"]

    delta = df_dms["Ngày giờ tạo phiếu vận chuyển"] - df_dms["Ngày giờ cập nhật"]

    # Đổi timedelta -> số ngày thập phân (có thể âm, float)
    df_dms= df_dms.rename(columns={"Ngày giờ xử lý của kho": "Số ngày xử lý của kho"})

    # Đổi timedelta -> số ngày (float)
    df_dms["Số ngày xử lý của kho"] = delta / pd.Timedelta(days=1)

    # Đổi sang giờ và làm tròn 3 số thập phân
    df_dms["Số giờ xử lý của kho"] = (df_dms["Số ngày xử lý của kho"] * 24) \
        .astype("float64").round(2)
    df_dms["Số ngày xử lý của kho"] = df_dms["Số ngày xử lý của kho"].astype("float64").round(2)


    ## Giao hàng
    # Tạo cột Số ngày giao hàng thành công
    df_dms["Số ngày giao hàng thành công"] = df_dms["Ngày giờ giao hàng thành công"] - df_dms["Ngày giờ tạo phiếu vận chuyển"]

    delta = df_dms["Ngày giờ giao hàng thành công"] - df_dms["Ngày giờ tạo phiếu vận chuyển"]

    # Đổi timedelta -> số ngày (float)
    df_dms["Số ngày giao hàng thành công"] = delta / pd.Timedelta(days=1)

    df_dms["Số ngày giao hàng thành công"] = df_dms["Số ngày giao hàng thành công"].astype("float64").round(2)

    # Data Mart
    # Danh sách cột bạn muốn ưu tiên đưa ra đầu
    priority_cols = [
        "Ngày giờ đặt hàng",
        "Thứ số",
        "Thứ",
        "Ngày giờ đặt hàng chuẩn hóa",
        "Ngày giờ cập nhật",
        "Ngày giờ tạo phiếu vận chuyển",
        "Ngày giờ giao hàng thành công",
        "Số ngày duyệt đơn CS",
        "Số giờ duyệt đơn CS",
        "Số ngày xử lý của kho",
        "Số giờ xử lý của kho",
        "Số ngày giao hàng thành công",
    ]

    # Các cột còn lại (trừ những cột ưu tiên)
    other_cols = [c for c in df_dms.columns if c not in priority_cols]

    # Đặt lại thứ tự cột
    df_dms_dwm = df_dms[priority_cols + other_cols]

    return df_dms_dwh, df_dms_dwm
