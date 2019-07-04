#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# features_csv = pd.read_csv("./flows_feature.csv")
labels_csv = pd.read_csv("./flows_label.csv")

features_csv = pd.read_csv("./features_normalized.csv")
# 归一化：
# features_csv = (features_csv - features_csv.min()) / (features_csv.max() - features_csv.min())
# features_csv.to_csv('features_normalized.csv')
# print("normalization success")

# 取出其中数据列：
features=features_csv[['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]


print("slice success")
# 归一化：
# features_csv = (features_csv - features_csv.min()) / (features_csv.max() - features_csv.min())
# features_csv.to_csv('features_normalized.csv')
# 运行DBSCAN算法：
db = DBSCAN(eps=0.1, min_samples=20).fit(features)

features_csv['cluster_label']=db.labels_
features_csv.to_csv('cluster_result.csv')

# 运行KMEANS算法：
# colors = np.array(['red','blue','black','yellow'])
# scaler = StandardScaler()
# feature_scaled = scaler.fit_transform(features)
# km = KMeans(n_clusters=3).fit(feature_scaled)
# features_csv["scaled_cluster"] = km.labels_
# features_csv.groupby("scaled_cluster").mean()
# pd.plotting.scatter_matrix(features, c=colors[features_csv.scaled_cluster], alpha=1, figsize=(10,10), s=100)
# plt.suptitle("with 3 centroids initialized using scaled_cluster")
# plt.show()
# db=KMeans(n_clusters=8).fit(features)
# print("train success")
# features_csv['cluster_label']=db.labels_
# features_csv.to_csv('cluster_result.csv')



