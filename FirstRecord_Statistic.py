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
			
def sortFunc2(x):
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
		
		right_index = 0;
		left_index = 0;
		merged_index = 0;
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
	collection = 'Sec_sta'
	ct = clientCT(database, collection)
	
	Item_Difficulty = []
	Difficulty_Degree = []

	for section in range(1, maxsection+1):
		for one in ct.find({'gameCode': game, 'sectionId':section}):
			Item_Difficulty.append(one['difficulty'])
			Difficulty_Degree.append(one['difficultyDegree'])
	return Item_Difficulty, Difficulty_Degree

choice = int(input("開始執行程式(1)Yes(2)No："))
if choice != 1:
	os.exit_(0)
peo = 0 #有紀錄的玩家
countInsert = 0 #insert的筆數
gameCode = ['Maze', 'Duck']
degree = [-3, -2, -1, 0, 1, 2]

FirstRecord_count = 0
FirstRecordLog_count = 0

database = 'dotCode'
db = clientDB(database)

#一般秒用x, y，log秒用m, n
x = 57600
y = 1
m = 20
n = 0.1

for game in gameCode:
	if game == 'Maze':
		maxSection = 40
	elif game == 'Duck':
		maxSection = 60

	item_difficulty = Add_Difficulty(game, maxSection)[0]
	difficultyDegree = Add_Difficulty(game, maxSection)[1]

	collection = 'FirstRecord'		
	ct = clientCT(database, collection)
	
	ct.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('gameTime', 1), ('difficultyDegree', 1)])		
	ct.create_index([('gameCode', 1), ('sectionId', 1), ('gameTime', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree', 1), ('gameStar', 1),  ('gameTime', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree', 1), ('gameTime', 1)])
	
	startTime = time.time()
	
	##step1依關卡
	print("insert %s data by section" %game)
	for section in range(1, maxSection+1):
		allPeople = []
		allCorrectness = []
		allPeople = columnFunc(0, int(x//y+1), 0)
		allCorrectness = columnFunc(0, int(x//y+1), 0)
		
		allPeople_log = []
		allCorrectness_log = []
		allPeople_log = columnFunc(0, int(m//n+1), 0)
		allCorrectness_log = columnFunc(0, int(m//n+1), 0)
		
		for star in range(0, 5):
			people = []
			totalCorrectness = []
			people = columnFunc(0, int(x//y+1), 0)
			totalCorrectness = columnFunc(0, int(x//y+1), 0)
			
			people_log = []
			totalCorrectness_log = []
			people_log = columnFunc(0, int(m//n+1), 0)
			totalCorrectness_log = columnFunc(0, int(m//n+1), 0)
			
			for one in ct.find({"gameCode":game, "sectionId":section, "gameStar":star, "gameTime":{"$gt":0, "$lte":x*1000}}):
				a = int(one['gameTime']//1000)
				people[a] += 1
				allPeople[a] += 1
				
				b = int(one['logTime_sec']//n)+24
				people_log[b] += 1
				allPeople_log[b] += 1					
				
				if(one['gameStar'] > 0):
					correctness = 1
				else:
					correctness = 0
				
				totalCorrectness[a] += correctness
				allCorrectness[a] += correctness
				
				totalCorrectness_log[b] += correctness
				allCorrectness_log[b] += correctness
				
			#分星星
			#秒
			for dseconds, dpeo, dcorrect, in zip(range(0, x+y, y), people, totalCorrectness):
				if (dpeo > 0):
					FirstRecord_sta_dict = {"gameCode" : game,
											"sectionId" : section,
											"seconds": dseconds,
											"tickTime" : y,
											"gameStar" : star,
											"people" : dpeo,
											"difficulty" : item_difficulty[section-1],
											"difficultyDegree" : difficultyDegree[section-1],
											"avgCorrectness" : dcorrect/dpeo
										   }
					db.FirstRecord_sta.update_one({"gameCode":game, "sectionId": section, "gameStar":star, "tickTime":y, "seconds":dseconds},{'$set': FirstRecord_sta_dict}, upsert = True)
					FirstRecord_count += 1
			#Log秒		
			for dseconds_log, dpeo_log, dcorrect_log, in zip(np.arange(-2.4, m+n, n), people_log, totalCorrectness_log):
				if (dpeo_log > 0):
					FirstRecordLog_sta_dict = {"gameCode" : game,
											   "sectionId" : section,
											   "seconds_log": round(dseconds_log,2),
											   "tickTime" : n,
											   "gameStar" : star,
											   "people" : dpeo_log,
											   "difficulty" : item_difficulty[section-1],
											   "difficultyDegree" : difficultyDegree[section-1],
											   "avgCorrectness" : dcorrect_log/dpeo_log
											  }
					db.FirstRecordLog_sta.update_one({"gameCode":game, "sectionId": section, "gameStar":star, "tickTime":n, "seconds_log":round(dseconds_log,2)},{'$set':FirstRecordLog_sta_dict}, upsert = True)
					FirstRecordLog_count += 1		
			del	people, totalCorrectness, people_log, totalCorrectness_log			
			gc.collect()
		#不分星星
		#秒
		for seconds_all, peo_all, correct_all, in zip(range(0, x+y, y), allPeople, allCorrectness):
			if (peo_all > 0):
				FirstRecordAll_sta_dict = {"gameCode" : game,
										   "sectionId" : section,
										   "seconds": seconds_all,
										   "tickTime" : y,
										   "gameStar" : 5,
										   "people" : peo_all,
										   "difficulty" : item_difficulty[section-1],
										   "difficultyDegree" : difficultyDegree[section-1],
										   "avgCorrectness" : correct_all/peo_all
									      }
				db.FirstRecord_sta.update_one({"gameCode":game, "sectionId":section, "gameStar":5, "tickTime":y, "seconds": seconds_all},{'$set': FirstRecordAll_sta_dict}, upsert = True)      
				db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1)])
				FirstRecord_count += 1
		#log秒
		for seconds_all_log, peo_all_log, correct_all_log, in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log):
			if (peo_all_log > 0):
				FirstRecordAllLog_sta_dict = {"gameCode" : game,
											  "sectionId" : section,
											  "seconds_log": round(seconds_all_log, 2),
											  "tickTime" : n,
											  "gameStar" : 5,
											  "people" : peo_all_log,
											  "difficulty" : item_difficulty[section-1],
											  "difficultyDegree" : difficultyDegree[section-1],
											  "avgCorrectness" : correct_all_log/peo_all_log
											 }
				db.FirstRecordLog_sta.update_one({"gameCode":game, "sectionId":section, "gameStar":5, "tickTime":n, "seconds_log":round(seconds_all_log, 2)},{'$set':FirstRecordAllLog_sta_dict}, upsert = True)   
				db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1)])
				FirstRecordLog_count += 1 		
		del	allPeople, allCorrectness ,allPeople_log, allCorrectness_log
		gc.collect()
	
	##step2依難度等級
	print("insert %s data by difficulty degree" %game)
	for i in range(0, len(degree)):
		allPeople = []
		allCorrectness = []
		allPeople = columnFunc(0, int(x//y+1), 0)
		allCorrectness = columnFunc(0, int(x//y+1), 0)
		
		allPeople_log = []
		allCorrectness_log = []
		allPeople_log = columnFunc(0, int(m//n+1), 0)
		allCorrectness_log = columnFunc(0, int(m//n+1), 0)
		
		for star in range(0, 5):
			people = []
			totalCorrectness = []
			people = columnFunc(0, int(x//y+1), 0)
			totalCorrectness = columnFunc(0, int(x//y+1), 0)
			
			people_log = []
			totalCorrectness_log = []
			people_log = columnFunc(0, int(m//n+1), 0)
			totalCorrectness_log = columnFunc(0, int(m//n+1), 0)
			for two in ct.find({"gameCode":game, "difficultyDegree":degree[i], "gameStar": star, "gameTime":{"$gt":0, "$lte":x*1000}}):
				#print(two)
				a = int(two['gameTime']//1000)
				people[a] += 1
				allPeople[a] += 1

				b = int(two['logTime_sec']//n)+24
				people_log[b] += 1
				allPeople_log[b] += 1	
				
				if(two['gameStar'] > 0):
					correctness = 1
				else:
					correctness = 0
				
				totalCorrectness[a] += correctness
				allCorrectness[a] += correctness
				
				totalCorrectness_log[b] += correctness
				allCorrectness_log[b] += correctness
				
			#分星星
			#秒
			for dseconds, dpeo, dcorrect in zip(range(0, x+y, y), people, totalCorrectness):
				if(dpeo) > 0:
					dtime_dict = {"gameCode": game,
								  "sectionId": 0,
								  "seconds": dseconds,
								  "tickTime" : y,
								  "gameStar" : star,
								  "people" : dpeo,
								  "difficulty" : None,
								  "difficultyDegree" : degree[i],
								  "avgCorrectness" : dcorrect/dpeo
								 }
					db.FirstRecord_sta.update_one({"gameCode":game,"seconds":dseconds,"tickTime":y,"gameStar":star,"difficulty":None,"difficultyDegree":degree[i]}, {'$set':dtime_dict}, upsert = True)			
					FirstRecord_count += 1
			#log秒
			for dseconds_log, dpeo_log, dcorrect_log in zip(np.arange(-2.4, m+n, n), people_log, totalCorrectness_log):
				if(dpeo_log) > 0:
					dtimeLog_dict = {"gameCode": game,
									 "sectionId": 0,
									 "seconds_log": round(dseconds_log, 2),
									 "tickTime" : n,
									 "gameStar" : star,
									 "people" : dpeo_log,
									 "difficulty" : None,
									 "difficultyDegree" : degree[i],
									 "avgCorrectness" : dcorrect_log/dpeo_log
									}
					db.FirstRecordLog_sta.update_one({"gameCode":game, "seconds_log":round(dseconds_log, 2), "tickTime":n, "gameStar":star, "difficulty":None, "difficultyDegree":degree[i]}, {'$set':dtimeLog_dict}, upsert = True)
					FirstRecordLog_count += 1
			del	people, totalCorrectness, people_log, totalCorrectness_log			
			gc.collect()		

		#不分星星
		#秒
		for seconds_all, peo_all, correct_all in zip(range(0, x+y, y), allPeople, allCorrectness):
			if(peo_all) > 0:
				dtimeAll_dict = {"gameCode":game,
								 "sectionId": 0,
								 "seconds": seconds_all,
								 "tickTime" : y,
								 "gameStar" : 5,
								 "people" : peo_all,
								 "difficulty" : None,
								 "difficultyDegree" : degree[i],
								 "avgCorrectness" : correct_all/peo_all
								}
				db.FirstRecord_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds_all, "tickTime":y, "gameStar":5, "difficulty":None, "difficultyDegree":degree[i]}, {'$set': dtimeAll_dict}, upsert = True)
				FirstRecord_count += 1
		#log秒
		for seconds_all_log, peo_all_log, correct_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log):
			if(peo_all_log) > 0:
				dtimeAllLog_dict = {"gameCode":game,
									"sectionId": 0,
									"seconds_log": round(seconds_all_log, 2),
									"tickTime" : n,
									"gameStar" : 5,
									"people" : peo_all_log,
									"difficulty" : None,
									"difficultyDegree" : degree[i],
									"avgCorrectness" : correct_all_log/peo_all_log
								   }
				db.FirstRecordLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficulty":None, "difficultyDegree":degree[i]}, {'$set': dtimeAllLog_dict}, upsert = True)					
				FirstRecordLog_count += 1
		del	allPeople, allCorrectness ,allPeople_log, allCorrectness_log
		gc.collect()

	
	##step3依時間 
	print("insert %s data by time" %game)
	allPeople = []
	allCorrectness = []	
	allDifficulty = []	#用來平均難度
	allPeople = columnFunc(0, int(x//y+1), 0)
	allCorrectness = columnFunc(0, int(x//y+1), 0)
	allDifficulty = columnFunc(0, int(x//y+1), 0)
	
	allPeople_log = []
	allCorrectness_log = []
	allDifficulty_log = []	
	allPeople_log = columnFunc(0, int(m//n+1), 0)
	allCorrectness_log = columnFunc(0, int(m//n+1), 0)
	allDifficulty_log = columnFunc(0, int(m//n+1), 0)
	
	for one in ct.find({"gameCode":game, "gameTime":{"$gt":0, "$lte":x*1000}}):
		a = int(one['gameTime']//1000)
		allPeople[a] += 1
		
		b = int(one['logTime_sec']//n)+24
		allPeople_log[b] += 1					
		
		if(one['gameStar'] > 0):
			correctness = 1
		else:
			correctness = 0
		
		allCorrectness[a] += correctness
		allDifficulty[a] += one['difficulty']
		
		allCorrectness_log[b] += correctness
		allDifficulty_log[b] += one['difficulty']
				
	#不分星星
	#秒
	for seconds_all, peo_all, correct_all, difficulty_all in zip(range(0, x+y, y), allPeople, allCorrectness, allDifficulty):
		if (peo_all > 0):
			FirstRecordAll_sta_dict = {"gameCode" : game,
									   "sectionId" : 0,
									   "seconds": seconds_all,
									   "tickTime" : y,
									   "gameStar" : 5,
									   "people" : peo_all,
									   "difficulty" : difficulty_all/peo_all,
									   "difficultyDegree" : 'n',
									   "avgCorrectness" : correct_all/peo_all
								      }
			db.FirstRecord_sta.update_one({"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":y, "seconds":seconds_all, "difficultyDegree":'n'},{'$set': FirstRecordAll_sta_dict}, upsert = True)      
			db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1)])
			FirstRecord_count += 1
	#log秒
	for seconds_all_log, peo_all_log, correct_all_log, difficulty_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, allDifficulty_log):
		if (peo_all_log > 0):
			FirstRecordAllLog_sta_dict = {"gameCode" : game,
										  "sectionId" : 0,
										  "seconds_log": round(seconds_all_log, 2),
										  "tickTime" : n,
										  "gameStar" : 5,
										  "people" : peo_all_log,
										  "difficulty" : difficulty_all_log/peo_all_log,
										  "difficultyDegree" : 'n',
										  "avgCorrectness" : correct_all_log/peo_all_log
										 }
			db.FirstRecordLog_sta.update_one({"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":n, "seconds_log":round(seconds_all_log, 2), "difficultyDegree":'n'},{'$set':FirstRecordAllLog_sta_dict}, upsert = True)   
			db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1)])
			FirstRecordLog_count += 1 		
	del	allPeople, allCorrectness ,allPeople_log, allCorrectness_log
	gc.collect()
	
	
endTime = time.time()
passTime = (endTime - startTime)	
print("Insert FirstRecord:", FirstRecord_count, "\nInsert FirstRecordLog:", FirstRecordLog_count)	
print("執行時間", passTime, "秒")
print("列入紀錄總數:", peo)