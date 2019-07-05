#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'
# 运行聚类算法：

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

features_csv = pd.read_csv("./features_normalized.csv")
labels_csv = pd.read_csv("./flows_label.csv")

# 取出其中数据列：
features_csv=features_csv[['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]

# 归一化：
# features_csv = (features_csv - features_csv.min()) / (features_csv.max() - features_csv.min())
# features_csv.to_csv('features_normalized.csv')
# 运行DBSCAN算法：
# db = DBSCAN(eps=0.1, min_samples=20).fit(features_csv)
#运行Kmeans算法：
db=KMeans(n_clusters=8).fit(features_csv)
features_csv['cluster_label']=db.labels_
features_csv.to_csv('cluster_result.csv')

