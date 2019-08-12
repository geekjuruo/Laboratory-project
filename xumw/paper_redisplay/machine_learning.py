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
feature_csv = pd.read_csv("/data/CompletePCAP/flows_feature.csv")
app_csv = pd.read_csv("/data/CompletePCAP/flows_label.csv")

feature_list = feature_csv[['PacketTotalNum','DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]
app_list = []
for i in app_csv['label']:
	app_list.append(i)

featureTrain, featureTest, appTrain, appTest = train_test_split(feature_list, app_list, test_size = 0.2, random_state = 42)

print(type(appTest))
# KNN Classifier  
knnClf = KNeighborsClassifier()
knnClf.fit(featureTrain, appTrain)
knnResult = knnClf.predict(featureTest)
print(type(knnResult))
knnAcc = 0
for i in range(0, len(knnResult)):
	print(knnResult[i])
	print(appTest[i])
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