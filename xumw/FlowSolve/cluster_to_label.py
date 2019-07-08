#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Charles Guo'
# 查看分出的cluster中的标签分布情况

import numpy as np
import pandas as pd

def order_dict(dicts, n):
    result = []
    result1 = []
    p = sorted([(k, v) for k, v in dicts.items()], reverse=True)
    s = set()
    for i in p:
        s.add(i[1])
    for i in sorted(s, reverse=True)[:n]:
        for j in p:
            if j[1] == i:
                result.append(j)
    for r in result:
        result1.append(r[0])
    return result1

cluster_result = pd.read_csv("./cluster_result.csv")
labels_csv = pd.read_csv("./flows_label.csv")

cluster_to_label=[{},{},{},{},{},{},{},{}]
for i in range(len(labels_csv)):
    if labels_csv["label"][i] not in cluster_to_label[cluster_result["cluster_label"][i]]:
        cluster_to_label[cluster_result["cluster_label"][i]][labels_csv["label"][i]]=1
    else:
        cluster_to_label[cluster_result["cluster_label"][i]][labels_csv["label"][i]] += 1

for i in range(8):
    print("\nclass {0}:".format(i))
    result=order_dict(cluster_to_label[i],8)
    for key in result:
        print("{0} : {1}".format(key,cluster_to_label[i][key] ))
    # for label,num in cluster_to_label[i].items():
    #     print("{0} : {1}".format(label,num))