import pandas as pd 
import csv
# 观察unknown端口号分布

unknown_csv = pd.read_csv("./flows_unknown_label.csv")


unknown = pd.DataFrame(unknown_csv['unknown'])
print(unknown.describe())