from pymongo import MongoClient
import numpy as np
import pandas as pd
import traceback
import os
import time
import datetime
import gc

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


###Insert average correct percentage every y seconds from AccuTime to AccuTime_sta
choice = int(input("開始執行程式(1)Yes(other)No："))
if choice != 1:
	os._exit(0)
	
startTime = time.time() 	
	
peo = 0 #有紀錄的玩家
countInsert = 0 #insert的筆數
#gameCode = ['Maze', 'Duck']
gameCode = ['Duck']
degree = [-3, -2, -1, 0, 1, 2]                                

database = 'dotCode'
db = clientDB(database)

#一般秒用x, y，log秒用m, n，Z用p, q， Zlog用u, v 
x = 999999
y = 10
m = 20
n = 0.1
p = 500
q = 1
u = 2
v = 0.01

#原資料庫建索引
collection = 'AccuTime'		
ct = clientCT(database, collection)
#1.依關卡
ct.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('accumulatedTime_sec', 1)])
ct.create_index([('sectionId', 1), ('gameStar', 1), ('accumulatedTime_sec', 1)])
#2.依難度
ct.create_index([('gameCode', 1), ('difficultyDegree', 1), ('gameStar', 1),('accumulatedTime_sec', 1)])
ct.create_index([('difficultyDegree', 1), ('gameStar', 1),('accumulatedTime_sec', 1)])
#3.依時間
ct.create_index([('gameCode', 1), ('accumulatedTime_sec', 1)])
ct.create_index([('accumulatedTime_sec', 1)])
#新資料庫建索引
#1.依關卡
db.AccuTime_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1)])
db.AccuTimeLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1)])
#2.依難度
db.AccuTime_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('difficultyDegree', 1)])
db.AccuTimeLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('difficultyDegree', 1)])
#3.依時間(AccuTime_sta與AccuTimeLog_sta不建，與難度相同)
db.AccuTimeZ_sta.create_index([('gameCode', 1), ('seconds_z', 1), ('tickTime', 1), ('gameStar', 1)])


AccuTime_count = 0
AccuTimeLog_count = 0
AccuTimeZ_count = 0

for game in gameCode:
	if game == 'Maze':
		maxSection = 40
	elif game == 'Duck':
		maxSection = 60

	item_difficulty = Add_Difficulty(game, maxSection)[0]
	difficultyDegree = Add_Difficulty(game, maxSection)[1]
	
	##step1依關卡
	print("insert %s data by section" %game)
	for section in range(1, maxSection+1):
		allPeople, allCorrectness, allTryCount = [], [], []
		allPeople = columnFunc(1, int(x//y)+2, 0)
		allCorrectness = columnFunc(1, int(x//y)+2, 0)
		allTryCount = columnFunc(1, int(x//y)+2, 0)
		
		allPeople_log, allCorrectness_log, allTryCount_log = [], [], []
		allPeople_log = columnFunc(0, int(m//n)+1, 0)
		allCorrectness_log = columnFunc(0, int(m//n)+1, 0)
		allTryCount_log = columnFunc(0, int(m//n)+1, 0)
		
		passPeople, passCorrectness, passTryCount = [], [], []
		passPeople = columnFunc(1, int(x//y)+2, 0)
		passCorrectness = columnFunc(1, int(x//y)+2, 0)
		passTryCount = columnFunc(1, int(x//y)+2, 0)
		
		passPeople_log,passCorrectness_log, passTryCount_log = [], [], []
		passPeople_log = columnFunc(0, int(m//n)+1, 0)
		passCorrectness_log = columnFunc(0, int(m//n)+1, 0)
		passTryCount_log = columnFunc(0, int(m//n)+1, 0)
		
		for star in range(0, 5):
			people, correctness, tryCount = [], [], []
			people = columnFunc(1, int(x//y)+2, 0)
			correctness = columnFunc(1, int(x//y)+2, 0)
			tryCount = columnFunc(1, int(x//y)+2, 0)
			
			people_log, correctness_log, tryCount_log= [], [], []
			people_log = columnFunc(0, int(m//n)+1, 0)
			correctness_log = columnFunc(0, int(m//n)+1, 0)
			tryCount_log = columnFunc(0, int(m//n)+1, 0)
			
			for one in ct.find({"gameCode":game, "sectionId":section, "gameStar":star, "accumulatedTime_sec":{"$gt":0, "$lte":x}}):
				try:
					a = int(one['accumulatedTime_sec']//y)
					people[a] += 1
					correctness[a] += one['correctPercentage']
					tryCount[a] += one['tryCount']
					
					allPeople[a] += 1
					allCorrectness[a] += one['correctPercentage']
					allTryCount[a] += one['tryCount']
					
					if star > 0:
						passPeople[a] += 1
						passCorrectness[a] += one['correctPercentage']
						passTryCount[a] += one['tryCount']
					
					b = int(one['logTime_sec']//n)+24
					people_log[b] += 1
					correctness_log[b] += one['correctPercentage']
					tryCount_log[b] += one['tryCount']
					
					allPeople_log[b] += 1
					allCorrectness_log[b] += one['correctPercentage']
					allTryCount_log[b] += one['tryCount']
					
					if star > 0:
						passPeople_log[b] += 1
						passCorrectness_log[b] += one['correctPercentage']
						passTryCount_log[b] += one['tryCount']	
				except:
					print(one)
				
			#分星星
			#秒
			for seconds, i_count, i_correct, i_try in zip(range(y, x+y+1, y), people, correctness, tryCount):
				if(i_count) > 0:
					#print("seconds:", seconds, "i_count:", i_count, "try", i_try, "i_correct:", i_correct/i_count)
					#os.system("pause")
					AccuTime_sta_dict = {"gameCode":game,
										 "sectionId":section,
										 "seconds":seconds,
										 "tickTime":y,
										 "gameStar":star,
										 "people":i_count,
										 "difficulty":item_difficulty[section-1],
										 "difficultyDegree":difficultyDegree[section-1],
										 "avgCorrectness":i_correct/i_count,
										 "avgTryCount":i_try/i_count,
										 "step":"1-1"
										}    
					db.AccuTime_sta.update_one({"gameCode":game, "sectionId":section, "seconds":seconds, "tickTime":y, "gameStar":star}, {'$set':AccuTime_sta_dict}, upsert = True)
					AccuTime_count += 1
			#Log秒		
			for seconds_log, i_count_log, i_correct_log, i_try_log in zip(np.arange(-2.4, m+n, n), people_log, correctness_log, tryCount_log):
				if (i_count_log > 0):
					AccuTimeLog_sta_dict = {"gameCode":game,
											"sectionId":section,
											"seconds_log":round(seconds_log, 2),
											"tickTime":n,
											"gameStar":star,
											"people":i_count_log,
											"difficulty":item_difficulty[section-1],
											"difficultyDegree":difficultyDegree[section-1],
											"avgCorrectness":i_correct_log/i_count_log,
											"avgTryCount":i_try_log/i_count_log,
											"step":"1-1"
										   }
					db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":section, "seconds_log":round(seconds_log, 2), "tickTime":n, "gameStar":star}, {'$set':AccuTimeLog_sta_dict}, upsert = True)
					AccuTimeLog_count += 1		
			del	people, correctness, tryCount, people_log, correctness_log, tryCount_log			
			gc.collect()
		
		#不分星
		#秒
		for seconds_all, i_count_all, i_correct_all, i_try_all in zip(range(y, x+y+1, y), allPeople, allCorrectness, allTryCount):
			if i_count_all > 0:
				#print("seconds:", seconds, "i_count:", i_count, "i_correct:", i_correct)
				AccuTimeAll_sta_dict  = {"gameCode":game,
										 "sectionId":section,
										 "seconds":seconds_all,
										 "tickTime":y,
										 "gameStar":5,	#5是不分星星數
										 "people":i_count_all,
										 "difficulty":item_difficulty[section-1],
										 "difficultyDegree":difficultyDegree[section-1],
										 "avgCorrectness":i_correct_all/i_count_all,
										 "avgTryCount":i_try_all/i_count_all,
										 "step":"1-2"
										}
				db.AccuTime_sta.update_one({"gameCode":game, "sectionId":section, "seconds":seconds_all, "tickTime":y, "gameStar":5}, {'$set':AccuTimeAll_sta_dict}, upsert = True)
				AccuTime_count += 1
						   
		#log秒
		for seconds_all_log, i_count_all_log, i_correct_all_log, i_try_all_log, in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, allTryCount_log):
			if (i_count_all_log > 0):
				AccuTimeAllLog_sta_dict = {"gameCode":game,
										   "sectionId":section,
										   "seconds_log":round(seconds_all_log, 2),
										   "tickTime":n,
										   "gameStar":5,	#5是不分星星數
										   "people":i_count_all_log,
										   "difficulty" : item_difficulty[section-1],
										   "difficultyDegree" : difficultyDegree[section-1],
										   "avgCorrectness" : i_correct_all_log/i_count_all_log,
										   "avgTryCount" : i_try_all_log/i_count_all_log,
										   "step":"1-2"
										  }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":section, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5}, {'$set':AccuTimeAllLog_sta_dict}, upsert = True)   
				AccuTimeLog_count += 1 		
		del	allPeople, allCorrectness ,allTryCount, allPeople_log, allCorrectness_log, allTryCount_log
		gc.collect()
					
		#只算有過關
		#秒
		for seconds_pass, i_count_pass, i_correct_pass, i_try_pass in zip(range(y, x+y+1, y), passPeople, passCorrectness, passTryCount):
			if i_count_pass > 0:
				AccuTimePass_sta_dict = {"gameCode":game,
										 "sectionId":section,
										 "seconds":seconds_pass,
										 "tickTime":y,
										 "gameStar":6,	#6是有過關
										 "people":i_count_pass,
										 "difficulty":item_difficulty[section-1],
										 "difficultyDegree":difficultyDegree[section-1],
										 "avgCorrectness":i_correct_pass/i_count_pass,
										 "avgTryCount":i_try_pass/i_count_pass,
										 "step":"1-3"
										}
				db.AccuTime_sta.update_one({"gameCode":game, "sectionId":section, "seconds":seconds_pass, "tickTime":y, "gameStar":6}, {'$set':AccuTimePass_sta_dict}, upsert = True)
				AccuTime_count += 1	
		
		#log秒
		for seconds_pass_log, i_count_pass_log, i_correct_pass_log, i_try_pass_log, in zip(np.arange(-2.4, m+n, n), passPeople_log, passCorrectness_log, passTryCount_log):
			if i_count_pass_log > 0:
				AccuTimePassLog_sta_dict = {"gameCode":game,
										   "sectionId":section,
										   "seconds_log":round(seconds_pass_log, 2),
										   "tickTime":n,
										   "gameStar":6,	#6是有過關
										   "people":i_count_pass_log,
										   "difficulty" : item_difficulty[section-1],
										   "difficultyDegree" : difficultyDegree[section-1],
										   "avgCorrectness" : i_correct_pass_log/i_count_pass_log,
										   "avgTryCount" : i_try_pass_log/i_count_pass_log,
										   "step":"1-3"
										  }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":section, "seconds_log":round(seconds_pass_log, 2), "tickTime":n, "gameStar":6}, {'$set':AccuTimePassLog_sta_dict}, upsert = True)   
				AccuTimeLog_count += 1 		
		del	passPeople, passCorrectness ,passTryCount, passPeople_log, passCorrectness_log, passTryCount_log
		gc.collect()		
	
	##step2依難度等級
	print("insert %s data by difficulty degree" %game)
	for i in range(0, len(degree)):
		allPeople, allCorrectness, alltryCount = [], [], []
		allPeople = columnFunc(1, int(x//y)+2, 0)
		allCorrectness = columnFunc(1, int(x//y)+2, 0)
		alltryCount = columnFunc(1, int(x//y)+2, 0)
		
		allPeople_log, allCorrectness_log, alltryCount_log = [], [], []
		allPeople_log = columnFunc(0, int(m//n)+1, 0)
		allCorrectness_log = columnFunc(0, int(m//n)+1, 0)
		alltryCount_log = columnFunc(0, int(m//n)+1, 0)
		
		passPeople, passCorrectness, passtryCount = [], [], []
		passPeople = columnFunc(1, int(x//y)+2, 0)
		passCorrectness = columnFunc(1, int(x//y)+2, 0)
		passtryCount = columnFunc(1, int(x//y)+2, 0)
		
		passPeople_log, passCorrectness_log, passtryCount_log = [], [], []
		passPeople_log = columnFunc(0, int(m//n)+1, 0)
		passCorrectness_log = columnFunc(0, int(m//n)+1, 0)
		passtryCount_log = columnFunc(0, int(m//n)+1, 0)
		
		for star in range(0, 5):
			people, correctness, tryCount = [], [], []
			people = columnFunc(1, int(x//y)+2, 0)
			correctness = columnFunc(1, int(x//y)+2, 0)
			tryCount = columnFunc(1, int(x//y)+2, 0)
			
			people_log, correctness_log, tryCount_log = [], [], [] 
			people_log = columnFunc(1, int(m//n)+2, 0)
			correctness_log = columnFunc(1, int(m//n)+2, 0)
			tryCount_log = columnFunc(1, int(m//n)+2, 0)
			
			for two in ct.find({"gameCode":game, "difficultyDegree":degree[i], "gameStar":star, "accumulatedTime_sec":{"$gt":0, "$lte":x}}):
				try:
					a = int(two['accumulatedTime_sec'] // y)
	
					people[a] += 1
					correctness[a] += two['correctPercentage']
					tryCount[a] += two['tryCount']
					
					allPeople[a] += 1
					allCorrectness[a] += two['correctPercentage']
					alltryCount[a] += two['tryCount']
					
					if star > 0:
						passPeople[a] += 1
						passCorrectness[a] += two['correctPercentage']
						passtryCount[a] += two['tryCount']
					
					b = int(two['logTime_sec']//n)+24
					
					people_log[b] += 1
					correctness_log[b] += two['correctPercentage']
					tryCount_log[b] += two['tryCount']
						
					allPeople_log[b] += 1
					allCorrectness_log[b] += two['correctPercentage']
					alltryCount_log[b] += two['tryCount']
					
					if star > 0:
						passPeople_log[b] += 1
						passCorrectness_log[b] += two['correctPercentage']
						passtryCount_log[b] += two['tryCount']
				except:
					print(two)
			
			#分星星
			for seconds, i_count, i_correct, i_try in zip(range(y, x+y+1, y), people, correctness, tryCount):
				if(i_count > 0):
					#print("seconds:", seconds, "i_count:", i_count, "try", i_try, "correct:", i_correct/i_count)
					#os.system("pause")
					AccuTime_sta_dict = {"gameCode":game,
										 "sectionId":0,
										 "seconds":seconds,
										 "tickTime":y,
										 "gameStar":star,
										 "people":i_count,
										 "difficulty":None,
										 "difficultyDegree":degree[i],
										 "avgCorrectness":i_correct/i_count,
										 "avgTryCount":i_try/i_count,
										 "step":"2-1"
										}
					db.AccuTime_sta.update_one({"gameCode": game,
												"sectionId":0, 
												"seconds":seconds,
												"tickTime":y, 
												"gameStar":star,
												"difficulty":None,													
												"difficultyDegree":degree[i]
												}, 
												{'$set': AccuTime_sta_dict}, 
												upsert = True
											   )
					AccuTime_count += 1
			for seconds_log, i_count_log, i_correct_log, i_try_log in zip(np.arange(-2.4, m+n, n), people_log, correctness_log, tryCount_log):
				if(i_count_log) > 0:
					AccuTimeLog_sta_dict = {"gameCode":game,
											"sectionId":0,
											"seconds_log":round(seconds_log, 2),
											"tickTime":n,
											"gameStar":star,
											"people":i_count_log,
											"difficulty":None,
											"difficultyDegree":degree[i],
											"avgCorrectness":i_correct_log/i_count_log,
											"avgTryCount":i_try_log/i_count_log,
											"step":"2-1"
										   }
					db.AccuTimeLog_sta.update_one({"gameCode":game, "seconds_log":round(seconds_log, 2), "tickTime":n, "gameStar":star, "difficulty":None, "difficultyDegree":degree[i]}, {'$set':AccuTimeLog_sta_dict}, upsert = True)
					AccuTimeLog_count += 1
			del	people, correctness, tryCount, people_log, correctness_log, tryCount_log			
			gc.collect()
		
		#不分星
		#秒
		for seconds_all, i_count_all, i_correct_all, i_try_all in zip(range(y, x+y+1, y), allPeople, allCorrectness, alltryCount):
			if(i_count_all) > 0:
				#print("seconds:", seconds, "i_count:", i_count, "correct:", correct)
				AccuTimeALL_sta_dict = {"gameCode" : game,
										"sectionId": 0,
										"seconds": seconds_all,
										"tickTime" : y,
										"gameStar" : 5,
										"people" : i_count_all,
										"difficulty" : None,
										"difficultyDegree" : degree[i],
										"avgCorrectness" : i_correct_all/i_count_all,
										"avgTryCount" : i_try_all/i_count_all,
										"step":"2-2"
									   }
				db.AccuTime_sta.update_one({"gameCode":game,
											"sectionId":0,
											"seconds":seconds_all,
											"tickTime":y,
											"gameStar":5,
											"difficulty":None,
											"difficultyDegree":degree[i]
										    },
											{'$set': AccuTimeALL_sta_dict},
											upsert = True
										   )
				AccuTime_count += 1
		#log秒
		for seconds_all_log, i_count_all_log, i_correct_all_log, i_try_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, alltryCount_log):
			if(i_count_all_log) > 0:
				AccuTimeAllLog_sta_dict = {"gameCode":game,
										   "sectionId":0,
										   "seconds_log":round(seconds_all_log, 2),
										   "tickTime":n,
										   "gameStar":5,
										   "people":i_count_all_log,
										   "difficulty":None,
										   "difficultyDegree":degree[i],
										   "avgCorrectness":i_correct_all_log/i_count_all_log,
										   "avgTryCount":i_try_all_log/i_count_all_log,
										   "step":"2-2"
										  }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficulty":None, "difficultyDegree":degree[i]}, {'$set': AccuTimeAllLog_sta_dict}, upsert = True)					
				AccuTimeLog_count += 1
		del	allPeople, allCorrectness, alltryCount, allPeople_log, allCorrectness_log, alltryCount_log
		gc.collect()
		
		#只算有過關
		#秒
		for seconds_pass, i_count_pass, i_correct_pass, i_try_pass in zip(range(y, x+y+1, y), passPeople, passCorrectness, passtryCount):
			if(i_count_pass) > 0:
				#print("seconds:", seconds, "i_count:", i_count, "correct:", correct)
				AccuTimePass_sta_dict = {"gameCode" : game,
										 "sectionId": 0,
										 "seconds": seconds_pass,
										 "tickTime" : y,
										 "gameStar" : 6,
										 "people" : i_count_pass,
										 "difficulty" : None,
										 "difficultyDegree" : degree[i],
										 "avgCorrectness" : i_correct_pass/i_count_pass,
										 "avgTryCount" : i_try_pass/i_count_pass,
										 "step":"2-3"
										}
				db.AccuTime_sta.update_one({"gameCode":game,
											"sectionId":0,
											"seconds":seconds_pass,
											"tickTime":y,
											"gameStar":6,
											"difficulty":None,
											"difficultyDegree":degree[i]
										    },
											{'$set': AccuTimePass_sta_dict},
											upsert = True
										  )
				AccuTime_count += 1
		#log秒
		for seconds_pass_log, i_count_pass_log, i_correct_pass_log, i_try_pass_log in zip(np.arange(-2.4, m+n, n), passPeople_log, passCorrectness_log, passtryCount_log):
			if(i_count_pass_log) > 0:
				AccuTimePassLog_sta_dict = {"gameCode":game,
											"sectionId":0,
											"seconds_log":round(seconds_pass_log, 2),
											"tickTime":n,
											"gameStar":6,
											"people":i_count_pass_log,
											"difficulty":None,
											"difficultyDegree":degree[i],
											"avgCorrectness":i_correct_pass_log/i_count_pass_log,
											"avgTryCount":i_try_pass_log/i_count_pass_log,
											"step":"2-3"
										   }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_pass_log, 2), "tickTime":n, "gameStar":6, "difficulty":None, "difficultyDegree":degree[i]}, {'$set':AccuTimePassLog_sta_dict}, upsert = True)					
				AccuTimeLog_count += 1
		del	passPeople, passCorrectness, passtryCount, passPeople_log, passCorrectness_log, passtryCount_log
		gc.collect()	

	##step3依時間
	print("insert %s data by time" %game)
	#這裡跟Difficulty相關的欄位是用來平均難度
	allPeople, allCorrectness, allDifficulty, allTryCount = [], [], [], []	

	allPeople = columnFunc(0, int(x//y)+1, 0)
	allCorrectness = columnFunc(0, int(x//y)+1, 0)
	allDifficulty = columnFunc(0, int(x//y)+1, 0)
	allTryCount = columnFunc(0, int(x//y)+1, 0)
	
	allPeople_log, allCorrectness_log, allDifficulty_log, allTryCount_log = [], [], [], []

	allPeople_log = columnFunc(0, int(m//n)+1, 0)
	allCorrectness_log = columnFunc(0, int(m//n)+1, 0)
	allDifficulty_log = columnFunc(0, int(m//n)+1, 0)
	allTryCount_log = columnFunc(0, int(m//n)+1, 0)
	
	passPeople, passCorrectness, passDifficulty, passTryCount = [], [], [], []

	passPeople = columnFunc(0, int(x//y)+1, 0)
	passCorrectness = columnFunc(0, int(x//y)+1, 0)
	passDifficulty = columnFunc(0, int(x//y)+1, 0)
	passTryCount = columnFunc(0, int(x//y)+1, 0)
	
	passPeople_log, passCorrectness_log, passDifficulty_log, passTryCount_log = [], [], [], []

	passPeople_log = columnFunc(0, int(m//n)+1, 0)
	passCorrectness_log = columnFunc(0, int(m//n)+1, 0)
	passDifficulty_log = columnFunc(0, int(m//n)+1, 0)
	passTryCount_log = columnFunc(0, int(m//n)+1, 0)	

	allzPeople, allzCorrectness, allzDifficulty, allzTryCount = [], [], [], []

	allzPeople = columnFunc(0, int(p//q)+1, 0)
	allzCorrectness = columnFunc(0, int(p//q)+1, 0)
	allzDifficulty = columnFunc(0, int(p//q)+1, 0)
	allzTryCount = columnFunc(0, int(p//q)+1, 0)

	for star in range(0, 5):
		people, correctness, tryCount, difficulty = [], [], [], []
		
		people = columnFunc(1, int(x//y)+2, 0)
		correctness = columnFunc(1, int(x//y)+2, 0)
		tryCount = columnFunc(1, int(x//y)+2, 0)
		difficulty = columnFunc(1, int(x//y)+2, 0)
		
		people_log, correctness_log, tryCount_log, difficulty_log = [], [], [], []

		people_log = columnFunc(1, int(m//n)+2, 0)
		correctness_log = columnFunc(1, int(m//n)+2, 0)
		tryCount_log = columnFunc(1, int(m//n)+2, 0)
		difficulty_log = columnFunc(1, int(m//n)+2, 0)
		
		zPeople, zCorrectness, zDifficulty, zTryCount = [], [], [], []
		
		zPeople = columnFunc(0, int(p//q)+1, 0)
		zCorrectness = columnFunc(0, int(p//q)+1, 0)
		zDifficulty = columnFunc(0, int(p//q)+1, 0)
		zTryCount = columnFunc(0, int(p//q)+1, 0)	
		
		zPeople_log, zCorrectness_log, zDifficulty_log, zTryCount_log = [], [], [], []
		
		zPeople_log = columnFunc(0, int(u//v)+1, 0)
		zCorrectness_log = columnFunc(0, int(u//v)+1, 0)
		zDifficulty_log = columnFunc(0, int(u//v)+1, 0)
		zTryCount_log = columnFunc(0, int(u//v)+1, 0)			
		
		error = 0
		for three in ct.find({"gameCode":game, "gameStar":star, "accumulatedTime_sec":{"$gt":0, "$lte":x}}):
			try:
				a = int(three['accumulatedTime_sec'] // y)
				people[a] += 1
				correctness[a] += three['correctPercentage']
				difficulty[a] += three['difficulty']
				tryCount[a] += three['tryCount']
				
				allPeople[a] += 1
				allCorrectness[a] += three['correctPercentage']
				allDifficulty[a] += three['difficulty']
				allTryCount[a] += three['tryCount']
				
				if star > 0:
					passPeople[a] += 1
					passCorrectness[a] += three['correctPercentage']
					passDifficulty[a] += three['difficulty']
					passTryCount[a] += three['tryCount']
				
				b = int(three['logTime_sec']//n)+24
				people_log[b] += 1
				correctness_log[b] += three['correctPercentage']
				difficulty_log[b] += three['difficulty']
				tryCount_log[b]	+= three['tryCount']
				
				allPeople_log[b] += 1					
				allCorrectness_log[b] += three['correctPercentage']
				allDifficulty_log[b] += three['difficulty']
				allTryCount_log[b]	+= three['tryCount']
				
				if star > 0:
					passPeople_log[b] += 1					
					passCorrectness_log[b] += three['correctPercentage']
					passDifficulty_log[b] += three['difficulty']
					passTryCount_log[b]	+= three['tryCount']				
				
				#c = int(three['ZTime']//q)+8
				c = int(three['ZTime']//q)+1
				zPeople[c] += 1
				zCorrectness[c] += three['correctPercentage']
				zDifficulty[c] += three['difficulty']
				zTryCount[c] += three['tryCount']
				
				allzPeople[c] += 1
				allzCorrectness[c] += three['correctPercentage']
				allzDifficulty[c] += three['difficulty']
				allzTryCount[c] += three['tryCount']
				
			except:
				error += 1
				#print(error, three)
				
		#分星星
		#秒
		for seconds, i_count, i_correct, i_try, i_difficulty in zip(range(y, x+y+1, y), people, correctness, tryCount, difficulty):
			if(i_count) > 0:
				AccuTime_sta_dict = {"gameCode":game,
									 "sectionId":0,
									 "seconds":seconds,
									 "tickTime":y,
									 "gameStar":star,
									 "people":i_count,
									 "difficulty":i_difficulty/i_count,
									 "difficultyDegree":'n',
									 "avgCorrectness":i_correct/i_count,
									 "avgTryCount":i_try/i_count,
									 "step":"3-1"
									}    
				db.AccuTime_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds, "tickTime":y, "gameStar":star, "difficultyDegree":'n'}, {'$set':AccuTime_sta_dict}, upsert = True)
				AccuTime_count += 1
		#Log秒		
		for seconds_log, i_count_log, i_correct_log, i_try_log, i_difficulty_log in zip(np.arange(-2.4, m+n, n), people_log, correctness_log, tryCount_log, difficulty_log):
			if (i_count_log > 0):
				AccuTimeLog_sta_dict = {"gameCode":game,
										"sectionId":0,
										"seconds_log":round(seconds_log, 2),
										"tickTime":n,
										"gameStar":star,
										"people":i_count_log,
										"difficulty":i_difficulty_log/i_count_log,
										"difficultyDegree":'n',
										"avgCorrectness":i_correct_log/i_count_log,
										"avgTryCount":i_try_log/i_count_log,
										"step":"3-1"
									   }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_log, 2), "tickTime":n, "gameStar":star, "difficultyDegree":'n'}, {'$set':AccuTimeLog_sta_dict}, upsert = True)
				AccuTimeLog_count += 1		
		#ZTime
		#for z_seconds, z_count, z_correct, z_try, z_difficulty in zip(np.arange(-1, p+q, q), zPeople, zCorrectness, zTryCount, zDifficulty):
		for z_seconds, z_count, z_correct, z_try, z_difficulty in zip(range(-1, p+q, q), zPeople, zCorrectness, zTryCount, zDifficulty):
			if(z_count) > 0:
				AccuTimeZ_sta_dict = {"gameCode":game,
									 "sectionId":0,
									 "seconds_z":z_seconds,#round(z_seconds, 2),
									 "tickTime":q,
									 "gameStar":star,
									 "people":z_count,
									 "difficulty":z_difficulty/z_count,
									 "difficultyDegree":'n',
									 "avgCorrectness":z_correct/z_count,
									 "avgTryCount":z_try/z_count,
									 "step":"3-1"
									}    
				db.AccuTimeZ_sta.update_one({"gameCode":game, "sectionId":0, "seconds_z":z_seconds, "tickTime":q, "gameStar":star}, {'$set':AccuTimeZ_sta_dict}, upsert = True)
				AccuTimeZ_count += 1		
		
		del	people, correctness, tryCount, difficulty, people_log, correctness_log, tryCount_log, difficulty_log, zPeople, zCorrectness, zTryCount, zDifficulty			
		gc.collect()				
		
	#不分星星
	#秒
	for seconds_all, i_count_all, i_correct_all, i_difficulty_all, i_try_all in zip(range(0, x+y, y), allPeople, allCorrectness, allDifficulty, allTryCount):
		if (i_count_all > 0):
			AccuTimeAll_sta_dict = {"gameCode":game,
									"sectionId":0,
									"seconds":seconds_all,
									"tickTime":y,
									"gameStar":5,
									"people":i_count_all,
									"difficulty":i_difficulty_all/i_count_all,
									"difficultyDegree":'n',
									"avgCorrectness":i_correct_all/i_count_all,
									"avgTryCount":i_try_all/i_count_all,
									"step":"3-2"
								   }
			db.AccuTime_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds_all, "tickTime":y, "gameStar":5, "difficultyDegree":'n'}, {'$set':AccuTimeAll_sta_dict}, upsert = True)      
			AccuTime_count += 1
	#log秒
	for seconds_all_log, i_count_all_log, i_correct_all_log, i_difficulty_all_log, i_try_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, allDifficulty_log, allTryCount_log):
		if (i_count_all_log > 0):
			AccuTimeAllLog_sta_dict = {"gameCode":game,
										  "sectionId":0,
										  "seconds_log":round(seconds_all_log, 2),
										  "tickTime":n,
										  "gameStar":5,
										  "people":i_count_all_log,
										  "difficulty":i_difficulty_all_log/i_count_all_log,
										  "difficultyDegree":'n',
										  "avgCorrectness":i_correct_all_log/i_count_all_log,
										  "avgTryCount":i_try_all_log/i_count_all_log,
										  "step":"3-2"
										 }
			db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficultyDegree":'n'},{'$set':AccuTimeAllLog_sta_dict}, upsert = True)
			AccuTimeLog_count += 1 		
	del	allPeople, allCorrectness, allDifficulty, allTryCount, allPeople_log, allCorrectness_log, allDifficulty_log, allTryCount_log
	gc.collect()
	
	#只算過關
	#秒
	for seconds_pass, i_count_pass, i_correct_pass, i_difficulty_pass, i_try_pass in zip(range(0, x+y, y), passPeople, passCorrectness, passDifficulty, passTryCount):
		if (i_count_pass > 0):
			AccuTimePass_sta_dict = {"gameCode":game,
									   "sectionId":0,
									   "seconds":seconds_pass,
									   "tickTime":y,
									   "gameStar":6,	#6是有過關		
									   "people":i_count_pass,
									   "difficulty":i_difficulty_pass/i_count_pass,
									   "difficultyDegree":'n',
									   "avgCorrectness":i_correct_pass/i_count_pass,
									   "avgTryCount":i_try_pass/i_count_pass,
									   "step":"3-3"
									  }
			db.AccuTime_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds_pass, "tickTime":y, "gameStar":6, "difficultyDegree":'n'}, {'$set':AccuTimePass_sta_dict}, upsert = True)      
			AccuTime_count += 1
	#log秒
	for seconds_pass_log, i_count_pass_log, i_correct_pass_log, i_difficulty_pass_log, i_try_pass_log in zip(np.arange(-2.4, m+n, n), passPeople_log, passCorrectness_log, passDifficulty_log, passTryCount_log):
		if (i_count_pass_log > 0):
			AccuTimePassLog_sta_dict = {"gameCode":game,
										"sectionId":0,
										"seconds_log":round(seconds_pass_log, 2),
										"tickTime":n,
										"gameStar":6,		#6是有過關
										"people":i_count_pass_log,
										"difficulty":i_difficulty_pass_log/i_count_pass_log,
										"difficultyDegree":'n',
										"avgCorrectness":i_correct_pass_log/i_count_pass_log,
										"avgTryCount":i_try_pass_log/i_count_pass_log,
										"step":"3-3"
									   }
			db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_pass_log, 2), "tickTime":n, "gameStar":6, "difficultyDegree":'n'},{'$set':AccuTimePassLog_sta_dict}, upsert = True)
			AccuTimeLog_count += 1
			
	for seconds_z_all, i_count_z_all, i_correct_z_all, i_difficulty_z_all, i_try_z_all in zip(range(-1, p+q, q), allzPeople, allzCorrectness, allzDifficulty, allzTryCount):
		if (i_count_z_all > 0):
			AccuTimeZAll_sta_dict = {"gameCode":game,
									"sectionId":0,
									"seconds_z":seconds_z_all,
									"tickTime":q,
									"gameStar":5,
									"people":i_count_z_all,
									"difficulty":i_difficulty_z_all/i_count_z_all,
									"difficultyDegree":'n',
									"avgCorrectness":i_correct_z_all/i_count_z_all,
									"avgTryCount":i_try_z_all/i_count_z_all,
									"step":"3-2"
								   }
			db.AccuTimeZ_sta.update_one({"gameCode":game, "sectionId":0, "seconds_z":seconds_z_all, "tickTime":q, "gameStar":5, "difficultyDegree":'n'}, {'$set':AccuTimeZAll_sta_dict}, upsert = True)      
			AccuTime_count += 1			
			
	del	passPeople, passCorrectness ,passDifficulty, passTryCount, passPeople_log, passCorrectness_log, passDifficulty_log, passTryCount_log, allzPeople, allzCorrectness, allzDifficulty, allzTryCount
	gc.collect()

endTime = time.time()

passTime = endTime - startTime
print(passTime)