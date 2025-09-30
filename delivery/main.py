import pandas as pd
from pathlib import Path
from delivery.handle import *


def main():
    dms_file = "D:\\intershop_data\\raw\\dms\\dms_delivery.xlsx"
    output_path = "D:\\intershop_data\\processed\\delivery\\dms_delivery_processed.xlsx"

    # Trích xuất dữ liệu
    df_dms=get_data(dms_file)

    # Biến đổi dữ liệu
    df_dms=transform_data(df_dms)

    # Xuất file excel
    df_dms.to_excel(output_path, index=False)

if __name__ == "__main__":
    main()