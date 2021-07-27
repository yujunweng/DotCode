'''
Created on 2019年9月24日
20191003    增加時間Z值的計算
@author: 翁毓駿
'''
from pymongo import MongoClient
import numpy as np
import traceback
import os
import time
import datetime
import gc
import json
import PaperCommon as pc


def descript_statis(array1, array2=None):
	'''array1 is int, if I want to calculate original number, use array2''' 
	meanT = np.mean(array2) if array2 is not None else np.mean(array1)
	midT = np.median(array1)
	try:
		modT = np.argmax(np.bincount(array1)) 
	except ValueError:
		modT = -1
	minT = np.amin(array1)
	maxT = np.amax(array1)
	stdT = np.std(array2) if array2 is not None else np.std(array1)
	return meanT, midT, modT, minT, maxT, stdT


def calculate_mean_std(array):
	mean = np.mean(array)
	std = np.std(array)
	return mean, std
	

def mean_and_std(array1, array2, array3):
	meanT, stdT = calculate_mean_std(array1)
	meanT_pass, stdT_pass = calculate_mean_std(array2)
	meanT_fail, stdT_fail = calculate_mean_std(array3)
	return meanT, meanT_pass, meanT_fail, stdT, stdT_pass, stdT_fail


def calculate_Z(value, mean, std):
	return (value - mean) / std


def write_Z(value, mean, std, key, indexDict):
	Z = calculate_Z(value, mean, std)
	updateDict = {key:Z}
	ct.update_one(indexDict, {'$set':updateDict}, upsert = True)


if __name__ == '__main__':
	'''calaulate Z of specified field'''
	database = 'dotCode'
	collection = 'AccuTime'
	
	db = pc.clientDB(database)	
	ct = pc.clientCT(database, collection)
	
	game = 'Duck'
	toZColumn = 'tryCount'
	ZValueColumn = 'Z'+toZColumn

	maxSection = pc.find_maxSection(game)
	ct.create_index([('gameCode', 1), ('sectionId', 1)])
	sectionId, itemDifficulty, difficultyDegree = pc.add_difficulty(game, '1')

	maxId = 679000
	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數

	for section in range(1, maxSection+1):
		peo_all = [] # 有紀錄的玩家		
		meanValue = []		# 平均數
		midValue = []		# 中位數
		modValue = []		# 眾數
		maxValue = []		# 最大
		minValue = []		# 最小
		stdValue = [] 		# 標準差
		
		sta_dict = {}
		for one in ct.find({"gameCode": game, "sectionId":section}):
			# 只有計算平均數與標準差才用origin
			try:
				peo_all.append(one[toZColumn])
			except:
				print(one, "lacks key")

		if len(peo_all) > 0:
			meanValue, midValue, modValue, minValue, maxValue, stdValue = descript_statis(peo_all)

			print("section:%d\n樣本數:%6d, 平均值:%.8f, 中位數:%.8f, 標準差:%.8f" %(section, len(peo_all), meanValue, midValue, stdValue))
				
			print("開始計算Z值\n")
			for two in ct.find({"gameCode":game, "sectionId":section}):
				Z = calculate_Z(two[toZColumn], meanValue, stdValue)
				Z_dict = {ZValueColumn:Z}
				pc.judge_isinstance_numpy(Z_dict)
				ct.update_one({'_id':two['_id']}, {'$set':Z_dict}, upsert=True)	
				countInsert += 1
	print("Insert 筆數：{}".format(countInsert))