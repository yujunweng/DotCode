'''
Created on 2019年9月24日
@author: Y.J.Weng
2021/12/23 修改為多核心
'''
from pymongo import MongoClient
from multiprocessing import Process, Pool
import numpy as np
import traceback
import os
import time
import datetime
import gc
import json
import PaperCommon as pc



def main_map(section): 
	startTime = time.time()
	database = 'test'
	collection = 'Record'
	game = 'Duck'
	
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)	
	
	mode = 1
	firstrecordCount, accutimeCount = 0, 0
	
	print("%s section %d start" %(game, section)) 
	userIds = np.array(list(set([one['userId'] for one in ct.find({'gameCode':'Duck', 'sectionId':section})])))

	for id in userIds:
		id = int(id)
		record = []
		sortedRecord = []	
		tryCount = 0   	# 嘗試破關次數
		for one in ct.find({"gameCode":game, "sectionId":section, "userId":id}):
			newGameTime = one['newGameTime'] if 'newGameTime' in one.keys() else one['gameTime']	
			if 0 < newGameTime <= 57600000:
				record.append([#one['gameCode'],
							   #one['sectionId'],
							   #one['userId'],
							   one['gameStar'],
							   newGameTime,
							   one['lastUpdateTime']
							 ])  
		lenRecord = len(record)
		
		if lenRecord > 0:
			record = np.array(record)
			pc.merge_sort(record, y=2) 
			'''
			if id in [145, 647]:
				print(record)
			record = pc.bubbleSort_twoLayer(record, 2)
			if id in [145, 647]:
				print(record)
			'''
			i = 0
			accumulatedTime = 0            
			while i < lenRecord:
				#常用資料賦值，減少運算次數
				star = int(record[i][0])
				GameTime = int(record[i][1])
				updateTime = int(record[i][2])
				tryCount += 1
				GameTime_sec = GameTime/1000
				logGameTime_sec = float(np.log(GameTime_sec))
				accumulatedTime += GameTime
				accumulatedTime_sec = accumulatedTime/1000
				logAccuTime_sec = float(np.log(accumulatedTime_sec))
				correctPercentage = 0 if star == 0 else (1/tryCount)			
		
				# FirstPass直到第一次過關的所有紀錄都insert
				firstPassDict ={"gameCode":game,
								"sectionId":section,
								"userId":int(id),
								"gameStar":star,
								"gameTime":GameTime,
								"gameTime_sec":GameTime_sec,
								"logGameTime_sec":logGameTime_sec,
								"accuTime_sec":accumulatedTime_sec,
								"logAccuTime_sec":logAccuTime_sec,
								"lastUpdateTime":updateTime,
								"tryCount":tryCount,
								"correctPercentage":correctPercentage
								}
		
				pc.judge_isinstance_numpy(firstPassDict)
				if mode == 1:				
					db.FirstPass.insert_many([firstPassDict])
				elif mode == 2:
					db.FirstPass.update_one({"gameCode":game, "sectionId":section, "userId":id, "lastUpdateTime" : updateTime},{'$set':firstPassDict}, upsert=True)
				
				# FirstRecord 只 insert 第一筆紀錄
				if i == 0:
					firstRecordDict = {"gameCode":game,
										"sectionId":section,
										"userId":int(id),
										"gameStar":star,									  
										"gameTime":GameTime,  #會是修正後的gameTime
										"gameTime_sec":GameTime_sec,
										"logGameTime_sec":logGameTime_sec,
										"lastUpdateTime":updateTime
									  }
					pc.judge_isinstance_numpy(firstRecordDict)
					if mode == 1:
						db.FirstRecord.insert_many([firstRecordDict])
					elif mode == 2:
						db.FirstRecord.update_one({"gameCode":game, "sectionId":section, "userId":id},{'$set':firstRecordDict}, upsert = True)
					firstrecordCount += 1
				
				# AccuTime 只 insert 最後一筆紀錄
				if i == (lenRecord-1) or star > 0:
					wrongTime_sec = (accumulatedTime_sec-GameTime_sec) if star > 0 else accumulatedTime_sec
					accuTimeDict = {"gameCode":game,
									"sectionId":section,
									"userId":int(id),
									"gameStar":star,
									"accuTime_sec":accumulatedTime_sec,
									"logAccuTime_sec":logAccuTime_sec,
									"wrongTime_sec":wrongTime_sec,
									"logwrongTime_sec":float(np.log(wrongTime_sec)),
									"correctPercentage":correctPercentage,
									"tryCount":tryCount
								}
					
					pc.judge_isinstance_numpy(accuTimeDict)
		
					if mode == 1:					  
						db.AccuTime.insert_many([accuTimeDict])					
					elif mode == 2:
						db.AccuTime.update_one({"gameCode":game, "sectionId":section, "userId":id},{'$set':accuTimeDict}, upsert=True)
					accutimeCount += 1									
					break	
				i += 1
			#print("lenrecord", lenRecord, "i =", i,  "game", game, "section", section, "user", id)
			#print("userid: %d, section : %d have insert..." %(id, section))
	
	#檢查筆數是否正確,FirstRecord會和AccuTime相同	
	if firstrecordCount != accutimeCount:
		print("firstrecord:%d" %firstrecordCount) 
		print("accutime:%d" %accutimeCount)
			
	print("%s section %d completed, used time %d" %(game, section, endTime-startTime))	
	
	

if __name__ == '__main__':
	'''
	創建3個主要的collection - AccuTime, FirstPass, FirstRecord
	AccuTime 每一關直到過關或在該關卡最後一次遊戲為止的累計時間
	FirstPass 每一關直到破關前的遊戲記錄
	FirstRecord 每一關第1次遊戲的記錄
	'''
	print("Create 3 collections - AccuTime, FirstPass, FirstRecord")
	mode = 1 # (1)insert data (2)update data (attention:choose insert when collection is empty, it's much quick)
	cpus = os.cpu_count()
	while 1:
		useCpus = int(input("請輸入要使用的cpu數量 1 ~ {}：".format(cpus-1)))
		print("使用 {} 顆CPU".format(useCpus))
		if 1 <= useCpus <= cpus-1:
			startTime = time.time()
			
			database = 'test'
			collection = 'Record'
			game = 'Duck'
			
			db = pc.clientDB(database)
			ct = pc.clientCT(database, collection)

			db.drop_collection('AccuTime')
			db.drop_collection('FirstRecord')
			db.drop_collection('FirstPass')

			ct.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	
			maxSection = pc.max_section(game)
			maxId = pc.max_user(game)
			
			sections = [section for section in range(1, maxSection+1)]

			# 設定處理程序數量
			pool = Pool(useCpus)

			# 運行多處理程序
			pool_outputs = pool.map(main_map, sections)
	
			# 輸出執行結果
			print(pool_outputs)
			
			# 建立索引
			print("start to create index")
			db.AccuTime.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
			db.FirstRecord.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
			db.FirstPass.create_index([('gameCode', 1), ('userId', 1)])
			db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1)])
			db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
			db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1), ('lastUpdateTime', 1)])
			
			print("Indexes created!")
			
			endTime = time.time()
			pc.pass_time(startTime, endTime)	
			
			break
		else:
			print("輸入錯誤, 請重新輸入")
			continue