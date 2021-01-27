'''
Created on 2019年9月24日
20191003    增加時間Z值的計算
20191005    增加畫圖
20191006    修改功能順序，增加insert第1次遊戲的紀錄
20191006    移除畫圖到plot.py
20200314    把計算Accumulated Time和Z值，及insert Elo值合併在選項3
@author: 翁毓駿
'''
from pymongo import MongoClient
import numpy as np
import pandas as pd
import traceback
import os
import time
import datetime
import gc
import json

def clientDB(database):
	client = MongoClient('localhost', 27017)
	db = client[database]
	return db

def clientCT(database, collection):
	ct = clientDB(database)[collection]
	return ct

def bubbleSort(x, y = 0):	#大的往後排
	matrix = []
	i = len(x)-1
	while (i > 0):
		j = 0
		while (j < i):	
			if (x[j][y] > x[j+1][y]):
				matrix = x[j+1]
				x[j+1] = x[j]
				x[j] = matrix
			j += 1
		i -= 1
	return x	
			
def bubbleSort2(x):
	matrix = []
	i = len(x)-1
	while (i > 0):
		j = 0
		while (j < i):
			if (x[j] > x[j+1]):
				matrix = x[j+1]
				x[j+1] = x[j]
				x[j] = matrix
			j += 1
		i -= 1
	return x
	
def Merge_Sort(array, y):
	if len(array) > 1:
		mid = len(array) // 2
		left_array = array[:mid]
		right_array = array[mid:]
		
		Merge_Sort(left_array, y)
		Merge_Sort(right_array, y)
		
		right_index = 0
		left_index = 0
		merged_index = 0
		while right_index < len(right_array) and left_index < len(left_array):
			if(right_array[right_index][y] < left_array[left_index][y]):
				array[merged_index] = right_array[right_index]
				right_index = right_index + 1
			else:
				array[merged_index] = left_array[left_index]
				left_index = left_index + 1
			merged_index = merged_index + 1
		while right_index < len(right_array):
			array[merged_index] = right_array[right_index]
			right_index = right_index + 1
			merged_index = merged_index + 1
		while left_index < len(left_array):
			array[merged_index] = left_array[left_index]
			left_index = left_index + 1
			merged_index = merged_index + 1
			
def writeLog(recordPath, *massage):
	try:
		fout = open(recordPath, "a")
	except:
		traceback.print_exc()
	for mas in massage:    
		mas = str(mas)
		fout.write(mas)
		fout.write("\n")
	fout.close()

def writeLog2(recordPath, fileName, *massage):
	try:
		if not(os.path.isdir(recordPath)):
			os.makedirs(recordPath)
		file = os.path.join(recordPath, fileName) 	
		fout2 = open(file, "a+")
		for mas in massage:
			mas = str(mas)
			fout2.write(mas+"\n")
		fout2.close()
	except:
		traceback.print_exc()	

def columnFunc(j, k, num):
	kList = []
	for i in range(j,k):
		kList.append(num)    
	return kList 

def Add_Difficulty(game, maxsection):
	database = 'dotCode'
	collection = 'Sec_sta'
	ct = clientCT(database, collection)
	
	Item_Difficulty = []
	Difficulty_Degree = []

	for section in range(1, maxsection+1):
		for one in ct.find({'gameCode': game, 'sectionId':section}):
			Item_Difficulty.append(one['difficulty'])
			Difficulty_Degree.append(one['difficultyDegree'])
	return Item_Difficulty, Difficulty_Degree

def descript_statis(array1, array2):
	meanT = np.mean(array2)
	midT = np.median(array1)
	modT = np.argmax(np.bincount(array1))
	minT = np.amin(array1)
	maxT = np.amax(array1)
	stdT = np.std(array2)
	return meanT, midT, modT, minT, maxT, stdT

def mean_and_std(array1, array2, array3):
	meanT = np.mean(array1)
	meanT_pass = np.mean(array2)
	meanT_fail = np.mean(array3)
	
	stdT = np.std(array1)
	stdT_pass = np.std(array2)
	stdT_fail = np.std(array3)
	return meanT, meanT_pass, meanT_fail, stdT, stdT_pass, stdT_fail

### 主程式
if __name__ == '__main__':
	value = int(input('''(1)Insert Origianal Data or fix error time data 
(2)Create 3 collections - AccuTime, FirstPass, FirstRecord
(3)Calculate Z of accumulated time and insert Elo from Elo to AccuTime
(4)Calculate Z of of game time of the first record and insert Elo from Elo to FirstRecord
(7)Insert section statistic information to Sec_sta\n:'''))
	startTime = time.time()

	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數
	gameCode = ['Maze', 'Duck']
	degree = [-3, -2, -1, 0, 1, 2]
	game = 'Duck'
	maxSection = 60 if game == 'Duck' else 40
	maxId = 679000
	
	if value == 1:	# 每筆資料insert
		connection = MongoClient('localhost', 27017)
		print(connection.list_database_names())  #Return a list of db, equal to: > show dbs
		db = connection["DATA"]
		
		choice = int(input("(1)insert one data at a time \n(2)import collection\n(3)fix wrong time record\n(4)insert vids time：\n"))
		startTime = time.time()
		
		if choice == 1:
			for c in db.list_collection_names():
				ct = db[c]		

				addCount = 0
				mazeCount = 0
				duckCount = 0
				str_collection = str(c) 
				CTN = str_collection[0:str_collection.find('_')]

				tran_startTime = datetime.datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S")	

				for post in ct.find():
					#print(post)
					collectSeq = str_collection[str_collection.find('_')+1:len(str_collection)]	#抓原始載入的集合序號
					post['oriCollect'] = collectSeq		#把序號加入post裡

					ts = (post['lastUpdateTime'])/1000		#把lastUpdateTime轉成西元時間				#print(ts)
					st = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
					#print(st)
					post['YYMMDD'] = st
					
					post2 = post
					#print(post2)

					if post['gameCode'] == 'Maze' :
						if (CTN == 'dotCodeStar'):
							db.dotCodeStar_Maze.insert(post2, w = 1, j = True, wtimeout = 1000)
						elif (CTN == 'dotCodeRecord'):
							db.dotCode.insert(post2, w = 1, j = True, wtimeout = 1000)
						mazeCount += 1

					elif post['gameCode'] == 'Duck':
						if CTN == 'dotCodeStar':
							db.dotCodeStar_Duck.insert(post2, w=1, j = True, wtimeout = 1000)
						elif CTN == 'dotCodeRecord':
							db.dotCode.insert(post2, w=1, j = True, wtimeout = 1000)
						duckCount += 1			

					addCount += 1
					#print("正在寫入第 %d 筆資料" %addCount)
				
				if addCount > 0:
					logPath = "D:\\paper\\practice\\practice file\\record\\InsertLog.txt"
					logContent = "開始時間：%s\n%s寫入完成!\nMaze寫入 %d 筆!\nDuck寫入 %d 筆!\n總計 %d 筆File!\n結束時間：%s\n" %(tran_startTime, collection, mazeCount, duckCount, addCount, tran_endTime)

					writeLog(logPath, logContent)
					print(logContent)

		elif choice == 2:
			readpath = "D:\\MongoDB\\Server\\4.0\\data\\DATA"
			files = os.listdir(readpath) 
			for file in files:
				if (file[:13] == "dotCodeRecord"):
					fileReadpath = os.path.join(readpath, file)
					#檔案(非資料夾)   
					with open(fileReadpath, encoding='UTF-8') as f:
						file_data = json.load(f)

					# if pymongo < 3.0, use insert()
					#collection_currency.insert(file_data)
					# if pymongo >= 3.0 use insert_one() for inserting one document
					#collection_currency.insert_one(file_data)
					# if pymongo >= 3.0 use insert_many() for inserting many documents
					db.Record.insert_many(file_data)
			connection.close()
		 
		elif choice == 3:
			# 尋找此ID的所有遊戲紀錄，將連續的兩個遊戲紀錄的lastUpdateTime相減
			# Find all record of this userId and subtract the lastUpdateTime of two consecutive game records
			# 算出lastUpdateTime較後面的紀錄的gameTime
			# to calculate gameTime of later record
			
			#connect to database
			client = MongoClient()
			database = 'dotCode'
			collection = 'Record'
			ct = client[database][collection]
			
			path = "D:\\paper\\practice\\practice file\\record\\ErrorProcess"
			restoreFile = "restore.csv"
			thefirstFile = "thefirst.csv"

			if os.path.isfile(os.path.join(path, restoreFile)):
				os.remove(os.path.join(path, restoreFile))
			if os.path.isfile(os.path.join(path, thefirstFile)):
				os.remove(os.path.join(path, thefirstFile))

			restore, theFirst, count, normal = 0
			errorTime = []
			limitTime = 1200000
			
			##建立索引
			print("start to create index...")
			db.Record.create_index([('gameCode', 1), ('userId', 1)])
			db.Record.create_index([('gameCode', 1), ('gameTime', 1)])
			db.Record.create_index([('gameTime', 1)])
			print("Indexes created!")
			
			#find abnormal of gameTime and sort by lastUpdateTime d 
			print("start to find abnormal game time") 
			#timeQuery = {"$or":[{"gameTime":None},{"gameTime":{"$gt":limitTime}},{"gameTime":{"$lte":0}}]}
			
			for one in ct.find({"gameCode":'Duck', "accumulatedTime_sec":{'$lte':6}, "gameStar":{'$gt':0}}):
				count += 1
				errorTime.append(one['userId'])
			
			for one in ct.find({"gameCode":"Duck", "gameTime":{"$gt":limitTime}}):
				count += 1
				errorTime.append(one['userId'])
			
			print("length of errorTime:", len(errorTime))
			print("length of set errorTime", len(set(errorTime)))
			
			#print("errorTime index:", errorTime.index)
			#errorTime = sorted(set(errorTime), key = errorTime.index)
			errorTime = set(errorTime)
			findEndTime = time.time()	
			#os.system("pause")
			
			#find userId in the list
			collection = 'Record'
			ct = client[database][collection]
			peo = len(errorTime)
			for id in errorTime:
			#for id in range(457401, 457402):	
				record = []
				for one in ct.find({"userId":id}):
					record.append([one['lastUpdateTime'], one['gameTime'], one['userId'] ,one['_id'], one['gameCode'], one['gameStar']])		
				record = bubbleSort(record, 0)
				#Merge_Sort(record, 0)
				x = len(record)
				print(record)
				os.system("pause")
				i = 0
				while (i < x):
					newGameTime = 0
					if(record[i][1] <= 0 or (record[i][4] == 'Duck' and record[i][1] > limitTime)):	#gameTime lower than zero or gameTime > 20 minutes
						if 0 < i < len(record):		#不是第1筆資料 
							newGameTime = record[i][0] - record[i-1][0]
							if (record[i][1] > 0):
								if(newGameTime < record[i][1]): #新gameTime比原gameTime小
									ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime": newGameTime}})
									record[i].append(newGameTime)
									restore += 1
									#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", newGameTime)
									writeLog2(path, restoreFile, record[i], record[i-1])
								else:
									normal += 1
								
							else:
								ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime":newGameTime}})
								record[i].append(newGameTime)
								restore += 1
								#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", newGameTime)
								writeLog2(path, restoreFile, record[i], record[i-1])

						else:#if the record is the first record of the userId in the collection, then we can't calculate the gameTime 
							theFirst += 1
							if(record[i][1] <= 0):
								ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime":0}})
								#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", 0, "the first")
							else:
								ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime":record[i][1]}})
								#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", newGameTime, "the first")
							
							record[i].append(newGameTime)
							if (len(record) == 1):
								writeLog2(path, thefirstFile, "the first", record[i], "沒有後一筆")
							else:
								writeLog2(path, thefirstFile, "the first", record[i], record[i+1]) #沒有前一筆資料,所以記後一筆對照
					'''				
					if (record[i][4] == 'Duck' and 0 < record[i][1] <= limitTime and record[i][5] > 0):
						if (0 < i < len(record)):		#不是第1筆資料 
							newGameTime = record[i][0] - record[i-1][0]
							if(newGameTime > record[i][1]): #新gameTime比原gameTime大
								ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime": newGameTime}})
								record[i].append(newGameTime)
								restore += 1
								#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", newGameTime)
								writeLog2(path, restoreFile, record[i], record[i-1])
							else:
								normal += 1				
					'''
					i += 1	
				peo -= 1
				print("剩下人數:", peo)
			
			print("有問題人數:%d" %count)
			massage = "修復筆數:%d, 無法修復:%d, 正常資料:%d" %(restore, theFirst, normal)
			print(massage)
			print("搜尋時間 %f秒" %(findEndTime - startTime))
			
		elif choice == 4:
			db = connection["dotCode"]
			ct = db['Record']
			print("insert vids time...")
			for post in ct.find():
				ts = (post['lastUpdateTime'])/1000		#把lastUpdateTime轉成西元時間				#print(ts)
				st = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")		
				post2 = {'YYMMDD':st}
				ct.update_one({'_id':post['_id']}, {'$set':post2}, upsert=True)


	if(value == 2):
		#創建3個主要的collection - AccuTime, FirstPass, FirstRecord
		#AccuTime計算累計時間的正確率、log時間、Z值
		#FirstPass每一關直到破關前的遊戲記錄
		#FirstRecord每一關第1次遊戲的記錄		
		mode = 1 # (1)insert data (2)update data (attention:choose insert when collection is empty, it's much quick)
		print("Create 3 collections - AccuTime, FirstPass, FirstRecord")
		choice = input("是否開始?Y/N")  
		database = 'dotCode'
		collection = 'Record'
		db = connection[database]
		ct = clientCT(database, collection)
		if choice == 'Y':
			firstrecord_count = 0
			accutime_count = 0	
			
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
						Merge_Sort(record, y=2) 
						
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
							'''
							# FirstPass第一次過關前的所有紀錄都insert
							firstPass_dict =[{"gameCode" : game,
											 "sectionId" : section,
											 "userId" : int(id),
											 "gameStar" : star,
											 "gameTime" : GameTime,
											 "gameTime_sec" : GameTime_sec,
											 "logGameTime_sec" : logGameTime_sec,
											 "accuTime_sec" : accumulatedTime_sec,
											 "logAccuTime_sec" : logAccuTime_sec,
											 "lastUpdateTime" : updateTime,
											 "tryCount" : try_count,
											 "correctPercentage" : correctPercentage
											}]
							
							for items in firstPass_dict.items():
								#print(items)
								if isinstance(items[1], np.int64):
									print(items[0])
							s =input("")
							
							if mode == 1:				
								db.FirstPass.insert_many(firstPass_dict)
							elif mode == 2:
								db.FirstPass.update_one({"gameCode":game, "sectionId":section, "userId":id, "lastUpdateTime" : updateTime},{'$set':firstPass_dict}, upsert = True)
							
							# FirstRecord 只 insert 第一筆紀錄
							if i == 0:
								firstRecord_dict = [{"gameCode":game,
													"sectionId":section,
													"userId":int(id),
													"gameStar":star,									  
													"gameTime":GameTime,  #會是修正後的gameTime
													"gameTime_sec":GameTime_sec,
													"logGameTime_sec":logGameTime_sec,
													"lastUpdateTime":updateTime
													}]
								if mode == 1:
									db.FirstRecord.insert_many(firstRecord_dict)
								elif mode == 2:
									db.FirstRecord.update_one({"gameCode":game, "sectionId":section, "userId":id},{'$set':firstRecord_dict}, upsert = True)
								firstrecord_count += 1
							'''
							# AccuTime 只 insert 最後一筆紀錄
							if i == (len_record-1) or star > 0:
								wrongTime_sec = accumulatedTime_sec-GameTime_sec if star > 0 else accumulatedTime_sec
								accuTime_dict =[{"gameCode" : game,
												"sectionId" : section,
												"userId" : int(id),
												"gameStar" : star,
												"accuTime_sec" : accumulatedTime_sec,
												"logAccuTime_sec" : logAccuTime_sec,
												"wrongTime_sec" : wrongTime_sec,
												"logwrongTime_sec" : float(np.log(wrongTime_sec)),
												"correctPercentage" : correctPercentage,
												"tryCount" : try_count
											   }]
								if mode == 1:					  
									db.AccuTime.insert_many(accuTime_dict)
								elif mode == 2:
									db.AccuTime.update_one({"gameCode":game, "sectionId":section, "userId":id},{'$set':accuTime_dict}, upsert = True)
								accutime_count += 1									

								break	
							i += 1
						#print("lenrecord", len_record, "i =", i,  "game", game, "section", section, "user", id)
				
				#檢查筆數是否正確,FirstRecord會和AccuTime相同	
				if(firstrecord_count != accutime_count):
					print("firstrecord:%d" %firstrecord_count) 
					print("accutime:%d" %accutime_count)

				endTime = time.time()		
				print("use time", endTime-startTime, "秒")			
			
		##建立索引
		print("start to create index")
		db.AccuTime.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
		db.FirstRecord.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
		db.FirstPass.create_index([('gameCode', 1), ('userId', 1)])
		db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1)])
		db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
		db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1), ('lastUpdateTime', 1)])
		#print("userid: %d, section : %d have insert..." %(id, section))
		print("Indexes created!")
			
	if (value == 3):
		step = int(input('''(1)calaulate Z of accumulated time and log accumulated time\n(2)insert Elo from PeoElo\n：'''))
		database = 'dotCode'
		db = clientDB(database)
		if(step == 1):
			###calaulate Z of accumulated time and log accumulated time
			collection = 'AccuTime'
			ct = clientCT(database, collection)
			
			ct.create_index([('gameCode', 1), ('sectionId', 1)])
			ct.create_index([('gameCode', 1), ('accumulatedTime_sec', 1)])
			
			for section in range(1, maxSection+1):
				peo_all = [] # 有紀錄的玩家
				peo_pass = [] # 過關的玩家 
				peo_fail = [] # 沒過關的玩家	
				log_peo_all, log_peo_pass, log_peo_fail = [], [], []
				peo_origin_all, peo_origin_pass, peo_origin_fail = [], [], []				
				
				meanT, meanT_pass, meanT_fail = None, None, None	# 平均數
				midT, midT_pass, midT_fail = None, None, None		# 中位數
				modT, modT_pass, modT_fail = None, None, None		# 眾數
				maxT, maxT_pass, maxT_fail = None, None, None		# 最大
				minT, minT_pass, minT_fail = None, None, None		# 最小
				stdT, stdT_pass, stdT_fail = None, None, None 		# 標準差
				
				sta_dict = {}
				
				for one in ct.find({"gameCode": game, "sectionId":section}):
					# 只有計算平均數與標準差才用origin
					accumulatedTime_sec = int(one['accuTime_sec'])
					
					peo_all.append(accumulatedTime_sec)
					peo_origin_all.append(one['accuTime_sec'])
					log_peo_all.append(one['logAccuTime_sec'])
					
					if one['gameStar'] > 0:		# 只算有過關
						peo_pass.append(accumulatedTime_sec)
						peo_origin_pass.append(one['accuTime_sec'])
						log_peo_pass.append(one['logAccuTime_sec'])
					else:		# 只算沒過關
						peo_fail.append(accumulatedTime_sec)
						peo_origin_fail.append(one['accuTime_sec'])
						log_peo_fail.append(one['logAccuTime_sec'])
				
				if len(peo_all) > 0:
					meanT, midT, modT, minT, maxT, stdT = descript_statis(peo_all, peo_origin_all)
					if len(peo_pass) > 0:
						meanT_pass, midT_pass, modT_pass, minT_pass, maxT_pass, stdT_pass = descript_statis(peo_pass, peo_origin_pass)
					if len(peo_fail) > 0:	
						meanT_fail, midT_fail, modT_fail, minT_fail, maxT_fail, stdT_fail = descript_statis(peo_fail, peo_origin_fail)				
					
					print("section:%d, 人數:%d, 平均時間:%f, 中位數時間:%f, 過關人數:%d, 過關平均時間:%f, 過關中位數時間:%f" %(section, len(peo_all), meanT, midT, len(peo_pass), meanT_pass, midT_pass))
					print("全部標準差 = ", stdT, "過關玩家標準差 = ", stdT_pass)

					print("開始計算Z值\n")
					log_meanT, log_meanT_pass, log_meanT_fail, log_stdT, log_stdT_pass, log_stdT_fail = mean_and_std(log_peo_all, log_peo_pass, log_peo_fail)
					ZTime, ZTime_pass, ZTime_fail = None, None, None
					ZLogTime, ZLogTime_pass, ZLogTime_fail = None, None, None
					Z_dict, Z_pass_dict, Z_fail_dict = {}, {}, {}
					
					for two in ct.find({"gameCode":game, "sectionId":section}): 
						ZTime = (two['accuTime_sec'] - meanT) / stdT
						ZLogTime = (two['logAccuTime_sec'] - log_meanT) / log_stdT
						Z_dict = {"ZTime":ZTime,
								  "ZLogTime":ZLogTime
								 }
						db.AccuTime.update_one({"_id":two['_id']}, {'$set':Z_dict}, upsert = True)
						countInsert += 1
						
						# 有過關
						if two['gameStar'] > 0:
							ZTime_pass = (two['accuTime_sec'] - meanT_pass) / stdT_pass
							ZLogTime_pass = (two['logAccuTime_sec'] - log_meanT_pass) / log_stdT_pass
							Z_pass_dict = {"ZTime_pass":ZTime_pass,
										   "ZLogTime_pass":ZLogTime_pass
										  }
							db.AccuTime.update_one({"_id":two['_id']}, {'$set': Z_pass_dict}, upsert = True)	
						else:
							ZTime_fail = (two['accuTime_sec'] - meanT_fail) / stdT_fail
							ZLogTime_fail = (two['logAccuTime_sec'] - log_meanT_pass) / log_stdT_pass
							Z_fail_dict = {"ZTime_fail":ZTime_fail,
										   "ZLogTime_fail":ZLogTime_fail
										  }
							db.AccuTime.update_one({"_id":two['_id']}, {'$set': Z_fail_dict}, upsert = True)
							
					sta_dict = {"AccuMeanTime":meanT, "AccuStdTime":stdT, "AccuMidTime":midT, "AccuModTime":float(modT), "AccuMinTime":float(minT), "AccuMaxTime":float(maxT),	
								"AccuMeanTime_pass":meanT_pass, "AccuStdTime_Pass":stdT_pass, "AccuMidTime_Pass":midT_pass,
								"AccuModTime_pass":float(modT_pass), "AccuMinTime_Pass":float(minT_pass), "AccuMaxTime_Pass":float(maxT_pass),
								"AccuMeanTime_fail":meanT_fail, "AccuStdTime_Fail":stdT_fail, "AccuMidTime_Fail":midT_fail, 
								"AccuModTime_fail":float(modT_fail), "AccuMinTime_Fail":float(minT_fail), "AccuMaxTime_Fail":float(maxT_fail),		
							   }
					for items in sta_dict.items():
						#print(items)
						if isinstance(items[1], np.int32):
							print(items[0])
							s =input("")		   
					db.Sec_sta.update_one({"gameCode":game, "sectionId":section}, {'$set': sta_dict}, upsert = True)
						
		elif(step == 2):	# Insert Elo
			collection = 'PeoElo'
			ct = clientCT(database, collection)

			ct.create_index([('gameCode', 1), ('userId', 1)])
			db.AccuTime.create_index([('gameCode', 1), ('userId', 1), ('sectionId', 1)])
			
			print("Insert Elo to AccuTime...")
			for id in range(1, maxId):
				for four in ct.find({"gameCode":game, "userId":id}):
					for section in range(1, maxSection+1):
						if(section > four['maxSection']):
							break
						else:
							if("section%d_elo" %section in four.keys()):
								elo = four["section%d_elo" %section]
								#print(elo)
								elo_dict = {"elo": elo}
								db.AccuTime.update_one({"gameCode": game, "userId":id, "sectionId":section}, {'$set': elo_dict}, upsert = True)
								countInsert += 1
								#print("section:", section, "user:", id, "elo:", elo)
							else: 
								pass

	
	if(value == 4):	# 計算 FirstRecord 中 gameTime 及Log gameTime 的Z值   
		step = int(input("(1)Insert Score\n(2)Calaulate Z of game time, log game time\n(3)Inspect empty of Z-Score, Z-Time, Z-LogTime\n："))
		
		database = 'dotCode'
		collection = 'FirstRecord'
		ct = clientCT(database, collection)
		
		ct.create_index([('gameCode', 1), ('sectionId', 1)])

		if step == 1:	# 插入score, Score的計算方式是官方的計算方式, 詳情見官方說明書
			for one in ct.find({"gameCode":game}):
				score_dict = {"score":(one['sectionId']+9) * one['gameStar']}
				db.FirstRecord.update_one({'_id':one['_id']}, {'$set': score_dict}, upsert = True)
				countInsert += 1
		
		elif step == 2:		# 各種敘述性統計資料 (gameTime已經是除錯過的)
			print("計算各種敘述性統計資料 (gameTime已經是除錯過的)")
			for section in range(1, maxSection+1):
				peo_all, peo_pass, peo_fail = []
				log_peo_all, log_peo_pass, log_peo_fail = []
				
				meanT, meanT_pass, meanT_fail = None	# 平均數
				midT, midT_pass, midT_fail = None		# 中位數
				modT, modT_pass, modT_fail = None		# 眾數
				maxT, maxT_pass, maxT_fail = None		# 最大
				minT, minT_pass, minT_fail = None		# 最小
				stdT, stdT_pass, stdT_fail = None 		# 標準差				
				
				sta_dict = {}
				
				for one in ct.find({"gameCode":game, "sectionId":section}):
					peo_all.append(one['gameTime_sec'])
					log_peo_all.append(one['logGameTime_sec'])
					if one['gameStar'] > 0:
						peo_pass.append(one['gameTime_sec'])
						log_peo_pass.append(one['logGameTime_sec'])
					else:
						peo_fail.append(one['gameTime_sec'])
						log_peo_fail.append(one['logGameTime_sec'])
				
				if len(peo_all) > 0:
					meanT, midT, modT, minT, maxT, stdT = descript_statis(peo_all, peo_origin_all)
					if len(peo_pass) > 0:
						meanT_pass, midT_pass, modT_pass, minT_pass, maxT_pass, stdT_pass = descript_statis(peo_pass, peo_origin_pass)
					if len(peo_fail) > 0:	
						meanT_fail, midT_fail, modT_fail, minT_fail, maxT_fail, stdT_fail = descript_statis(peo_fail, peo_origin_fail)				
					print("section:%d, 人數:%d, 平均時間:%f, 過關人數:%d, 過關平均時間:%f" %(section, len(peo_all), meanT, len(peo_pass), meanT_pass))
					
					# ZTime值
					ZTime, ZTime_pass, ZTime_fail = 999
					ZLogTime, ZLogTime_pass, ZLogTime_fail = -999
					Z_dict, Z_pass_dict, Z_fail_dict = {}
					log_meanT, log_meanT_pass, log_meanT_fail, log_stdT, log_stdT_pass, log_stdT_fail = mean_and_std(log_peo_all, log_peo_pass, log_peo_fail)
					
					print("開始計算Z值\n")
					for two in ct.find({"gameCode": game, "sectionId":section}):
						ZTime = (two['gameTime_sec'] - meanT) / stdT
						ZLogTime = (two['logGameTime_sec'] - log_meanT) / log_stdT
						Z_dict = {"ZTime":ZTime,
								  "ZLogTime":ZLogTime
								 }
						db.FirstRecord.update_one({'_id':two['_id']},{'$set':Z_dict}, upsert = True)
						countInsert += 1			
						
						# 有過關
						if two['gameStar'] > 0:
							ZTime_pass = (two['gameTime_sec'] - meanT_pass) / stdT_pass
							ZLogTime_pass = (two['logGameTime_sec'] - log_meanT_pass) / log_stdT_pass
							Z_pass_dict = {"ZTime_pass":ZTime_pass,
										   "ZLogTime_pass":ZLogTime_pass
										  }					
							db.FirstRecord.update_one({'_id':two['_id']},{'$set':Z_pass_dict}, upsert = True)					
						else:
							ZTime_fail = (two['gameTime_sec'] - meanT_fail) / stdT_fail
							ZLogTime_fail = (two['logGameTime_sec'] - log_meanT_fail) / log_stdT_fail
							Z_fail_dict = {"ZTime_fail":ZTime_fail,
										   "ZLogTime_fail":ZLogTime_fail
										  }
							db.FirstRecord.update_one({"_id":two['_id']}, {'$set': Z_fail_dict}, upsert = True)
								
					sta_dict = {"FirstMeanTime":meanT, "FirstStdTime":stdT, "FirstMidTime":midT, "FirstModTime":modT, "FirstMinTime":minT, "FirstMaxTime":maxT,	
								"FirstMeanTime_pass":meanT_pass, "FirstStdTime_Pass":stdT_pass, "FirstMidTime_Pass":midT_pass,
								"FirstModTime_pass":modT_pass, "FirstMinTime_Pass":minT_pass, "FirstMaxTime_Pass":maxT_pass,
								"FirstMeanTime_fail":meanT_fail, "FirstStdTime_Fail":stdT_fail, "FirstMidTime_Fail":midT_fail, 
								"FirstModTime_fail":modT_fail, "FirstMinTime_Fail":minT_fail, "FirstMaxTime_Fail":maxT_fail}	
					db.Sec_sta.update_one({"gameCode":game, "sectionId":section}, {'$set':sta_dict}, upsert = True)		   
		
		elif step == 3:	# 檢查Z值是否NULL
			ct.create_index([('ZTime', 1)])
			ct.create_index([('ZLogTime', 1)])
			for three in ct.find():
				if(three['ZTime'] not in three.keys() or three['ZLogTime'] not in three.keys()):
					print("lack key", three.keys())


	if (value == 7):	# Insert section statistic information(Sec_sta)
		step = int(input("""1.amount of people of get how many stars in every section
2.base on the 30th of spent time until pass the section to calculate mutiple of use time of every sections
3.Degree of difficulty of every sections\n:"""))   
		#connection = MongoClient('localhost', 27017)
		#print(connection.list_database_names())  #Return a list of db, equal to: > show dbs
		#print(db.list_collection_names())        #Return a list of collections in 'testdb1'
		database = 'dotCode'
		db = clientDB(database)
		if step == 1:
			if 'Sec_sta' in db.list_collection_names():   # Check if collection "posts"
				collection = db['Sec_sta']
				print(collection.estimated_document_count())    # exists in db (testdb1)
				#collection.drop()	# Delete(drop) collection named 'posts' from db
				#print("drop collection %s" %str(collection))
			
			collection = 'AccuTime'
			ct = clientCT(database, collection)
			
			for section in range(1, maxSection+1):
				print("collcting data of %s section %d..." %(game, section))
				correctPercentage, totalSectionCorrect = 0, 0
				zeroStar, oneStar, twoStar, threeStar, fourStar = 0, 0, 0, 0, 0
				peo = 0 # 因為要算每關人數, 所以要重置為0
				for one in ct.find({"gameCode": game, "sectionId" : section}):
					if(one['gameStar'] == 0):
						zeroStar += 1
					elif(one['gameStar'] == 1):
						oneStar += 1
					elif(one['gameStar'] == 2):
						twoStar += 1
					elif(one['gameStar'] == 3):
						threeStar += 1
					elif(one['gameStar'] == 4):
						fourStar += 1
					totalSectionCorrect += (one['correctPercentage'])
					peo += 1
				
				if peo > 0:
					correctPercentage = totalSectionCorrect/peo
					section_dict =  {"gameCode" : game,
									 "sectionId" : section,
									 "peo" : peo,
									 "peo_pass" :oneStar+twoStar+threeStar+fourStar,
									 "zeroStar" : zeroStar,
									 "oneStar" : oneStar,
									 "twoStar" : twoStar,
									 "threeStar" : threeStar,
									 "fourStar" : fourStar,
									 "correctPercentage" : correctPercentage
									}
					db.Sec_sta.update_one({'gameCode':game, 'sectionId':section},{'$set': section_dict}, upsert = True)
					countInsert += 1

		elif step == 2:
			collection = 'Sec_sta'
			ct = clientCT(database, collection)
		
			time_List = []
			ntime_List = []
			base = 0
			for two in ct.find():
				time_List.append(two['avgTime'])

			ntime_List = bubbleSort2(time_List)    
			base = ntime_List[29]   #取排序後的第30個位置作為基準，中間值

			i = 0
			while i < len(time_List):
				print(i+1, "ntime_List:", ntime_List[i])
				i += 1

			tofTime = 0
			times_dict = {}
			for section in range(1, maxSection+1):
				for three in ct.find({"sectionId":section}):
					tofTime = three['avgTime']/base  #計算倍數
					times_dict = {"times" : tofTime}
					db.Sec_sta.update_one({'_id':three['_id']}, {'$set': times_dict}, upsert = True)
					countInsert += 1

		elif step== 3:	#區分關卡難度等級 
			collection = 'Sec_sta'
			db = clientDB(database)
			ct = clientCT(database, collection)

			item_difficulty = 0
			count = 0

			for section in range(1, maxSection+1):
				for one in ct.find({"gameCode": game, "sectionId" : section}):
					item_difficulty += one['difficulty']
					count += 1
			avgDifficulty = item_difficulty/count

			x = 0
			y = 0
			for section in range(1, maxSection+1):
				for one in ct.find({"gameCode":game, "sectionId":section}):
					x += (one['difficulty'] - avgDifficulty)**2
					y += 1
			Variation = x/y
			Standard_deviation = Variation**0.5

			print("Average Difficulty of %s = %f" %(game, avgDifficulty))
			print("Variation = %f" %Variation)
			print("Standard deviation of %s = %f" %(game, Standard_deviation))

			for section in range(1,maxSection+1):
				dDegree_dict = {}
				for one in ct.find({"gameCode":game, "sectionId":section}):
					if (avgDifficulty <= one['difficulty'] < avgDifficulty+Standard_deviation):
						dDegree_dict = {'difficultyDegree':0}
					elif (avgDifficulty+Standard_deviation <= one['difficulty'] < avgDifficulty+2*Standard_deviation):
						dDegree_dict = {'difficultyDegree':1}
					elif (one['difficulty'] >= avgDifficulty+2*Standard_deviation):
						dDegree_dict = {'difficultyDegree':2}
					elif (avgDifficulty - Standard_deviation <= one['difficulty'] < avgDifficulty):
						dDegree_dict = {'difficultyDegree':-1}
					elif (avgDifficulty - 2*Standard_deviation <= one['difficulty'] < avgDifficulty - Standard_deviation):
						dDegree_dict = {'difficultyDegree':-2}
					elif (one['difficulty'] < avgDifficulty-2*Standard_deviation):
						dDegree_dict = {'difficultyDegree':-3}
					
					ct.update_one({"gameCode":game, "sectionId": section},{'$set': dDegree_dict}, upsert = True)
					countInsert += 1

	###delete data
	#value =0
	if(value == 0):
		print('''修改或刪除資料前, 先刪除該與該資料或欄位相關的index可大幅加快速度, 避免硬碟寫入滿載, 因修改或刪除資料必須重新排序index''')
		choice = int(input("(1)delete data\n(2)update data\n(3)count data\n："))
		startTime = time.time()
		database = 'dotCode'
		if choice == 1:
			collection = 'Record'
			ct = clientCT(database, collection)
			
			print("delete %s data" %collection)
			#myquery = {'gameCode':'Maze'}
			#myquery = {"tryCount":{"$gt":0}}
			myquery = {'gameCode':'Maze'}
			#myquery = {'$and':[{'gameCode':{'$ne':'Maze'}}, {'gameCode':{'$ne':None}}, {'gamecode':'Maze'}]}

			x = ct.delete_many(myquery)
			print(x.deleted_count, "documents deleted.")
		
		elif choice == 2:
			collection = 'AccuTime'
			ct = clientCT(database, collection)
			
			'''
			# 刪除欄位
			print("unset %s data" %collection)
			unset_dict = {'logTime_sec':''}
			x = ct.update_many({"gameCode":"Duck"}, {'$unset':unset_dict}, upsert=False)
			#x = ct.update_many({}, {'$unset':{"accumulatedTime":''}}, upsert=False)
			print(x.modified_count, "documents modified.")
			'''
			
			# 修改欄位
			print("unset %s data" %collection)
			for one in ct.find({"gameCode":"Duck"}):
				wrongTime_sec = one['accuTime_sec']-one['GameTime_sec'] if one['gameStar'] > 0 else one['accuTime_sec'],
				modify_dict = {'wrongTime_sec' : wrongTime_sec, 
							   'logwrongTime_sec' : float(np.log(wrongTime_sec))
							  }
			x = ct.update_one({"gameCode":"Duck"}, {'$set':modify_dict}, upsert=True)
			print(x.modified_count, "documents modified.")
			
			'''
			# 增加欄位
			print("upsert data")
			for one in ct.find({"gameCode":"Duck"}): 
				update_dict = {"logTime_sec":np.log(one['gameTime']/1000)}
				ct.update_one({'_id':one['_id']}, {'$set':update_dict}, upsert=False)
			'''
			'''
			pipeline = [#{'$match':{"sectionId":section}},
						{'$group': {'_id': "$sectionId", 'count': {'$sum': 1}}},
						#{'$count': "count"}
					   ]
			a = []
			b = []
			for x in db.FirstRecord.aggregate(pipeline):
				a.append(x['count'])
			for y in db.AccuTime.aggregate(pipeline):
				b.append(y['count'])
			
			for i, j in zip(a,b):
				if i != j:
					print(i, j)
			'''	
		
		elif choice == 3:	
			collection = 'Record'
			ct = clientCT(database, collection)
			#db.AccuTime.aggregate([{$match:{gameCode:'Duck', accumulatedTime_sec:{'$lt':10}, gameStar:{'$gt':0}}},{$count: "count"}])
			#db.collection.aggregate([{$group:{sectionId:1, myCount:{$sum:1}}},{$project:{_id:0}}])
			print("count data")
			newsection = 0
			section_count = columnFunc(0, maxSection, 0)
			for one in ct.find({"gameCode":"Duck", "newGameTime":{"$gte":0}}):
				newsection = 0 if one['sectionId'] > 60 else one['sectionId']
				section_count[newsection] += 1		
			peo += 1
			
			for i, record in zip(range(0, maxSection), section_count):
				print(i, record, "\n")
				
	endTime = time.time()
	passTime = (endTime - startTime)
	#tran_startTime = datetime.datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S")
	#tran_endTime = datetime.datetime.fromtimestamp(endTime).strftime("%Y-%m-%d %H:%M:%S")		
	print("total inserted data:", countInsert, "列入紀錄總人數:", peo)
	print("執行時間", passTime, "秒")
