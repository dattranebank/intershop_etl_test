import pyarrow.parquet as pq

# Đọc schema mà KHÔNG load dữ liệu vào RAM
parquet_file = pq.ParquetFile("D:/data/output/dms17_2025.parquet")

# Lấy danh sách cột
columns = parquet_file.schema.names
print(columns)
