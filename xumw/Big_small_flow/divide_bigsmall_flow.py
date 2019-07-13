import pandas as pd 
import csv

# 用于区分大小流，根据我们数据的实际分布

# flows_label = pd.read_csv('../../../flows_label_all.csv')
flows_feature = pd.read_csv('../../../flows_feature_all.csv')

flows_bigsmall_label = []
for item in flows_feature['PacketTotalNum']:
    if item <= 7:
        flows_bigsmall_label.append('small')
    else:
        flows_bigsmall_label.append('big')

df = pd.DataFrame(columns=['label'], data=flows_bigsmall_label)
df.to_csv('./flows_bigsmall_label.csv')

# flows_bigsmall_label = pd.read_csv('./flows_bigsmall_label.csv')
# print(flows_bigsmall_label['label'].describe())