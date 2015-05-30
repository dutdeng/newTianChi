#! /usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import *
from sklearn import *
import cPickle
import os
import csv
import operator

def strToInt(x):
	if x != '':
		return int(x)
	else:
		return 0
def strToLong(x):
	if x != '':
		return long(x)
	else:
		return 0

def dicCount():# tong ji zong shu
	dicCount = {}
	dicCount2 = {}
	with open('./user_balance_table.csv', 'r') as fr:
		lineTitle = fr.readline()
		lines = fr.readlines()
		for line in lines:
			lineList = line.strip().split(',')
			user_id = lineList[0]
			report_date = lineList[1]
			if report_date not in dicCount:
				dicCount[report_date] = [0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
				dicCount2[report_date] = [0,0]
			dicCount[report_date] += array(map(strToInt,lineList[4:]))
			dicCount2[report_date] += array(map(strToLong,lineList[2:4]))
			#print dicCount[report_date]
	f = open('./dicCount.pkl','wb')
	cPickle.dump(dicCount,f,-1)
	f.close()
	f = open('./dicCount2.pkl','wb')
	cPickle.dump(dicCount2,f,-1)
	f.close()
	f = open("dicCount.txt","w")
	for data in dicCount:
		line = list(dicCount[data])
		line2 = list(dicCount2[data])
		line = map(str,line)
		line2 = map(str,line2)
		f.write(data+','+line2[0]+','+line2[1]+','+line[0]+','+line[1]+','+line[2]+','+line[3]+','+line[4]+','+line[5]+','+line[6]+','+line[7]+','+line[8]+','+line[9]+','+line[10]+','+line[11]+','+line[12]+','+line[13]+'\n')
	
def findUserFirstBuyDay():
	userFirstBuyDay = {}
	with open('./user_balance_table.csv', 'r') as fr:
		lineTitle = fr.readline()
		lines = fr.readlines()
		for line in lines:
			lineList = line.strip().split(',')
			user_id = lineList[0]
			report_date = lineList[1]
			if user_id not in userFirstBuyDay:
				userFirstBuyDay[user_id] = 0
			if userFirstBuyDay[user_id] == 0 or (userFirstBuyDay[user_id] != 0 and (userFirstBuyDay[user_id] > int(report_date))):
				userFirstBuyDay[user_id] = int(report_date)
			
	f = open('./userFirstBuyDay.pkl','wb')
	cPickle.dump(userFirstBuyDay,f,-1)
	f.close()
	for user in userFirstBuyDay:
		print user,userFirstBuyDay[user]

def gennerateUserFeature():
	userPurchaseFeature = {}
	userRedeemFeature = {}
	with open('./user_balance_table.csv', 'r') as fr:
		lineTitle = fr.readline()
		lines = fr.readlines()
		for line in lines:
			lineList = line.strip().split(',')
			user_id = lineList[0]
			report_date = lineList[1]
			d_purchase = lineList[5]
			redeem = lineList[8]
			index = ((int(report_date) - 20130000)/10000)*12 - 7 + (int(report_date)%10000)/100
			#print report_date,index
			if user_id not in userPurchaseFeature:
				userPurchaseFeature[user_id] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			if user_id not in userRedeemFeature:
				userRedeemFeature[user_id] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			userPurchaseFeature[user_id][index] += int(d_purchase)
			userRedeemFeature[user_id][index] += int(redeem)

	f = open('./userPurchaseFeature.pkl','wb')
	cPickle.dump(userPurchaseFeature,f,-1)
	f.close()
	f = open('./userRedeemFeature.pkl','wb')
	cPickle.dump(userRedeemFeature,f,-1)
	f.close()

def countCurrentUser():
	userFirstBuyDay = cPickle.load(open('./userFirstBuyDay.pkl', 'rb'))
	currentUser = {}
	for user in userFirstBuyDay:
		if userFirstBuyDay[user] not in currentUser:
			currentUser[userFirstBuyDay[user]] = 0
		currentUser[userFirstBuyDay[user]] += 1
	sortedCurrentUser = sorted(currentUser.iteritems(), key=operator.itemgetter(0), reverse=False)
	allCurrentUser = {}
	allCurrentUser[sortedCurrentUser[0][0]] = sortedCurrentUser[0][1]
	for i in range(len(sortedCurrentUser)-1):
		allCurrentUser[sortedCurrentUser[i+1][0]] = allCurrentUser[sortedCurrentUser[i][0]] + sortedCurrentUser[i+1][1]
	f = open('./allCurrentUser.pkl','wb')
	cPickle.dump(allCurrentUser,f,-1)
	f.close()

def splitDataBuyDate():
	os.mkdir('./date')
	with open('./user_balance_table.csv', 'r') as fr:
		lineTitle = fr.readline()
		lines = fr.readlines()
		for line in lines:
			lineList = line.strip().split(',')
			user_id = lineList[0]
			report_date = lineList[1]
			with open('./date/'+str(report_date)+'.csv', 'a') as f:
				fw = csv.writer(f)
				fw.writerow(lineList)
			f.close()

def countCurrentActiveUser():
	userPurchaseFeature = cPickle.load(open('./userPurchaseFeature.pkl', 'rb'))
	userRedeemFeature = cPickle.load(open('./userRedeemFeature.pkl', 'rb'))
	CurrentActiveUser = {}
	fileList = [x for x in os.listdir('./date')]
	for File in fileList:
		date = File.split('.')[0]
		index = ((int(date) - 20130000)/10000)*12 - 7 + (int(date)%10000)/100
		CurrentActiveUser[date] = 0
		with open('./date/'+File,'r') as fr:
			for line in fr.readlines():
				lineList = line.strip().split(',')
				user_id = lineList[0]
				last_three_purchase = 0
				for i in range(3):
					last_three_purchase += userPurchaseFeature[user_id][index-1-i]
				last_three_redeem = 0
				for i in range(3):
					last_three_redeem += userRedeemFeature[user_id][index-1-i]
				if last_three_purchase != 0 and last_three_redeem != 0:
					CurrentActiveUser[date] += 1
	f = open('./CurrentActiveUser.pkl','wb')
	cPickle.dump(CurrentActiveUser,f,-1)
	f.close()

def findActiveUser():
	userPurchaseFeature = cPickle.load(open('./userPurchaseFeature.pkl', 'rb'))
	userRedeemFeature = cPickle.load(open('./userRedeemFeature.pkl', 'rb'))
	count = 0
	for user in userPurchaseFeature:
		last_three_purchase = 0
		for i in range(3):
			last_three_purchase += userPurchaseFeature[user][13-i]
		last_three_redeem = 0
		for i in range(3):
			last_three_redeem += userRedeemFeature[user][13-i]
		if last_three_purchase !=0 and last_three_redeem != 0:
			count += 1
	print count 

def countMeanByDate():
	dicCount = cPickle.load(open('./dicCount.pkl', 'rb'))
	dicCount2 = cPickle.load(open('./dicCount2.pkl', 'rb'))
	allCurrentUser = cPickle.load(open('./allCurrentUser.pkl', 'rb'))
	CurrentActiveUser = cPickle.load(open('./CurrentActiveUser.pkl', 'rb'))
	#purchaseCurrentActiveUser = cPickle.load(open('./purchaseCurrentActiveUser.pkl', 'rb'))
	#redeemCurrentActiveUser = cPickle.load(open('./redeemCurrentActiveUser.pkl', 'rb'))
	meanByDate = {}
	for date in dicCount:	
		meanByDate[int(date)] = [0,0,0,0]  # userNum balance purchase redeem
		#meanByDate[int(date)][0] = allCurrentUser[int(date)]
		meanByDate[int(date)][0] = CurrentActiveUser[date]
		#meanByDate[int(date)][1] = redeemCurrentActiveUser[date]
		meanByDate[int(date)][1] = (float)(dicCount2[date][0]) / CurrentActiveUser[date]
		meanByDate[int(date)][2] = (float)(dicCount[date][0]) / CurrentActiveUser[date]
		meanByDate[int(date)][3] = (float)(dicCount[date][4]) / CurrentActiveUser[date]
	f = open('./meanByDate.pkl','wb')
	cPickle.dump(meanByDate,f,-1)
	f.close()
	f = open("dicCount2.txt","w")
	for date in meanByDate:
		f.write(str(date)+','+str(meanByDate[int(date)][0])+','+str(meanByDate[int(date)][1])+','+str(meanByDate[int(date)][2])+','+str(meanByDate[int(date)][3])+'\n')

def generateDateFeature():
	dateFeature = {}
	meanByDate = cPickle.load(open('./meanByDate.pkl', 'rb'))
	sortedMeanByDate = sorted(meanByDate.iteritems(), key=operator.itemgetter(0), reverse=False)
	#print sortedMeanByDate[365][0]  # date
	#print sortedMeanByDate[365][1][0] # userNum
	for i in range(325,427):
		print sortedMeanByDate[i][0],sortedMeanByDate[i][1][0],sortedMeanByDate[i][1][2],sortedMeanByDate[i][1][3]
		dateFeature[sortedMeanByDate[i][0]] = [0, 0,0, 0,0,0, 0,0, 0,0,0] # userNum1,userNum2, 30 _2 days, 180 days, * 1 week, * 1 month, 3 months, 6 months
		dateFeature[sortedMeanByDate[i][0]][0] = sortedMeanByDate[i][1][0]
		#dateFeature[sortedMeanByDate[i][0]][1] = sortedMeanByDate[i][1][1]
		
		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(30,60):
			threeDaysUserSum += sortedMeanByDate[i-1-j][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-1-j][1][2]) * sortedMeanByDate[i-1-j][1][0]
		dateFeature[sortedMeanByDate[i][0]][1] = float(threeDaysPurchaseSum) / threeDaysUserSum
		'''
		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(30,180):
			threeDaysUserSum += sortedMeanByDate[i-1-j][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-1-j][1][2]) * sortedMeanByDate[i-1-j][1][0]
		dateFeature[sortedMeanByDate[i][0]][2] = float(threeDaysPurchaseSum) / threeDaysUserSum
		'''
		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,8):
			threeDaysUserSum += sortedMeanByDate[i-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-(1+j)*7][1][2]) * sortedMeanByDate[i-(1+j)*7][1][0]
		dateFeature[sortedMeanByDate[i][0]][3] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,16):
			threeDaysUserSum += sortedMeanByDate[i-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-(1+j)*7][1][2]) * sortedMeanByDate[i-(1+j)*7][1][0]
		dateFeature[sortedMeanByDate[i][0]][4] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,28):
			threeDaysUserSum += sortedMeanByDate[i-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-(1+j)*7][1][2]) * sortedMeanByDate[i-(1+j)*7][1][0]
		dateFeature[sortedMeanByDate[i][0]][5] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(30,60):
			threeDaysUserSum += sortedMeanByDate[i-1-j][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-1-j][1][3]) * sortedMeanByDate[i-1-j][1][0]
		dateFeature[sortedMeanByDate[i][0]][6] = float(threeDaysPurchaseSum) / threeDaysUserSum
		'''
		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(30,180):
			threeDaysUserSum += sortedMeanByDate[i-1-j][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-1-j][1][3]) * sortedMeanByDate[i-1-j][1][0]
		dateFeature[sortedMeanByDate[i][0]][7] = float(threeDaysPurchaseSum) / threeDaysUserSum
		'''
		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,8):
			threeDaysUserSum += sortedMeanByDate[i-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-(1+j)*7][1][3]) * sortedMeanByDate[i-(1+j)*7][1][0]
		dateFeature[sortedMeanByDate[i][0]][8] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,16):
			threeDaysUserSum += sortedMeanByDate[i-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-(1+j)*7][1][3]) * sortedMeanByDate[i-(1+j)*7][1][0]
		dateFeature[sortedMeanByDate[i][0]][9] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,28):
			threeDaysUserSum += sortedMeanByDate[i-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[i-(1+j)*7][1][3]) * sortedMeanByDate[i-(1+j)*7][1][0]
		dateFeature[sortedMeanByDate[i][0]][10] = float(threeDaysPurchaseSum) / threeDaysUserSum
	
	for i in range(20140901,20140931):
		dateFeature[i] = [0, 0,0, 0,0,0, 0,0, 0,0,0]
		dateFeature[i][0] = sortedMeanByDate[426][1][0] + (i-20140900)*5
		
		index = i - 20140900 + 426	
			
		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(30,60):
			threeDaysUserSum += sortedMeanByDate[index-1-j][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-1-j][1][2]) * sortedMeanByDate[index-1-j][1][0]
		dateFeature[i][1] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,8):
			threeDaysUserSum += sortedMeanByDate[index-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-(1+j)*7][1][2]) * sortedMeanByDate[index-(1+j)*7][1][0]
		dateFeature[i][3] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,16):
			threeDaysUserSum += sortedMeanByDate[index-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-(1+j)*7][1][2]) * sortedMeanByDate[index-(1+j)*7][1][0]
		dateFeature[i][4] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,28):
			threeDaysUserSum += sortedMeanByDate[index-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-(1+j)*7][1][2]) * sortedMeanByDate[index-(1+j)*7][1][0]
		dateFeature[i][5] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(30,60):
			threeDaysUserSum += sortedMeanByDate[index-1-j][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-1-j][1][3]) * sortedMeanByDate[index-1-j][1][0]
		dateFeature[i][6] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,8):
			threeDaysUserSum += sortedMeanByDate[index-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-(1+j)*7][1][3]) * sortedMeanByDate[index-(1+j)*7][1][0]
		dateFeature[i][8] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,16):
			threeDaysUserSum += sortedMeanByDate[index-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-(1+j)*7][1][3]) * sortedMeanByDate[index-(1+j)*7][1][0]
		dateFeature[i][9] = float(threeDaysPurchaseSum) / threeDaysUserSum

		threeDaysUserSum = 0
		threeDaysPurchaseSum = 0
		for j in range(4,28):
			threeDaysUserSum += sortedMeanByDate[index-(1+j)*7][1][0]
			threeDaysPurchaseSum += long(sortedMeanByDate[index-(1+j)*7][1][3]) * sortedMeanByDate[index-(1+j)*7][1][0]
		dateFeature[i][10] = float(threeDaysPurchaseSum) / threeDaysUserSum
	
	for date in dateFeature:
		print date,dateFeature[date]
	f = open('./dateFeature.pkl','wb')
	cPickle.dump(dateFeature,f,-1)
	f.close()
	f = open("dicCount3.txt","w")
	for date in dateFeature:
		f.write(str(date)+','+str(dateFeature[date][0])+','+str(dateFeature[date][1])+','+str(dateFeature[date][2])+','+str(dateFeature[date][3])+','+str(dateFeature[date][4])+','+str(dateFeature[date][5])+','+str(dateFeature[date][6])+','+str(dateFeature[date][7])+','+str(dateFeature[date][8])+','+str(dateFeature[date][9])+','+str(dateFeature[date][10])+'\n')

def generateDateFeatureMatrix():
	dicCount = cPickle.load(open('./dicCount.pkl', 'rb'))
	dateFeature = cPickle.load(open('./dateFeature.pkl', 'rb'))
	trainDataMatrix_purchase = []
	trainDataLabel_purchase = []
	trainDataMatrix_redeem = []
	trainDataLabel_redeem = []
	for date in dateFeature:
		if date < 20140901:
			#print date
			userNum1 = dateFeature[date][0]
			newRecord = dateFeature[date][1:6]
			newRecord2 = dateFeature[date][6:]
			datePurchase = dicCount[str(date)][0]
			meanPurchase = float(datePurchase) / userNum1
			dateRedeem = dicCount[str(date)][4]
			meanRedeem = float(dateRedeem) / userNum1
			trainDataLabel_purchase.append(meanPurchase)
			trainDataMatrix_purchase.append(newRecord)
			trainDataLabel_redeem.append(meanRedeem)
			trainDataMatrix_redeem.append(newRecord2)
	testDataMatrix_purchase = []
	testDatalabel_purchase = []
	testDataMatrix_redeem = []
	testDatalabel_redeem = []
	userNumber1 = []
	for date in dateFeature:
		if date > 20140831:
			#print date
			userNum1 = dateFeature[date][0]
			newRecord = dateFeature[date][1:6]
			newRecord2 = dateFeature[date][6:]
			userNumber1.append(userNum1)
			#datePurchase = dicCount[str(date)][0]
			#meanPurchase = float(datePurchase) / userNum1
			#dateRedeem = dicCount[str(date)][4]
			#meanRedeem = float(dateRedeem) / userNum1
			#testDatalabel_purchase.append(meanPurchase)
			testDataMatrix_purchase.append(newRecord)
			#testDatalabel_redeem.append(meanRedeem)
			testDataMatrix_redeem.append(newRecord2)
	
	#print testDataMatrix
	#print testDatalabel
	#clf = linear_model.LinearRegression()
	clf = linear_model.Ridge(alpha=1)
	clf.fit(trainDataMatrix_purchase,trainDataLabel_purchase)
	print clf.coef_
	print clf.predict(testDataMatrix_purchase)
	#print userNumber
	_purchase = multiply(clf.predict(testDataMatrix_purchase),userNumber1)
	print _purchase
	#print abs((clf.predict(testDataMatrix_purchase) - testDatalabel_purchase) / testDatalabel_purchase)
	#print mean(abs((clf.predict(testDataMatrix_purchase) - testDatalabel_purchase) / testDatalabel_purchase))
	
	#clf = linear_model.LinearRegression()
	clf = linear_model.Ridge(alpha=1)
	clf.fit(trainDataMatrix_redeem,trainDataLabel_redeem)
	print clf.coef_
	print clf.predict(testDataMatrix_redeem)
	#print userNumber
	_redeem = multiply(clf.predict(testDataMatrix_redeem),userNumber1)
	print _redeem
	
	with open('tc_comp_predict_table.csv','w') as f:
		for i in range(len(_purchase)):
			date = str(i+20140901)
			f.write(date+','+str(int(_purchase[i]))+','+str(int(_redeem[i]))+'\n')
	
	#print abs((clf.predict(testDataMatrix_redeem) - testDatalabel_redeem) / testDatalabel_redeem)
	#print mean(abs((clf.predict(testDataMatrix_redeem) - testDatalabel_redeem) / testDatalabel_redeem))

	#print (clf.predict(testDataMatrix) - testDatalabel) / testDatalabel
	#print mean(abs((clf.predict(testDataMatrix) - testDatalabel) / testDatalabel))
	#print abs((clf.predict(trainDataMatrix) - trainDataLabel) / trainDataLabel)
	#print mean(abs((clf.predict(trainDataMatrix) - trainDataLabel) / trainDataLabel))
		
if __name__ == '__main__':
	#dicCount()
	#findUserFirstBuyDay()
	#countCurrentUser()
	#splitDataBuyDate()
	#countCurrentActiveUser()
	countMeanByDate()
	generateDateFeature()
	generateDateFeatureMatrix()
	#gennerateUserFeature()
	#findActiveUser()
