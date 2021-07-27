'''
Created on 2019年9月24日
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


if __name__ == '__main__':
	'''
	創建3個主要的collection - AccuTime, FirstPass, FirstRecord
	AccuTime計算累計時間的正確率、log時間、Z值
	FirstPass每一關直到破關前的遊戲記錄
	FirstRecord每一關第1次遊戲的記錄
	'''
	print("Create 3 collections - AccuTime, FirstPass, FirstRecord")
	mode = 1 # (1)insert data (2)update data (attention:choose insert when collection is empty, it's much quick)
	
	ct = pc.clientCT('dotCode', 'Record')
	firstrecord_count, accutime_count = 0, 0
	for section in range(1, maxSection+1):
		print("%s section：%d" %(game, section)) 
		for id in range(1, maxId):    
			record = []
			sortedRecord = []
			try_count = 0   	# 嘗試破關次數
			for one in ct.find({"gameCode":"Duck", "sectionId":section, "userId":id}):
				newGameTime = one['newGameTime'] if 'newGameTime' in one.keys() else one['gameTime']	
				
				if 0 < newGameTime <= 57600000:
					record.append([#one['gameCode'],
								   #one['sectionId'],
								   #one['userId'],
								   one['gameStar'],
								   newGameTime,
								   one['lastUpdateTime']
								 ])  
			len_record = len(record)

			if len_record > 0:
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
				while i < len_record:
					#常用資料賦值，減少運算次數
					star = int(record[i][0])
					GameTime = int(record[i][1])
					updateTime = int(record[i][2])
					try_count += 1
					GameTime_sec = GameTime/1000
					logGameTime_sec = float(np.log(GameTime_sec))
					accumulatedTime += GameTime
					accumulatedTime_sec = accumulatedTime/1000
					logAccuTime_sec = float(np.log(accumulatedTime_sec))
					correctPercentage = 0 if star == 0 else (1/try_count)			
					
					# FirstPass直到第一次過關的所有紀錄都insert
					firstPass_dict ={"gameCode":game,
									 "sectionId":section,
									 "userId":int(id),
									 "gameStar":star,
									 "gameTime":GameTime,
									 "gameTime_sec":GameTime_sec,
									 "logGameTime_sec":logGameTime_sec,
									 "accuTime_sec":accumulatedTime_sec,
									 "logAccuTime_sec":logAccuTime_sec,
									 "lastUpdateTime":updateTime,
									 "tryCount":try_count,
									 "correctPercentage":correctPercentage
									}
					
					pc.judge_isinstance_numpy(firstPass_dict)
					if mode == 1:				
						db.FirstPass.insert_many([firstPass_dict])
					elif mode == 2:
						db.FirstPass.update_one({"gameCode":game, "sectionId":section, "userId":id, "lastUpdateTime" : updateTime},{'$set':firstPass_dict}, upsert = True)
					
					# FirstRecord 只 insert 第一筆紀錄
					if i == 0:
						firstRecord_dict = {"gameCode":game,
											"sectionId":section,
											"userId":int(id),
											"gameStar":star,									  
											"gameTime":GameTime,  #會是修正後的gameTime
											"gameTime_sec":GameTime_sec,
											"logGameTime_sec":logGameTime_sec,
											"lastUpdateTime":updateTime
											}
						pc.judge_isinstance_numpy(firstRecord_dict )
						if mode == 1:
							db.FirstRecord.insert_many([firstRecord_dict])
						elif mode == 2:
							db.FirstRecord.update_one({"gameCode":game, "sectionId":section, "userId":id},{'$set':firstRecord_dict}, upsert = True)
						firstrecord_count += 1
					
					# AccuTime 只 insert 最後一筆紀錄
					if i == (len_record-1) or star > 0:
						wrongTime_sec = (accumulatedTime_sec-GameTime_sec) if star > 0 else accumulatedTime_sec
						accuTime_dict ={"gameCode" : game,
										"sectionId" : section,
										"userId" : int(id),
										"gameStar" : star,
										"accuTime_sec" : accumulatedTime_sec,
										"logAccuTime_sec" : logAccuTime_sec,
										"wrongTime_sec" : wrongTime_sec,
										"logwrongTime_sec" : float(np.log(wrongTime_sec)),
										"correctPercentage" : correctPercentage,
										"tryCount" : try_count
									   }
						firstPass_dict = {"maxTryCount":tryCount}
						
						pc.judge_isinstance_numpy(accuTime_dict)
						pc.judge_isinstance_numpy(firstPass_dict)
						
						db.FirstPass.update_many({"gameCode":game, "sectionId":section, "userId":id},{'$set':firstPass_dict}, upsert = True)
						if mode == 1:					  
							db.AccuTime.insert_many([accuTime_dict])					
						elif mode == 2:
							db.AccuTime.update_one({"gameCode":game, "sectionId":section, "userId":id},{'$set':accuTime_dict}, upsert = True)
						accutime_count += 1									
						break	
					i += 1
				#print("lenrecord", len_record, "i =", i,  "game", game, "section", section, "user", id)
		
		#檢查筆數是否正確,FirstRecord會和AccuTime相同	
		if firstrecord_count != accutime_count:
			print("firstrecord:%d" %firstrecord_count) 
			print("accutime:%d" %accutime_count)

	# 建立索引
	print("start to create index")
	db.AccuTime.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.FirstRecord.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.FirstPass.create_index([('gameCode', 1), ('userId', 1)])
	db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1)])
	db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1), ('lastUpdateTime', 1)])
	#print("userid: %d, section : %d have insert..." %(id, section))
	print("Indexes created!")