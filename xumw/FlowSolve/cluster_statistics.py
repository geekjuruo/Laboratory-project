import pandas as pd 
import csv
# 本文件用来分析聚类效果
# 计算聚类准确性

cluster_csv = pd.read_csv("./cluster_result.csv", low_memory=False)
label_csv = pd.read_csv("./all_labels.csv", low_memory=False)

cluster_result = {}

for item in range(0, 50): # 将每一个类初始化为一个字典
    cluster_result[item] = {}

# print(cluster_csv['cluster_label'][999999])
for item in range(0, 1000000):
    if label_csv['label'][item] not in cluster_result[cluster_csv['cluster_label'][item]]:
        cluster_result[cluster_csv['cluster_label'][item]][label_csv['label'][item]] = 1
    else:
        cluster_result[cluster_csv['cluster_label'][item]][label_csv['label'][item]] += 1

# print(cluster_result)

sumAcc = 0
for item in range(0, 50):
    listitem= sorted(cluster_result[item].items(),key=lambda x:x[1],reverse=True)
    print("第", item, "类出现最多应用类型: " , listitem[0][0])
    sum_cluster = 0
    for x in listitem:
        sum_cluster += x[1]
    print("第", item, "类聚类准确度: ", listitem[0][1]/sum_cluster)
    sumAcc += listitem[0][1]/sum_cluster

print("----------------------------------------")
print("50类平均准确率：", sumAcc/50)