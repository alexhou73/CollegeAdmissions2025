import pandas as pd

# 打开 Excel 文件
file_path = '2025.xlsx'

# 读取 '普通批' sheet 的所有列名和前10行数据
df = pd.read_excel(file_path, sheet_name='普通批')
print('列名:', df.columns.tolist())
print(df.head(10))

# 输出统计信息
print(df.describe()) 