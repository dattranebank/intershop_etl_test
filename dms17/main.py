import pandas as pd
from pathlib import Path
from delivery.handle import *


def main():
    dms_file = "D:\\data\\T1.2025.xlsx"
    output_path_1 = "D:\\data\\test.xlsx"

    # Trích xuất dữ liệu
    df_dms=get_data(dms_file)
    print(df_dms)
    df_dms.to_excel(output_path_1, index=False)


    # # Biến đổi dữ liệu
    # df_dms_dwh, df_dms_dwm=transform_data(df_dms)
    #
    # # Xuất file excel
    # df_dms_dwh.to_excel(output_path_1, index=False)
    # df_dms_dwm.to_excel(output_path_2, index=False)

if __name__ == "__main__":
    main()