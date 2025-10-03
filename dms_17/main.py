from pathlib import Path
import pandas as pd
from dms_17.io_utils import *
from dms_17.handle import *


def main():
    input_dir = Path("D:/data/input")
    output_dir = Path("D:/data/output")

    all_data = []
    for file in input_dir.glob("*.xlsx"):
        try:
            df = get_data(file, sheet_name="DSDH")
            df["Nguồn file"] = file.name
            all_data.append(df)
        except Exception as e:
            print(f"Lỗi khi xử lý {file}: {e}")

    if not all_data:
        print("Không có dữ liệu để xuất.")
        return

    df_all = pd.concat(all_data, ignore_index=True)

    # Đưa "Nguồn file" xuống cuối
    cols = [c for c in df_all.columns if c != "Nguồn file"] + ["Nguồn file"]
    df_all = df_all[cols]

    # transform
    # df_dwh, df_dwm = transform_data(df_all)

    df_all = clean_columns(df_all)
    # save
    save_output(df_all, output_dir, "Output")


if __name__ == "__main__":
    main()
