# -*- encoding:utf-8
import dpkt
import socket
import scapy
from scapy.all import *
from scapy.utils import PcapReader
import numpy as np 
import pandas as pd
import random
import csv
import math
from scipy.sparse import csr_matrix, hstack
from sklearn import svm

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import  AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection  import train_test_split

# 基于端口号的分类。单分类器分类

f = open('../../../pcaptest_20190516/0.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)


def inet_to_str(inet):
    try:
        return socket.inet_ntop(socket.AF_INET,inet)
    except:
        return socket.inet_ntop(socket.AF_INET6,inet)

feature_list = []
num = 0
for ts,buf in pcap:
	feature =[]
	num += 1
	print(num)
	ethData = dpkt.ethernet.Ethernet(buf) # 物理层
	ipData = ethData.data # 网络层
	transData = ipData.data # 传输层
	appData = transData.data # 应用层
	if num > 10000:
		break
	feature.append(transData.dport) # 每个包的属性列表暂时只添加包的目的端口号
	feature_list.append(feature) # 通过dst port分析

print("--------------------------------------")
print("pcap dst port type num:", len(feature_list))

port_official_csv = pd.read_csv("./service-names-port-numbers.csv")

port_official_useful = {}
for i in range(0, len(port_official_csv)):
    if (port_official_csv['Service Name'][i] is not np.nan) and  (port_official_csv['Port Number'][i] is not np.nan):
        port_official_useful[port_official_csv['Port Number'][i]] = port_official_csv['Service Name'][i]

print("--------------------------------------")
print("official useful port number:",len(port_official_useful))

app_list = []
for i in range(0, len(feature_list)):
	x = str(feature_list[i][0]) # 第一个属性为端口号
	if (x in port_official_useful.keys()):
		app_list.append(port_official_useful[x]) 
	else:
		app_list.append('unknown')

print("--------------------------------------")
print("label set num:",len(app_list))

featureTrain, featureTest, appTrain, appTest = train_test_split(feature_list, app_list, test_size = 0.2, random_state = 42)

# KNN Classifier  
knnClf = KNeighborsClassifier()
knnClf.fit(featureTrain, appTrain)
knnResult = knnClf.predict(featureTest)

knnAcc = 0
for i in range(0, len(knnResult)):
	if knnResult[i] == appTest[i]:
		knnAcc += 1
print("KNN Accuracy:", (knnAcc*1.0)/len(appTest))

# Logistic Regression Classifier   
lrClf = LogisticRegression(penalty='l2')
lrClf.fit(featureTrain, appTrain)
lrResult = lrClf.predict(featureTest)

lrAcc = 0
for i in range(0, len(lrResult)):
	if lrResult[i] == appTest[i]:
		lrAcc += 1
print("Logistic Regression Accuracy:", (lrAcc*1.0)/len(appTest))

# Random Forest Classifier
rfClf = RandomForestClassifier(n_estimators=8)
rfClf.fit(featureTrain, appTrain)
rfResult = rfClf.predict(featureTest)

rfAcc = 0
for i in range(0, len(rfResult)):
	if rfResult[i] == appTest[i]:
		rfAcc += 1
print("Random Forest Accuracy:", (rfAcc*1.0)/len(appTest))

# Decision Tree Classifier
dtClf = DecisionTreeClassifier()
dtClf.fit(featureTrain, appTrain)
dtResult = dtClf.predict(featureTest)

dtAcc = 0
for i in range(0, len(dtResult)):
	if dtResult[i] == appTest[i]:
		dtAcc += 1
print("Decsion Tree Accuracy:", (dtAcc*1.0)/len(appTest))

# GBDT(Gradient Boosting Decision Tree) Classifier 
gbdtClf = GradientBoostingClassifier(n_estimators=200)
gbdtClf.fit(featureTrain, appTrain)
gbdtResult = gbdtClf.predict(featureTest)

gbdtAcc = 0
for i in range(0, len(gbdtResult)):
	if gbdtResult[i] == appTest[i]:
		gbdtAcc += 1
print("GBDT Accuracy:", (gbdtAcc*1.0)/len(appTest))

#AdaBoost Classifier
adaClf = AdaBoostClassifier()
adaClf.fit(featureTrain, appTrain)
adaResult = adaClf.predict(featureTest)

adaAcc = 0
for i in range(0, len(adaResult)):
	if adaResult[i] == appTest[i]:
		adaAcc += 1
print("AdaBoost Accuracy:", (adaAcc*1.0)/len(appTest))

# GaussianNB
gaussClf = GaussianNB()
gaussClf.fit(featureTrain, appTrain)
gaussResult = gaussClf.predict(featureTest)

gaussAcc = 0
for i in range(0, len(gaussResult)):
	if gaussResult[i] == appTest[i]:
		gaussAcc += 1
print("GaussianNB Accuracy:", (gaussAcc*1.0)/len(appTest))

# Multinomial Naive Bayes Classifier
mnbClf = MultinomialNB(alpha = 0.01)
mnbClf.fit(featureTrain, appTrain)
mnbResult = mnbClf.predict(featureTest)

mnbAcc = 0
for i in range(0, len(mnbResult)):
	if mnbResult[i] == appTest[i]:
		mnbAcc += 1
print("Multinomial Naive Bayes Accuracy:", (mnbAcc*1.0)/len(appTest))