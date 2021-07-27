from pymongo import MongoClient
import numpy as np
import traceback
import os
import time
import datetime
import gc
import json
import PaperCommon as pc



if __name__ =='__main__':
	connection = MongoClient('localhost', 27017)
	print(connection.list_database_names())  #Return a list of db, equal to: > show dbs
	db = connection["DATA"]
	
	choice = int(input("(1)insert one data at a time \n(2)import collection \n(3)fix wrong time \n"))
	if choice == 1:
		for c in db.list_collection_names():
			ct = db[c]		
			CTN, oriCollect = str(c).split("_")
			addCount = 0
			mazeCount = 0
			duckCount = 0
			for one in ct.find():
				one['YYMMDD'] = pc.to_vids_time((one['lastUpdateTime'])/1000)# 把lastUpdateTime轉成西元時間		 
				one['oriCollect'] = oriCollect
				
				if one['gameCode'] == 'Maze' :
					if CTN == 'dotCodeStar':
						db.Star_Maze.insert(one, w=1, j=True, wtimeout=1000)
					elif CTN == 'dotCodeRecord':
						db.Reocrd.insert(one, w=1, j=True, wtimeout=1000)
					mazeCount += 1

				elif one['gameCode'] == 'Duck':
					if CTN == 'dotCodeStar':
						db.Star_Duck.insert(one, w=1, j=True, wtimeout=1000)
					elif CTN == 'dotCodeRecord':
						db.Reocrd.insert(one, w=1, j=True, wtimeout=1000)
					duckCount += 1			

				addCount += 1
				#print("正在寫入第 %d 筆資料" %addCount)
				tran_endTime = pc.to_vids_time(time.time())
			
			if addCount > 0:
				logPath = r"D:\paper\practice\practice file\Record\InsertLog.txt"
				logContent = "開始時間：%s\n%s寫入完成!\nMaze寫入 %d 筆!\nDuck寫入 %d 筆!\n總計 %d 筆data!\n結束時間：%s\n" %(tran_startTime, collection, mazeCount, duckCount, addCount, tran_endTime)
				pc.writeLog(logPath, logContent)
				print(logContent)

	elif choice == 2:
		readpath = r"D:\MongoDB\Server\4.0\data\DATA"
		files = os.listdir(readpath)
		for file in files:
			if str(file).find("dotCodeRecord") > -1:
				fileReadpath = os.path.join(readpath, file)
				#檔案(非資料夾)   
				with open(fileReadpath, encoding='UTF-8') as f:
					file_data = json.load(f)
				db.Record.insert_many(file_data)
				'''
				if pymongo < 3.0, use insert()
					collection_currency.insert(file_data)
				if pymongo >= 3.0 use insert_one() for inserting one document
					collection_currency.insert_one(file_data)
				if pymongo >= 3.0 use insert_many() for inserting many documents
				'''
				
	elif choice == 3:
		'''
		尋找此ID的所有遊戲紀錄，將連續的兩個遊戲紀錄的lastUpdateTime相減
		算出lastUpdateTime較後面的紀錄的gameTime
		'''
		ct = pc.clientCT(database, 'Record')
		path = r"D:\paper\practice\practice file\record\ErrorProcess"
		restoreFile = "Restore.csv"
		thefirstFile = "TheFirst.csv"
		remove_file(path, restoreFile)
		remove_file(path, thefirstFile)

		restore, theFirst, count, normal = 0, 0, 0, 0
		limitTime = 1200000
		errorTime = []
		
		print("start to create index...")	# 建立索引
		db.Record.create_index([('gameCode', 1), ('userId', 1)])
		db.Record.create_index([('gameCode', 1), ('gameTime', 1)])
		db.Record.create_index([('gameTime', 1)])
		print("Indexes created！") 
		
		print("Start to find abnormal game time...")
		#timeQuery = {"$or":[{"gameTime":None},{"gameTime":{"$gt":limitTime}},{"gameTime":{"$lte":0}}]}
		for one in ct.find({"gameCode":'Duck', "accumulatedTime_sec":{'$lte':6}, "gameStar":{'$gt':0}}):
			count += 1
			errorTime.append(one['userId'])
		
		for one in ct.find({"gameCode":"Duck", "gameTime":{"$gt":limitTime}}):
			count += 1
			errorTime.append(one['userId'])
		
		print("length of errorTime:", len(errorTime))
		errorTime = set(errorTime)
		peo = len(errorTime)
		print("length of set errorTime", peo)
		findEndTime = time.time()	
		
		# find userId in the list
		collection = 'Record'
		ct = client[database][collection]

		for id in errorTime:
		#for id in range(457401, 457402):	
			record = []
			for one in ct.find({"userId":id}):
				record.append([one['lastUpdateTime'], one['gameTime'], one['userId'] ,one['_id'], one['gameCode'], one['gameStar']])		
			record = bubbleSort(record, 0)
			#pc.merge_sort(record, 0)
			x = len(record)
			print(record)
			os.system("pause")
			i = 0
			while i < x:
				newGameTime = 0
				if (record[i][1] <= 0) or (record[i][4] == 'Duck' and record[i][1] > limitTime):	#gameTime lower than zero or gameTime > 20 minutes
					if 0 < i < len(record):		#不是第1筆資料 
						newGameTime = record[i][0] - record[i-1][0]
						if record[i][1] > 0:
							if newGameTime < record[i][1]: #新gameTime比原gameTime小
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

					else:	# if the record is the first record of the userId in the collection, then we can't calculate the gameTime 
						theFirst += 1
						if record[i][1] <= 0:
							ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime":0}})
							#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", 0, "the first")
						else:
							ct.update_one({"_id":record[i][3]}, {"$set":{"newGameTime":record[i][1]}})
							#print(peo, "userId:", record[i][2], "gameTime:", record[i][1], "newGameTime:", newGameTime, "the first")
						
						record[i].append(newGameTime)
						if len(record) == 1:
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
		
	connection.close()