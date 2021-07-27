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
	'''calaulate Z of accumulated time and log accumulated time'''
	database = 'dotCode'
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	degree = ['Very Simple', 'Simple', 'Medium', 'Hard', 'Very Hard']
	sectionId, itemDifficulty, difficultyDegree = pc.add_difficulty(game, '1')
	#sectionId2, itemDifficulty2, difficultyDegree2 = pc.add_difficulty(game, '2')
	#sectionId3, itemDifficulty3, difficultyDegree3 = pc.add_difficulty(game, '3')
	maxId = 679000
	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數
	db = pc.clientDB(database)	
	ct = pc.clientCT(database, 'AccuTime')
	
	ct.create_index([('gameCode', 1), ('sectionId', 1)])
	ct.create_index([('gameCode', 1), ('accumulatedTime_sec', 1)])
	
	for section in range(1, maxSection+1):
		peo_all = [] # 有紀錄的玩家
		peo_pass = [] # 過關的玩家 
		peo_fail = [] # 沒過關的玩家
		peo_all_wrong = []	# 有紀錄的玩家的累積錯誤時間
		peo_pass_wrong = []	# 過關的玩家的累積錯誤時間
		peo_origin_all, peo_origin_pass, peo_origin_fail = [], [], []				
		peo_origin_all_wrong, peo_origin_pass_wrong = [], []
		#log_peo_all, log_peo_pass, log_peo_fail = [], [], []
		
		meanT, meanT_pass, meanT_fail = pc.create_lists(0, 3, None)		# 平均數
		midT, midT_pass, midT_fail = pc.create_lists(0, 3, None)		# 中位數
		modT, modT_pass, modT_fail = pc.create_lists(0, 3, None)		# 眾數
		maxT, maxT_pass, maxT_fail = pc.create_lists(0, 3, None)		# 最大
		minT, minT_pass, minT_fail = pc.create_lists(0, 3, None)		# 最小
		stdT, stdT_pass, stdT_fail = pc.create_lists(0, 3, None) 		# 標準差
		
		meanWt, meanWT_pass, meanWT_fail = pc.create_lists(0, 3, None)	# 平均數
		midWT, midWT_pass, midWT_fail = pc.create_lists(0, 3, None)		# 中位數
		modWT, modWT_pass, modWT_fail = pc.create_lists(0, 3, None)		# 眾數
		maxWT, maxWT_pass, maxWT_fail = pc.create_lists(0, 3, None)		# 最大
		minWT, minWT_pass, minWT_fail = pc.create_lists(0, 3, None)		# 最小
		stdWT, stdWT_pass, stdWT_fail = pc.create_lists(0, 3, None) 		# 標準差
		
		sta_dict = {}
		
		
		for one in ct.find({"gameCode": game, "sectionId":section}):
			# 只有計算平均數與標準差才用origin
			try:
				accumulatedTime_sec = int(one['accuTime_sec'])
				wrongTime_sec = int(one['wrongTime_sec']) 
				
				peo_all.append(accumulatedTime_sec)
				peo_all_wrong.append(wrongTime_sec)
				
				peo_origin_all.append(one['accuTime_sec'])
				peo_origin_all_wrong.append(one['wrongTime_sec'])
				#log_peo_all.append(one['logAccuTime_sec'])
				
				if one['gameStar'] > 0:		# 只算有過關
					peo_pass.append(accumulatedTime_sec)
					peo_pass_wrong.append(wrongTime_sec)
					peo_origin_pass.append(one['accuTime_sec'])
					peo_origin_pass_wrong.append(one['wrongTime_sec'])
					#log_peo_pass.append(one['logAccuTime_sec'])
				else:		# 只算沒過關
					peo_fail.append(accumulatedTime_sec)
					peo_origin_fail.append(one['accuTime_sec'])
					#log_peo_fail.append(one['logAccuTime_sec'])
			
			except:
				print(one, "lacks key")
		
		if len(peo_all) > 0:
			meanT, midT, modT, minT, maxT, stdT = descript_statis(peo_all, peo_origin_all)
			meanWT, midWT, modWT, minWT, maxWT, stdWT = descript_statis(peo_all_wrong, peo_origin_all_wrong)
			if len(peo_pass) > 0:
				meanT_pass, midT_pass, modT_pass, minT_pass, maxT_pass, stdT_pass = descript_statis(peo_pass, peo_origin_pass)
				meanWT_pass, midWT_pass, modWT_pass, minWT_pass, maxWT_pass, stdWT_pass = descript_statis(peo_pass_wrong, peo_origin_pass_wrong)
			if len(peo_fail) > 0:	
				meanT_fail, midT_fail, modT_fail, minT_fail, maxT_fail, stdT_fail = descript_statis(peo_fail, peo_origin_fail)
				#meanWT_fail, midWT_fail, modWT_fail, minWT_fail, maxWT_fail, stdWT_fail = descript_statis(peo_fail_wrong, peo_origin_fail_wrong)	
			
			print("section:%d\n全部人數:%6d, 平均時間:%f, 中位數時間:%f" %(section, len(peo_origin_all), meanT, midT))
			print("過關人數:%6d, 平均時間:%f, 中位數時間:%f" %(len(peo_origin_pass), meanT_pass, midT_pass))
			print("失敗人數:%6d, 平均時間:%f, 中位數時間:%f" %(len(peo_origin_fail), meanT_fail, midT_fail))
			print("全部標準差:%.4f, 過關玩家標準差:%.4f\n" %(stdT, stdT_pass))
			
			print("全部人數:%6d, 平均錯誤時間:%f, 中位數錯誤時間:%f" %(len(peo_origin_all_wrong), meanWT, midWT))
			print("過關人數:%6d, 平均錯誤時間:%f, 中位數錯誤時間:%f" %(len(peo_origin_pass_wrong), meanWT_pass, midWT_pass))
			print("全部標準差:%.4f, 過關玩家標準差:%.4f\n" %(stdWT, stdWT_pass))				
			
			# log_meanT, log_meanT_pass, log_meanT_fail, log_stdT, log_stdT_pass, log_stdT_fail = mean_and_std(log_peo_all, log_peo_pass, log_peo_fail)
			
			print("開始計算Z值\n")
			for two in ct.find({"gameCode":game, "sectionId":section}):
				Z = calculate_Z(two['accuTime_sec'], meanT, stdT)
				#logZ = calculate_Z(two['logAccuTime_sec'], log_meanT, log_stdT)
				accu_dict = {"ZTime":Z, 
							 #"ZLogTime":logZ
							}
				db.AccuTime.update_one({'_id':two['_id']}, {'$set':accu_dict}, upsert = True)	
				countInsert += 1
			
			sta_dict = {"AccuMeanTime":meanT, "AccuStdTime":stdT, "AccuMidTime":midT, "AccuModTime":float(modT), "AccuMinTime":float(minT), "AccuMaxTime":float(maxT),	
						"AccuMeanTime_pass":meanT_pass, "AccuStdTime_pass":stdT_pass, "AccuMidTime_pass":midT_pass,
						"AccuModTime_pass":float(modT_pass), "AccuMinTime_pass":float(minT_pass), "AccuMaxTime_pass":float(maxT_pass),
						"AccuMeanTime_fail":meanT_fail, "AccuStdTime_fail":stdT_fail, "AccuMidTime_fail":midT_fail, 
						"AccuModTime_fail":float(modT_fail), "AccuMinTime_fail":float(minT_fail), "AccuMaxTime_fail":float(maxT_fail),		
						"AccuMeanWTime":meanWT, "AccuStdWTime":stdWT, "AccuMidWTime":midWT, "AccuModWTime":float(modWT), "AccuMinWTime":float(minWT), "AccuMaxWTime":float(maxWT),
						"AccuMeanWTime_pass":meanWT_pass, "AccuStdWTime_pass":stdWT_pass, "AccuMidWTime_pass":midWT_pass,
						"AccuModTime_pass":float(modWT_pass), "AccuMinWTime_pass":float(minWT_pass), "AccuMaxWTime_pass":float(maxWT_pass),
						#"AccuMeanWTime_fail":meanWT_fail, "AccuStdWTime_fail":stdWT_fail, "AccuMidWTime_fail":midWT_fail, 
						#"AccuModWTime_fail":float(modWT_fail), "AccuMinWTime_fail":float(minWT_fail), "AccuMaxWTime_fail":float(maxWT_fail),
					   }
			pc.judge_isinstance_numpy(sta_dict)		   
			db.Sec_sta.update_one({"gameCode":game, "sectionId":section}, {'$set': sta_dict}, upsert = True)
		