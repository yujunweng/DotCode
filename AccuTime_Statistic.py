import numpy as np
import pandas as pd
import traceback
import os
import time
import datetime
import gc
import PaperCommon as pc
	

if __name__ == '__main__':
	'''Insert average correct percentage every y seconds from AccuTime to AccuTime_sta'''
	choice = input("開始執行程式(y)Yes(other)No：")
	if choice.upper() != 'Y':
		os._exit(0)
		
	startTime = time.time() 	
		
	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數
	sectionDegree = pc.sections_degrees()
	playerDegree = pc.players_degrees()	
	
	database = 'dotCode'
	game = 'Duck'
	db = pc.clientDB(database)

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
	ct = pc.clientCT(database, collection)
	#1.依關卡
	ct.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('accuTime_sec', 1)])
	ct.create_index([('sectionId', 1), ('gameStar', 1), ('accuTime_sec', 1)])
	#2.依難度
	ct.create_index([('gameCode', 1), ('eloDegree', 1), ('gameStar', 1),('accuTime_sec', 1)])
	ct.create_index([('eloDegree', 1), ('gameStar', 1),('accuTime_sec', 1)])
	#3.依時間
	ct.create_index([('gameCode', 1), ('accuTime_sec', 1)])
	ct.create_index([('accuTime_sec', 1)])
	#4.依玩家等級
	ct.create_index([('gameCode', 1), ('playerDegree_kmeans', 1), ('gameStar', 1),('accuTime_sec', 1)])
	ct.create_index([('playerDegree_kmeans', 1), ('gameStar', 1),('accuTime_sec', 1)])
	
	#新資料庫建索引
	#1.依關卡
	db.AccuTime_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1)])
	db.AccuTimeLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1)])
	#2.依難度
	db.AccuTime_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('eloDegree', 1)])
	db.AccuTimeLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('eloDegree', 1)])
	#3.依時間(AccuTime_sta與AccuTimeLog_sta不建，與難度相同)
	db.AccuTimeZ_sta.create_index([('gameCode', 1), ('seconds_z', 1), ('tickTime', 1), ('gameStar', 1)])

	AccuTime_count = 0
	AccuTimeLog_count = 0
	AccuTimeZ_count = 0
	maxSection = pc.find_maxSection(game)
	sectionId, item_difficulty, eloDegree = pc.add_difficulty(game, 1)
	
	##step1依關卡)
	print("insert {} data by section".format(game))
	for section in range(1, maxSection+1):
		allPeople, allCorrectness, allTryCount = [], [], []
		allPeople = pc.create_lists(1, int(x//y)+2, 0)
		allCorrectness = pc.create_lists(1, int(x//y)+2, 0)
		allTryCount = pc.create_lists(1, int(x//y)+2, 0)
		
		allPeople_log, allCorrectness_log, allTryCount_log = [], [], []
		allPeople_log = pc.create_lists(0, int(m//n)+1, 0)
		allCorrectness_log = pc.create_lists(0, int(m//n)+1, 0)
		allTryCount_log = pc.create_lists(0, int(m//n)+1, 0)
		
		passPeople, passCorrectness, passTryCount = [], [], []
		passPeople = pc.create_lists(1, int(x//y)+2, 0)
		passCorrectness = pc.create_lists(1, int(x//y)+2, 0)
		passTryCount = pc.create_lists(1, int(x//y)+2, 0)
		
		passPeople_log,passCorrectness_log, passTryCount_log = [], [], []
		passPeople_log = pc.create_lists(0, int(m//n)+1, 0)
		passCorrectness_log = pc.create_lists(0, int(m//n)+1, 0)
		passTryCount_log = pc.create_lists(0, int(m//n)+1, 0)
		
		for star in range(0, 5):
			people, correctness, tryCount = [], [], []
			people = pc.create_lists(1, int(x//y)+2, 0)
			correctness = pc.create_lists(1, int(x//y)+2, 0)
			tryCount = pc.create_lists(1, int(x//y)+2, 0)
			
			people_log, correctness_log, tryCount_log= [], [], []
			people_log = pc.create_lists(0, int(m//n)+1, 0)
			correctness_log = pc.create_lists(0, int(m//n)+1, 0)
			tryCount_log = pc.create_lists(0, int(m//n)+1, 0)
			
			for one in ct.find({"gameCode":game, "sectionId":section, "gameStar":star, "accuTime_sec":{"$gt":0, "$lte":x}}):
				try:
					a = int(one['accuTime_sec']//y)
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
					
					b = int(one['logAccuTime_sec']//n)+24
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
					traceback.print_exc()
				
			#分星星
			#秒
			for seconds, i_count, i_correct, i_try in zip(range(y, x+y+1, y), people, correctness, tryCount):
				if i_count > 0:
					#print("seconds:", seconds, "i_count:", i_count, "try", i_try, "i_correct:", i_correct/i_count)
					#os.system("pause")
					AccuTime_sta_dict = {"gameCode":game,
										 "sectionId":section,
										 "seconds":seconds,
										 "tickTime":y,
										 "gameStar":star,
										 "people":i_count,
										 "difficulty":item_difficulty[section-1],
										 "eloDegree":eloDegree[section-1],
										 "avgCorrectness":i_correct/i_count,
										 "avgTryCount":i_try/i_count,
										 "step":"1-1"
										}    
					db.AccuTime_sta.update_one({"gameCode":game, "sectionId":section, "seconds":seconds, "tickTime":y, "gameStar":star}, {'$set':AccuTime_sta_dict}, upsert = True)
					AccuTime_count += 1
			
			#Log秒		
			for seconds_log, i_count_log, i_correct_log, i_try_log in zip(np.arange(-2.4, m+n, n), people_log, correctness_log, tryCount_log):
				if i_count_log > 0:
					AccuTimeLog_sta_dict = {"gameCode":game,
											"sectionId":section,
											"seconds_log":round(seconds_log, 2),
											"tickTime":n,
											"gameStar":star,
											"people":i_count_log,
											"difficulty":item_difficulty[section-1],
											"eloDegree":eloDegree[section-1],
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
										 "eloDegree":eloDegree[section-1],
										 "avgCorrectness":i_correct_all/i_count_all,
										 "avgTryCount":i_try_all/i_count_all,
										 "step":"1-2"
										}
				db.AccuTime_sta.update_one({"gameCode":game, "sectionId":section, "seconds":seconds_all, "tickTime":y, "gameStar":5}, {'$set':AccuTimeAll_sta_dict}, upsert = True)
				AccuTime_count += 1


		#log秒
		for seconds_all_log, i_count_all_log, i_correct_all_log, i_try_all_log, in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, allTryCount_log):
			if i_count_all_log > 0:
				AccuTimeAllLog_sta_dict = {"gameCode":game,
										   "sectionId":section,
										   "seconds_log":round(seconds_all_log, 2),
										   "tickTime":n,
										   "gameStar":5,	#5是不分星星數
										   "people":i_count_all_log,
										   "difficulty" : item_difficulty[section-1],
										   "eloDegree" : eloDegree[section-1],
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
										 "eloDegree":eloDegree[section-1],
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
										   "eloDegree" : eloDegree[section-1],
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
	playerDegree = [num for num in range ]
	for i in range(0, len(degree)):
		allPeople, allCorrectness, alltryCount = [], [], []
		allPeople = pc.create_lists(1, int(x//y)+2, 0)
		allCorrectness = pc.create_lists(1, int(x//y)+2, 0)
		alltryCount = pc.create_lists(1, int(x//y)+2, 0)
		
		allPeople_log, allCorrectness_log, alltryCount_log = [], [], []
		allPeople_log = pc.create_lists(0, int(m//n)+1, 0)
		allCorrectness_log = pc.create_lists(0, int(m//n)+1, 0)
		alltryCount_log = pc.create_lists(0, int(m//n)+1, 0)
		
		passPeople, passCorrectness, passtryCount = [], [], []
		passPeople = pc.create_lists(1, int(x//y)+2, 0)
		passCorrectness = pc.create_lists(1, int(x//y)+2, 0)
		passtryCount = pc.create_lists(1, int(x//y)+2, 0)
		
		passPeople_log, passCorrectness_log, passtryCount_log = [], [], []
		passPeople_log = pc.create_lists(0, int(m//n)+1, 0)
		passCorrectness_log = pc.create_lists(0, int(m//n)+1, 0)
		passtryCount_log = pc.create_lists(0, int(m//n)+1, 0)
		
		for star in range(0, 5):
			people, correctness, tryCount = [], [], []
			people = pc.create_lists(1, int(x//y)+2, 0)
			correctness = pc.create_lists(1, int(x//y)+2, 0)
			tryCount = pc.create_lists(1, int(x//y)+2, 0)
			
			people_log, correctness_log, tryCount_log = [], [], [] 
			people_log = pc.create_lists(1, int(m//n)+2, 0)
			correctness_log = pc.create_lists(1, int(m//n)+2, 0)
			tryCount_log = pc.create_lists(1, int(m//n)+2, 0)
			
			for two in ct.find({"gameCode":game, "eloDegree":degree[i], "gameStar":star, "accuTime_sec":{"$gt":0, "$lte":x}}):
				try:
					a = int(two['accuTime_sec'] // y)
	
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
					
					b = int(two['logAccuTime_sec']//n)+24
					
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
				if i_count > 0:
					#print("seconds:", seconds, "i_count:", i_count, "try", i_try, "correct:", i_correct/i_count)
					#os.system("pause")
					AccuTime_sta_dict = {"gameCode":game,
										 "sectionId":0,
										 "seconds":seconds,
										 "tickTime":y,
										 "gameStar":star,
										 "people":i_count,
										 "difficulty":None,
										 "eloDegree":degree[i],
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
												"eloDegree":degree[i]
												}, 
												{'$set': AccuTime_sta_dict}, 
												upsert = True
											   )
					AccuTime_count += 1
			for seconds_log, i_count_log, i_correct_log, i_try_log in zip(np.arange(-2.4, m+n, n), people_log, correctness_log, tryCount_log):
				if i_count_log > 0:
					AccuTimeLog_sta_dict = {"gameCode":game,
											"sectionId":0,
											"seconds_log":round(seconds_log, 2),
											"tickTime":n,
											"gameStar":star,
											"people":i_count_log,
											"difficulty":None,
											"eloDegree":degree[i],
											"avgCorrectness":i_correct_log/i_count_log,
											"avgTryCount":i_try_log/i_count_log,
											"step":"2-1"
										   }
					db.AccuTimeLog_sta.update_one({"gameCode":game, "seconds_log":round(seconds_log, 2), "tickTime":n, "gameStar":star, "difficulty":None, "eloDegree":degree[i]}, {'$set':AccuTimeLog_sta_dict}, upsert = True)
					AccuTimeLog_count += 1
			del	people, correctness, tryCount, people_log, correctness_log, tryCount_log			
			gc.collect()
		
		#不分星
		#秒
		for seconds_all, i_count_all, i_correct_all, i_try_all in zip(range(y, x+y+1, y), allPeople, allCorrectness, alltryCount):
			if i_count_all > 0:
				#print("seconds:", seconds, "i_count:", i_count, "correct:", correct)
				AccuTimeALL_sta_dict = {"gameCode" : game,
										"sectionId": 0,
										"seconds": seconds_all,
										"tickTime" : y,
										"gameStar" : 5,
										"people" : i_count_all,
										"difficulty" : None,
										"eloDegree" : degree[i],
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
											"eloDegree":degree[i]
										    },
											{'$set': AccuTimeALL_sta_dict},
											upsert = True
										   )
				AccuTime_count += 1
		#log秒
		for seconds_all_log, i_count_all_log, i_correct_all_log, i_try_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, alltryCount_log):
			if i_count_all_log > 0:
				AccuTimeAllLog_sta_dict = {"gameCode":game,
										   "sectionId":0,
										   "seconds_log":round(seconds_all_log, 2),
										   "tickTime":n,
										   "gameStar":5,
										   "people":i_count_all_log,
										   "difficulty":None,
										   "eloDegree":degree[i],
										   "avgCorrectness":i_correct_all_log/i_count_all_log,
										   "avgTryCount":i_try_all_log/i_count_all_log,
										   "step":"2-2"
										  }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficulty":None, "eloDegree":degree[i]}, {'$set': AccuTimeAllLog_sta_dict}, upsert = True)					
				AccuTimeLog_count += 1
		del	allPeople, allCorrectness, alltryCount, allPeople_log, allCorrectness_log, alltryCount_log
		gc.collect()
		
		#只算有過關
		#秒
		for seconds_pass, i_count_pass, i_correct_pass, i_try_pass in zip(range(y, x+y+1, y), passPeople, passCorrectness, passtryCount):
			if i_count_pass > 0:
				#print("seconds:", seconds, "i_count:", i_count, "correct:", correct)
				AccuTimePass_sta_dict = {"gameCode" : game,
										 "sectionId": 0,
										 "seconds": seconds_pass,
										 "tickTime" : y,
										 "gameStar" : 6,
										 "people" : i_count_pass,
										 "difficulty" : None,
										 "eloDegree" : degree[i],
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
											"eloDegree":degree[i]
										    },
											{'$set': AccuTimePass_sta_dict},
											upsert = True
										  )
				AccuTime_count += 1
		#log秒
		for seconds_pass_log, i_count_pass_log, i_correct_pass_log, i_try_pass_log in zip(np.arange(-2.4, m+n, n), passPeople_log, passCorrectness_log, passtryCount_log):
			if i_count_pass_log > 0:
				AccuTimePassLog_sta_dict = {"gameCode":game,
											"sectionId":0,
											"seconds_log":round(seconds_pass_log, 2),
											"tickTime":n,
											"gameStar":6,
											"people":i_count_pass_log,
											"difficulty":None,
											"eloDegree":degree[i],
											"avgCorrectness":i_correct_pass_log/i_count_pass_log,
											"avgTryCount":i_try_pass_log/i_count_pass_log,
											"step":"2-3"
										   }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_pass_log, 2), "tickTime":n, "gameStar":6, "difficulty":None, "eloDegree":degree[i]}, {'$set':AccuTimePassLog_sta_dict}, upsert = True)					
				AccuTimeLog_count += 1
		del	passPeople, passCorrectness, passtryCount, passPeople_log, passCorrectness_log, passtryCount_log
		gc.collect()	
	
	##step3依時間
	print("insert %s data by time" %game)
	#這裡跟Difficulty相關的欄位是用來平均難度
	allPeople, allCorrectness, allDifficulty, allTryCount = [], [], [], []	

	allPeople = pc.create_lists(0, int(x//y)+1, 0)
	allCorrectness = pc.create_lists(0, int(x//y)+1, 0)
	allDifficulty = pc.create_lists(0, int(x//y)+1, 0)
	allTryCount = pc.create_lists(0, int(x//y)+1, 0)
	
	allPeople_log, allCorrectness_log, allDifficulty_log, allTryCount_log = [], [], [], []

	allPeople_log = pc.create_lists(0, int(m//n)+1, 0)
	allCorrectness_log = pc.create_lists(0, int(m//n)+1, 0)
	allDifficulty_log = pc.create_lists(0, int(m//n)+1, 0)
	allTryCount_log = pc.create_lists(0, int(m//n)+1, 0)
	
	passPeople, passCorrectness, passDifficulty, passTryCount = [], [], [], []

	passPeople = pc.create_lists(0, int(x//y)+1, 0)
	passCorrectness = pc.create_lists(0, int(x//y)+1, 0)
	passDifficulty = pc.create_lists(0, int(x//y)+1, 0)
	passTryCount = pc.create_lists(0, int(x//y)+1, 0)
	
	passPeople_log, passCorrectness_log, passDifficulty_log, passTryCount_log = [], [], [], []

	passPeople_log = pc.create_lists(0, int(m//n)+1, 0)
	passCorrectness_log = pc.create_lists(0, int(m//n)+1, 0)
	passDifficulty_log = pc.create_lists(0, int(m//n)+1, 0)
	passTryCount_log = pc.create_lists(0, int(m//n)+1, 0)	

	allzPeople, allzCorrectness, allzDifficulty, allzTryCount = [], [], [], []

	allzPeople = pc.create_lists(0, int(p//q)+1, 0)
	allzCorrectness = pc.create_lists(0, int(p//q)+1, 0)
	allzDifficulty = pc.create_lists(0, int(p//q)+1, 0)
	allzTryCount = pc.create_lists(0, int(p//q)+1, 0)

	for star in range(0, 5):
		people, correctness, tryCount, difficulty = [], [], [], []
		
		people = pc.create_lists(1, int(x//y)+2, 0)
		correctness = pc.create_lists(1, int(x//y)+2, 0)
		tryCount = pc.create_lists(1, int(x//y)+2, 0)
		difficulty = pc.create_lists(1, int(x//y)+2, 0)
		
		people_log, correctness_log, tryCount_log, difficulty_log = [], [], [], []

		people_log = pc.create_lists(1, int(m//n)+2, 0)
		correctness_log = pc.create_lists(1, int(m//n)+2, 0)
		tryCount_log = pc.create_lists(1, int(m//n)+2, 0)
		difficulty_log = pc.create_lists(1, int(m//n)+2, 0)
		
		zPeople, zCorrectness, zDifficulty, zTryCount = [], [], [], []
		
		zPeople = pc.create_lists(0, int(p//q)+1, 0)
		zCorrectness = pc.create_lists(0, int(p//q)+1, 0)
		zDifficulty = pc.create_lists(0, int(p//q)+1, 0)
		zTryCount = pc.create_lists(0, int(p//q)+1, 0)	
		
		zPeople_log, zCorrectness_log, zDifficulty_log, zTryCount_log = [], [], [], []
		
		zPeople_log = pc.create_lists(0, int(u//v)+1, 0)
		zCorrectness_log = pc.create_lists(0, int(u//v)+1, 0)
		zDifficulty_log = pc.create_lists(0, int(u//v)+1, 0)
		zTryCount_log = pc.create_lists(0, int(u//v)+1, 0)			
		
		error = 0
		for three in ct.find({"gameCode":game, "gameStar":star, "accuTime_sec":{"$gt":0, "$lte":x}}):
			try:
				a = int(three['accuTime_sec'] // y)
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
				
				b = int(three['logAccuTime_sec']//n)+24
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
			if i_count > 0:
				AccuTime_sta_dict = {"gameCode":game,
									 "sectionId":0,
									 "seconds":seconds,
									 "tickTime":y,
									 "gameStar":star,
									 "people":i_count,
									 "difficulty":i_difficulty/i_count,
									 "eloDegree":'n',
									 "avgCorrectness":i_correct/i_count,
									 "avgTryCount":i_try/i_count,
									 "step":"3-1"
									}    
				db.AccuTime_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds, "tickTime":y, "gameStar":star, "eloDegree":'n'}, {'$set':AccuTime_sta_dict}, upsert = True)
				AccuTime_count += 1
		#Log秒		
		for seconds_log, i_count_log, i_correct_log, i_try_log, i_difficulty_log in zip(np.arange(-2.4, m+n, n), people_log, correctness_log, tryCount_log, difficulty_log):
			if i_count_log > 0:
				AccuTimeLog_sta_dict = {"gameCode":game,
										"sectionId":0,
										"seconds_log":round(seconds_log, 2),
										"tickTime":n,
										"gameStar":star,
										"people":i_count_log,
										"difficulty":i_difficulty_log/i_count_log,
										"eloDegree":'n',
										"avgCorrectness":i_correct_log/i_count_log,
										"avgTryCount":i_try_log/i_count_log,
										"step":"3-1"
									   }
				db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_log, 2), "tickTime":n, "gameStar":star, "eloDegree":'n'}, {'$set':AccuTimeLog_sta_dict}, upsert = True)
				AccuTimeLog_count += 1		
		#ZTime
		#for z_seconds, z_count, z_correct, z_try, z_difficulty in zip(np.arange(-1, p+q, q), zPeople, zCorrectness, zTryCount, zDifficulty):
		for z_seconds, z_count, z_correct, z_try, z_difficulty in zip(range(-1, p+q, q), zPeople, zCorrectness, zTryCount, zDifficulty):
			if z_count > 0:
				AccuTimeZ_sta_dict = {"gameCode":game,
									 "sectionId":0,
									 "seconds_z":z_seconds,#round(z_seconds, 2),
									 "tickTime":q,
									 "gameStar":star,
									 "people":z_count,
									 "difficulty":z_difficulty/z_count,
									 "eloDegree":'n',
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
		if i_count_all > 0:
			AccuTimeAll_sta_dict = {"gameCode":game,
									"sectionId":0,
									"seconds":seconds_all,
									"tickTime":y,
									"gameStar":5,
									"people":i_count_all,
									"difficulty":i_difficulty_all/i_count_all,
									"eloDegree":'n',
									"avgCorrectness":i_correct_all/i_count_all,
									"avgTryCount":i_try_all/i_count_all,
									"step":"3-2"
								   }
			db.AccuTime_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds_all, "tickTime":y, "gameStar":5, "eloDegree":'n'}, {'$set':AccuTimeAll_sta_dict}, upsert = True)      
			AccuTime_count += 1
	#log秒
	for seconds_all_log, i_count_all_log, i_correct_all_log, i_difficulty_all_log, i_try_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, allDifficulty_log, allTryCount_log):
		if i_count_all_log > 0:
			AccuTimeAllLog_sta_dict = {"gameCode":game,
										  "sectionId":0,
										  "seconds_log":round(seconds_all_log, 2),
										  "tickTime":n,
										  "gameStar":5,
										  "people":i_count_all_log,
										  "difficulty":i_difficulty_all_log/i_count_all_log,
										  "eloDegree":'n',
										  "avgCorrectness":i_correct_all_log/i_count_all_log,
										  "avgTryCount":i_try_all_log/i_count_all_log,
										  "step":"3-2"
										 }
			db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "eloDegree":'n'},{'$set':AccuTimeAllLog_sta_dict}, upsert = True)
			AccuTimeLog_count += 1 		
	del	allPeople, allCorrectness, allDifficulty, allTryCount, allPeople_log, allCorrectness_log, allDifficulty_log, allTryCount_log
	gc.collect()
	
	#只算過關
	#秒
	for seconds_pass, i_count_pass, i_correct_pass, i_difficulty_pass, i_try_pass in zip(range(0, x+y, y), passPeople, passCorrectness, passDifficulty, passTryCount):
		if i_count_pass > 0:
			AccuTimePass_sta_dict = {"gameCode":game,
									   "sectionId":0,
									   "seconds":seconds_pass,
									   "tickTime":y,
									   "gameStar":6,	#6是有過關		
									   "people":i_count_pass,
									   "difficulty":i_difficulty_pass/i_count_pass,
									   "eloDegree":'n',
									   "avgCorrectness":i_correct_pass/i_count_pass,
									   "avgTryCount":i_try_pass/i_count_pass,
									   "step":"3-3"
									  }
			db.AccuTime_sta.update_one({"gameCode":game, "sectionId":0, "seconds":seconds_pass, "tickTime":y, "gameStar":6, "eloDegree":'n'}, {'$set':AccuTimePass_sta_dict}, upsert = True)
			AccuTime_count += 1
	#log秒
	for seconds_pass_log, i_count_pass_log, i_correct_pass_log, i_difficulty_pass_log, i_try_pass_log in zip(np.arange(-2.4, m+n, n), passPeople_log, passCorrectness_log, passDifficulty_log, passTryCount_log):
		if i_count_pass_log > 0:
			AccuTimePassLog_sta_dict = {"gameCode":game,
										"sectionId":0,
										"seconds_log":round(seconds_pass_log, 2),
										"tickTime":n,
										"gameStar":6,		#6是有過關
										"people":i_count_pass_log,
										"difficulty":i_difficulty_pass_log/i_count_pass_log,
										"eloDegree":'n',
										"avgCorrectness":i_correct_pass_log/i_count_pass_log,
										"avgTryCount":i_try_pass_log/i_count_pass_log,
										"step":"3-3"
									   }
			db.AccuTimeLog_sta.update_one({"gameCode":game, "sectionId":0, "seconds_log":round(seconds_pass_log, 2), "tickTime":n, "gameStar":6, "eloDegree":'n'},{'$set':AccuTimePassLog_sta_dict}, upsert = True)
			AccuTimeLog_count += 1
			
	for seconds_z_all, i_count_z_all, i_correct_z_all, i_difficulty_z_all, i_try_z_all in zip(range(-1, p+q, q), allzPeople, allzCorrectness, allzDifficulty, allzTryCount):
		if i_count_z_all > 0:
			AccuTimeZAll_sta_dict = {"gameCode":game,
									"sectionId":0,
									"seconds_z":seconds_z_all,
									"tickTime":q,
									"gameStar":5,
									"people":i_count_z_all,
									"difficulty":i_difficulty_z_all/i_count_z_all,
									"eloDegree":'n',
									"avgCorrectness":i_correct_z_all/i_count_z_all,
									"avgTryCount":i_try_z_all/i_count_z_all,
									"step":"3-3"
								   }
			db.AccuTimeZ_sta.update_one({"gameCode":game, "sectionId":0, "seconds_z":seconds_z_all, "tickTime":q, "gameStar":5, "eloDegree":'n'}, {'$set':AccuTimeZAll_sta_dict}, upsert = True)      
			AccuTime_count += 1			
			
	del	passPeople, passCorrectness ,passDifficulty, passTryCount, passPeople_log, passCorrectness_log, passDifficulty_log, passTryCount_log, allzPeople, allzCorrectness, allzDifficulty, allzTryCount
	gc.collect()
	


pc.pass_time(startTime, time.time())