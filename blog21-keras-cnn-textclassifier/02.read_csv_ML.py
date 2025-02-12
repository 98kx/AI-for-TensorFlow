# -*- coding:utf-8 -*-
import csv
import numpy as np
import jieba
import jieba.analyse
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn import neighbors
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression

#----------------------------------第一步 读取文件--------------------------------
file = "data.csv"

with open(file, "r", encoding="UTF-8") as f:
    # 使用csv.DictReader读取文件中的信息
    reader = csv.DictReader(f)
    labels = []
    contents = []
    for row in reader:
        # 数据元素获取
        if row['label'] == '好评':
            res = 0
        else:
            res = 1
        labels.append(res)
        content = row['content']
        seglist = jieba.cut(content,cut_all=False)  #精确模式
        output = ' '.join(list(seglist))            #空格拼接
        #print(output)
        contents.append(output)

print(labels[:5])
print(contents[:5])


#----------------------------------第二步 数据预处理--------------------------------
# 将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
vectorizer = CountVectorizer()

# 该类会统计每个词语的tf-idf权值
transformer = TfidfTransformer()

#第一个fit_transform是计算tf-idf 第二个fit_transform是将文本转为词频矩阵
tfidf = transformer.fit_transform(vectorizer.fit_transform(contents))
for n in tfidf[:5]:
    print(n)
#tfidf = tfidf.astype(np.float32)
print(type(tfidf))

# 获取词袋模型中的所有词语  
word = vectorizer.get_feature_names()
for n in word[:5]:
    print(n)
print("单词数量:", len(word)) 

# 将tf-idf矩阵抽取出来，元素w[i][j]表示j词在i类文本中的tf-idf权重
X = tfidf.toarray()
print(X.shape)

# 使用 train_test_split 分割 X y 列表
# X_train矩阵的数目对应 y_train列表的数目(一一对应)  -->> 用来训练模型
# X_test矩阵的数目对应 	 (一一对应) -->> 用来测试模型的准确性
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.3, random_state=1)


#----------------------------------第四步 评价结果--------------------------------
def classification_pj(name, y_test, pre):
    print("算法评价:", name)
    
    # 正确率 Precision = 正确识别的个体总数 /  识别出的个体总数
    # 召回率 Recall = 正确识别的个体总数 /  测试集中存在的个体总数
    # F值 F-measure = 正确率 * 召回率 * 13 / (正确率 + 召回率)

    YC_B, YC_G = 0,0  #预测 bad good
    ZQ_B, ZQ_G = 0,0  #正确
    CZ_B, CZ_G = 0,0  #存在

    #0-good 1-bad 同时计算防止类标变化
    i = 0
    while i<len(pre):
        z = int(y_test[i])   #真实 
        y = int(pre[i])      #预测

        if z==0:
            CZ_G += 1
        else:
            CZ_B += 1
            
        if y==0:
            YC_G += 1
        else:
            YC_B += 1

        if z==y and z==0 and y==0:
            ZQ_G += 1
        elif z==y and z==1 and y==1:
            ZQ_B += 1
        i = i + 1
    print(ZQ_B, ZQ_G, YC_B, YC_G, CZ_B, CZ_G)

    # 结果输出
    P_G = ZQ_G * 1.0 / YC_G
    P_B = ZQ_B * 1.0 / YC_B
    print("Precision Good 0:{:.4f}".format(P_G))
    print("Precision Bad 1:{:.4f}".format(P_B))
    print("Avg_precision:{:.4f}".format((P_G+P_B)/2))

    R_G = ZQ_G * 1.0 / CZ_G
    R_B = ZQ_B * 1.0 / CZ_B
    print("Recall Good 0:{:.4f}".format(R_G))
    print("Recall Bad 1:{:.4f}".format(R_B))
    print("Avg_recall:{:.4f}".format((R_G+R_B)/2))

    F_G = 2 * P_G * R_G / (P_G + R_G)
    F_B = 2 * P_B * R_B / (P_B + R_B)
    print("F-measure Good 0:{:.4f}".format(F_G))
    print("F-measure Bad 1:{:.4f}".format(F_B))
    print("Avg_fmeasure:{:.4f}".format((F_G+F_B)/2))
    

#----------------------------------第三步 机器学习分类--------------------------------
# 随机森林分类方法模型
rf = RandomForestClassifier(n_estimators=20)
rf.fit(X_train, y_train)
pre = rf.predict(X_test)
print("随机森林分类")
print(classification_report(y_test, pre))
classification_pj("RandomForest", y_test, pre)
print("\n")

# 决策树分类方法模型
dtc = DecisionTreeClassifier()
dtc.fit(X_train, y_train)
pre = dtc.predict(X_test)
print("决策树分类")
print(classification_report(y_test, pre))
classification_pj("DecisionTree", y_test, pre)
print("\n")

# SVM分类方法模型
SVM = svm.LinearSVC() #支持向量机分类器LinearSVC
SVM.fit(X_train, y_train)
pre = SVM.predict(X_test)
print("支持向量机分类")
print(classification_report(y_test, pre))
classification_pj("LinearSVC", y_test, pre)
print("\n")

# KNN分类方法模型
knn = neighbors.KNeighborsClassifier() #n_neighbors=11
knn.fit(X_train, y_train)
pre = knn.predict(X_test)
print("最近邻分类")
print(classification_report(y_test, pre))
classification_pj("KNeighbors", y_test, pre)
print("\n")

# 朴素贝叶斯分类方法模型
nb = MultinomialNB()
nb.fit(X_train, y_train)
pre = nb.predict(X_test)
print("朴素贝叶斯分类")
print(classification_report(y_test, pre))
classification_pj("MultinomialNB", y_test, pre)
print("\n")

# 逻辑回归分类方法模型
LR = LogisticRegression(solver='liblinear')
LR.fit(X_train, y_train)
pre = LR.predict(X_test)
print("逻辑回归分类")
print(classification_report(y_test, pre))
classification_pj("LogisticRegression", y_test, pre)
print("\n")

