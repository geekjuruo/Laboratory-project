import pandas as pd 
import csv

# 进行数据的预处理和特征归一化

pd.set_option('precision', 5) #设置精度
pd.set_option('display.float_format', lambda x: '%.5f' % x) #为了直观的显示数字，不采用科学计数法

label_csv = pd.read_csv('./flows_label.csv')
feature_csv = pd.read_csv('./flows_feature.csv')

featureName=['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']

flows_feature = []
flows_label = []

# print(type(feature_csv))
true_label = label_csv.iloc[0:1000000]
true_feature = feature_csv.iloc[0:1000000]

features_csv=true_feature[['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]
features_csv = (features_csv - features_csv.min()) / (features_csv.max() - features_csv.min())

true_label.to_csv("true_label.csv")
features_csv.to_csv("true_feature.csv")