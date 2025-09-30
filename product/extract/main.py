import pandas as pd
from pathlib import Path


def export_to_excel_with_sheets(output_path: str, dfs: dict):
    """
    Xuất nhiều DataFrame vào 1 file Excel nhiều sheet.
    dfs: dict {sheet_name: DataFrame}
    """
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Đã lưu file Excel nhiều sheet tại: {output_path}")


def join_products(dms_path, interncare_path, misa_path, output_path):
    # Đọc 3 file
    df_misa = pd.read_excel(misa_path)
    df_dms = pd.read_excel(dms_path)
    df_interncare = pd.read_excel(interncare_path)

    # -------- Bước 1: Aggregate Interncare --------
    df_interncare_agg = df_interncare.groupby("ProductCode").agg(
        lambda x: "; ".join(map(str, x.dropna().unique()))
    ).reset_index()

    # Thêm cột Count dựa trên ID
    df_count = df_interncare.groupby("ProductCode")["ID"].nunique().reset_index(name="Count_ID")
    df_interncare_agg = pd.merge(df_interncare_agg, df_count, on="ProductCode", how="left")

    # -------- Bước 2: Join MISA + DMS --------
    df_joined = pd.merge(
        df_misa,
        df_dms,
        left_on="Mã",          # cột bên trái (MISA)
        right_on="Mã SP",      # cột bên phải (DMS)
        how="left"             # giữ toàn bộ MISA
    )

    # Join tiếp với Interncare (đã aggregate)
    df_joined = pd.merge(
        df_joined,
        df_interncare_agg,
        left_on="Mã",
        right_on="ProductCode",
        how="left"
    )

    # -------- Bước 3: Tạo bảng duplicated --------
    df_detail = pd.merge(
        df_misa,
        df_interncare,
        left_on="Mã",
        right_on="ProductCode",
        how="left"
    )

    # Đếm số lần trùng mỗi Mã trong Interncare
    count_series = df_detail.groupby("Mã")["ProductCode"].transform("count")

    # Lọc ra chỉ những mã có >= 2 lần trùng
    df_duplicates = df_detail[count_series >= 2].reset_index(drop=True)

    # -------- Bước 4: Xuất nhiều sheet --------
    export_to_excel_with_sheets(output_path, {
        "Joined": df_joined,
        "Duplicated_Interncare": df_duplicates
    })

    print("Số dòng JOINED:", len(df_joined))
    print("Số dòng DUPLICATED:", len(df_duplicates))
    print("Các cột JOINED:", df_joined.columns.tolist())


if __name__ == "__main__":
    dms_file = "D:\\intershop_data\\processed\\product\\products_dms_processed.xlsx"
    interncare_file = "D:\\intershop_data\\processed\\product\\products_interncare_processed.xlsx"
    misa_file = "D:\\intershop_data\\processed\\product\\products_misa_processed.xlsx"
    output_file = "D:\\intershop_data\\processed\\product\\products_joined.xlsx"

    join_products(dms_file, interncare_file, misa_file, output_file)
