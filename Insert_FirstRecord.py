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
	modT = np.argmax(np.bincount(array1))
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
	''' 
	計算 FirstRecord 中 gameTime 及Log gameTime 的Z值 
	各種敘述性統計資料 (gameTime已經是除錯過的)	
	'''

	database = 'dotCode'
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	degree = [-2, -1, 0, 1, 2]
	sectionId, itemDifficulty, difficultyDegree = pc.add_difficulty(game, '1')
	#sectionId2, itemDifficulty2, difficultyDegree2 = pc.add_difficulty(game, '2')
	#sectionId3, itemDifficulty3, difficultyDegree3 = pc.add_difficulty(game, '3')
	maxId = 679000
	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數
	db = pc.clientDB(database)

	choice = input('''(1)Insert statistics values and Calaulate Z of game time, log game time
(2)Insert difficulty to FirstRecord：\n''')				
	startTime = time.time()
	tran_startTime = pc.to_vids_time(startTime)

	if choice == '1':
		ct = pc.clientCT(database, 'FirstRecord')
		ct.create_index([('gameCode', 1), ('sectionId', 1)])		
		for section in range(1, maxSection+1):
			sta_dict = {}
			peo_all, peo_pass, peo_fail = [], [], []
			peo_origin_all, peo_origin_pass, peo_origin_fail = [], [], []
			#log_peo_all, log_peo_pass, log_peo_fail = [], [], []
			meanT, meanT_pass, meanT_fail = None, None, None	# 平均數
			midT, midT_pass, midT_fail = None, None, None		# 中位數
			modT, modT_pass, modT_fail = None, None, None		# 眾數
			maxT, maxT_pass, maxT_fail = None, None, None		# 最大
			minT, minT_pass, minT_fail = None, None, None		# 最小
			stdT, stdT_pass, stdT_fail = None, None, None 		# 標準差				
			
			for one in ct.find({"gameCode":game, "sectionId":section}):
				gameTime_sec = int(one['gameTime_sec'])
				peo_all.append(gameTime_sec)
				peo_origin_all.append(one['gameTime_sec'])
				#log_peo_all.append(one['logGameTime_sec'])
				if one['gameStar'] > 0:
					peo_pass.append(gameTime_sec)
					peo_origin_pass.append(one['gameTime_sec'])
					#log_peo_pass.append(one['logGameTime_sec'])
				else:
					peo_fail.append(gameTime_sec)
					peo_origin_fail.append(one['gameTime_sec'])
					#log_peo_fail.append(one['logGameTime_sec'])
			
			if len(peo_all) > 0:
				meanT, midT, modT, minT, maxT, stdT = descript_statis(peo_all, peo_origin_all)
				if len(peo_pass) > 0:
					meanT_pass, midT_pass, modT_pass, minT_pass, maxT_pass, stdT_pass = descript_statis(peo_pass, peo_origin_pass)
				if len(peo_fail) > 0:	
					meanT_fail, midT_fail, modT_fail, minT_fail, maxT_fail, stdT_fail = descript_statis(peo_fail, peo_origin_fail)				
				print("section:%d, 人數:%d, 平均時間:%f, 過關人數:%d, 過關平均時間:%f" %(section, len(peo_all), meanT, len(peo_pass), meanT_pass))
				
				#log_meanT, log_meanT_pass, log_meanT_fail, log_stdT, log_stdT_pass, log_stdT_fail = mean_and_std(log_peo_all, log_peo_pass, log_peo_fail)
				
				print("開始計算Z值\n")
				for two in ct.find({"gameCode": game, "sectionId":section}):
					Z = calculate_Z(two['gameTime_sec'], meanT, stdT)
					#logZ = calculate_Z(two['logGameTime_sec'], log_meanT, log_stdT)
					firstRecord_dict = {"ZTime":Z}
					db.FirstRecord.update_one({'_id':two['_id']}, {'$set':firstRecord_dict}, upsert = True)
					countInsert += 1	
				
				sta_dict = {"FirstMeanTime":meanT, "FirstStdTime":stdT, "FirstMidTime":midT, "FirstModTime":float(modT), 
							"FirstMeanTime_pass":meanT_pass, "FirstStdTime_pass":stdT_pass, "FirstMidTime_Pass":midT_pass, "FirstModTime_pass":float(modT_pass),
							"FirstMinTime_pass":float(minT_pass), "FirstMaxTime_pass":float(maxT_pass),
							"FirstMeanTime_fail":meanT_fail, "FirstStdTime_fail":stdT_fail, "FirstMidTime_Fail":midT_fail, 
							"FirstModTime_fail":float(modT_fail), "FirstMinTime_fail":float(minT_fail), "FirstMaxTime_Fail":float(maxT_fail)
							}	
				pc.judge_isinstance_numpy(sta_dict)
				db.Sec_sta.update_one({"gameCode":game, "sectionId":section}, {'$set':sta_dict}, upsert = True)		   
		
		# 檢查Z值是否NULL
		ct.create_index([('ZTime', 1)])
		ct.create_index([('ZLogTime', 1)])
		for three in ct.find():
			if three['ZTime'] not in three.keys() or three['ZLogTime'] not in three.keys():
				print("lack key", three.keys())
	
	elif choice == '2':
		'''insert difficulty and difficulty degree of section into FirstRecord'''
		ct = pc.clientCT(database, 'FirstRecord')
		for two in ct.find():
			firstRecord_dict = {"difficulty":itemDifficulty[two['sectionId']-1], 
								"difficultyDegree_kmeans":difficultyDegree[two['sectionId']-1],
								#"difficulty2":itemDifficulty2[two['sectionId']-1], 
								#"difficultyDegree2":difficultyDegree2[two['sectionId']-1],
								#"difficulty3":itemDifficulty3[two['sectionId']-1], 
								#"difficultyDegree3":difficultyDegree3[two['sectionId']-1]									
							   }
			db.FirstRecord.update_one({"_id":two['_id']}, {'$set':firstRecord_dict}, upsert = True)
				