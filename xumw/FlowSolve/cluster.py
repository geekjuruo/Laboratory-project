#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'
# 运行所有数据的Kmeans聚类算法：

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

known_features_csv = pd.read_csv("./known_flows_feature.csv")
known_labels_csv = pd.read_csv("./known_flows_label.csv")
unknown_features_csv = pd.read_csv("./unknown_flows_feature.csv")
unknown_labels_csv = pd.read_csv("./unknown_flows_label.csv")

features_csv = pd.concat([known_features_csv, unknown_features_csv], ignore_index=True)
labels_csv = pd.concat([known_labels_csv, unknown_labels_csv], ignore_index=True)

# 取出其中数据列：
features_csv=features_csv[['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]

# 归一化：
# features_csv = (features_csv - features_csv.min()) / (features_csv.max() - features_csv.min())
# features_csv.to_csv('features_normalized.csv')
# 运行DBSCAN算法：
# db = DBSCAN(eps=0.1, min_samples=20).fit(features_csv)
#运行Kmeans算法：
db=KMeans(n_clusters=50).fit(features_csv)
features_csv['cluster_label']=db.labels_
features_csv.to_csv('cluster_result.csv')
labels_csv.to_csv('all_labels.csv')

