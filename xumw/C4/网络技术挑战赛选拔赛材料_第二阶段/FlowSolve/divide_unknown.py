import pandas as pd 
import csv
# 观察unknown端口号分布
# 提取unknown数据用以后面的分类

all_feature_csv = pd.read_csv("./last_feature.csv")
all_label_csv = pd.read_csv("./last_label.csv")

unknown_flows = []
known_flows = []

known_label = []
for item in range(0, 1000000):
    unknown_feature = []
    known_feature = []
    if all_label_csv['label'][item] == 'unknown':
        unknown_feature.append(all_feature_csv['PacketTotalNum'][item])
        unknown_feature.append(all_feature_csv['DurationTime'][item])
        unknown_feature.append(all_feature_csv['PacketLenMean'][item])
        unknown_feature.append(all_feature_csv['PayloadLenMean'][item])
        unknown_feature.append(all_feature_csv['TimeGapMean'][item])
        unknown_flows.append(unknown_feature)
    else:
        known_feature.append(all_feature_csv['PacketTotalNum'][item])
        known_feature.append(all_feature_csv['DurationTime'][item])
        known_feature.append(all_feature_csv['PacketLenMean'][item])
        known_feature.append(all_feature_csv['PayloadLenMean'][item])
        known_feature.append(all_feature_csv['TimeGapMean'][item])
        known_flows.append(known_feature)
        known_label.append(all_label_csv['label'][item])
    

featureName=['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']
df1=pd.DataFrame(columns=featureName,data=unknown_flows)
df1.to_csv('unknown_flows_feature.csv')

df2=pd.DataFrame(columns=featureName,data=known_flows)
df2.to_csv("known_flows_feature.csv")

labelName=['label']
df2=pd.DataFrame(columns=labelName,data=known_label)
df2.to_csv('known_flows_label.csv')