import pandas as pd 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import  AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection  import train_test_split

# 大小流的机器学习识别

label_csv = pd.read_csv('./flows_bigsmall_label.csv')
feature_csv = pd.read_csv('./flows_feature_all.csv')

# feature 不用包数量
feature = feature_csv[['DurationTime','PacketLenMean', 'PayloadLenMean', 'TimeGapMean']]
label = []

for item in label_csv['label']:
    label.append(item)

# print(feature)
# print(label)

featureTrain, featureTest, labelTrain, labelTest = train_test_split(feature, label, test_size = 0.2, random_state = 42)

# KNN Classifier  
knnClf = KNeighborsClassifier()
knnClf.fit(featureTrain, labelTrain)
knnResult = knnClf.predict(featureTest)

knnAcc = 0
for i in range(0, len(knnResult)):
	if knnResult[i] == labelTest[i]:
		knnAcc += 1
print("KNN Accuracy:", (knnAcc*1.0)/len(labelTest))

# Logistic Regression Classifier   
lrClf = LogisticRegression(penalty='l2')
lrClf.fit(featureTrain, labelTrain)
lrResult = lrClf.predict(featureTest)

lrAcc = 0
for i in range(0, len(lrResult)):
	if lrResult[i] == labelTest[i]:
		lrAcc += 1
print("Logistic Regression Accuracy:", (lrAcc*1.0)/len(labelTest))

# Random Forest Classifier
rfClf = RandomForestClassifier(n_estimators=8)
rfClf.fit(featureTrain, labelTrain)
rfResult = rfClf.predict(featureTest)

rfAcc = 0
for i in range(0, len(rfResult)):
	if rfResult[i] == labelTest[i]:
		rfAcc += 1
print("Random Forest Accuracy:", (rfAcc*1.0)/len(labelTest))

# Decision Tree Classifier
dtClf = DecisionTreeClassifier()
dtClf.fit(featureTrain, labelTrain)
dtResult = dtClf.predict(featureTest)

dtAcc = 0
for i in range(0, len(dtResult)):
	if dtResult[i] == labelTest[i]:
		dtAcc += 1
print("Decsion Tree Accuracy:", (dtAcc*1.0)/len(labelTest))

# GBDT(Gradient Boosting Decision Tree) Classifier 
gbdtClf = GradientBoostingClassifier(n_estimators=200)
gbdtClf.fit(featureTrain, labelTrain)
gbdtResult = gbdtClf.predict(featureTest)

gbdtAcc = 0
for i in range(0, len(gbdtResult)):
	if gbdtResult[i] == labelTest[i]:
		gbdtAcc += 1
print("GBDT Accuracy:", (gbdtAcc*1.0)/len(labelTest))

#AdaBoost Classifier
adaClf = AdaBoostClassifier()
adaClf.fit(featureTrain, labelTrain)
adaResult = adaClf.predict(featureTest)

adaAcc = 0
for i in range(0, len(adaResult)):
	if adaResult[i] == labelTest[i]:
		adaAcc += 1
print("AdaBoost Accuracy:", (adaAcc*1.0)/len(labelTest))

# GaussianNB
gaussClf = GaussianNB()
gaussClf.fit(featureTrain, labelTrain)
gaussResult = gaussClf.predict(featureTest)

gaussAcc = 0
for i in range(0, len(gaussResult)):
	if gaussResult[i] == labelTest[i]:
		gaussAcc += 1
print("GaussianNB Accuracy:", (gaussAcc*1.0)/len(labelTest))

# Multinomial Naive Bayes Classifier
mnbClf = MultinomialNB(alpha = 0.01)
mnbClf.fit(featureTrain, labelTrain)
mnbResult = mnbClf.predict(featureTest)

mnbAcc = 0
for i in range(0, len(mnbResult)):
	if mnbResult[i] == labelTest[i]:
		mnbAcc += 1
print("Multinomial Naive Bayes Accuracy:", (mnbAcc*1.0)/len(labelTest))