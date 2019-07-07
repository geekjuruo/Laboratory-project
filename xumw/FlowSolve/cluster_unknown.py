import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

# 运行unknown数据的聚类算法
# 对unknown数据进行划分聚类

unknown_features_csv = pd.read_csv("./unknown_flows_feature.csv")
known_features_csv = pd.read_csv("./known_flows_feature.csv")
known_label_csv = pd.read_csv("./known_flows_label.csv")

# 取出其中数据列：
features_csv=unknown_features_csv[['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]

#运行Kmeans算法：
db=KMeans(n_clusters=20).fit(features_csv)

df1=pd.DataFrame(columns=['label'],data=db.labels_)
df1.to_csv('unknown_flows_label.csv')

