from pymongo import MongoClient
import numpy as np
import pandas as pd
import traceback
import os
import time
import datetime
import gc
import json
import PaperCommon as pc

if __name__ == '__main__':
	choice = input("開始執行程式(y)Yes(other)No：")
	if choice.upper() != 'Y':
		os.exit_(0)

	database = 'dotCode'
	collection = 'FirstRecord'
	
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)	
	
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	playerKmeansDegree = [0, 1]
	
	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數
	FirstRecord_count = 0
	FirstRecordLog_count = 0
	FirstRecordZ_count = 0
	
	eloChoice = input("請選擇elo分級欄位\n(1)elo1:0.01\n(2)elo2:0.01-0.002n\n(3)elo3：0.02\n：")
	if eloChoice == 2:
		sectionId2, itemDifficulty2, difficultyDegree2 = pc.add_difficulty(game, '2')
	elif eloChoice == 3:
		sectionId3, itemDifficulty3, difficultyDegree3 = pc.add_difficulty(game, '3')
	else:
		sectionId, itemDifficulty, difficultyDegree = pc.add_difficulty(game, '1')
	
	kmeansDegree = pc.bubbleSort(list(set(difficultyDegree)))
	
	#一般秒用x, y，log秒用m, n
	x = 57600
	y = 1
	m = 20
	n = 0.1
	minZ = -1.1
	maxZ = 333.4
	intervalZ = 0.01
	
	ct.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('gameTime_sec', 1)])		
	ct.create_index([('gameCode', 1), ('sectionId', 1), ('gameTime_sec', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree_kmeans', 1), ('gameStar', 1),  ('gameTime_sec', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree_kmeans', 1), ('gameTime_sec', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree2', 1), ('gameStar', 1),  ('gameTime_sec', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree2', 1), ('gameTime_sec', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree3', 1), ('gameStar', 1),  ('gameTime_sec', 1)])
	ct.create_index([('gameCode', 1), ('difficultyDegree3', 1), ('gameTime_sec', 1)])
		
	startTime = time.time()
	
	if "FirstRecord_sta" in db.list_collection_names():
		insertMode = 0
	else:
		insertMode = 1
	
	##step1依關卡
	print("insert %s data by section" %game)
	for section in range(1, maxSection+1):
		totalPeo = ct.count_documents({"sectionId":section})
		cumulativePeo = 0
		allPeople = pc.create_lists(0, int(x//y+2), 0)
		allCorrectness = pc.create_lists(0, int(x//y+2), 0)
		
		cumulativePeo_log = 0
		allPeople_log = pc.create_lists(0, int(m//n+2), 0)
		allCorrectness_log = pc.create_lists(0, int(m//n+2), 0)

		for star in range(0, 5):
			people = pc.create_lists(0, int(x//y+2), 0)
			starCorrectness = pc.create_lists(0, int(x//y+2), 0)
			
			people_log = pc.create_lists(0, int(m//n+2), 0)
			starCorrectness_log = pc.create_lists(0, int(m//n+2), 0)
			
			for one in ct.find({"gameCode":game, "sectionId":section, "gameStar":star, "gameTime_sec":{"$gt":0, "$lte":x}}):
				a = int(one['gameTime_sec']//y)
				people[a] += 1
				allPeople[a] += 1
				
				b = int(one['logGameTime_sec']//n)+24
				people_log[b] += 1
				allPeople_log[b] += 1
				
				correctness = 1 if(one['gameStar'] > 0) else 0

				starCorrectness[a] += correctness
				allCorrectness[a] += correctness
				
				starCorrectness_log[b] += correctness
				allCorrectness_log[b] += correctness
				
			#分星星
			#秒
			for dseconds, dpeo, dcorrect, in zip(range(0, x+y, y), people, starCorrectness):
				if dpeo > 0:
					FirstRecord_sta_dict = {"gameCode":game,
											"sectionId":section,
											"seconds":dseconds,
											"tickTime":y,
											"gameStar":star,
											"people":dpeo,
											"difficulty":itemDifficulty[section-1],
											"difficultyDegree_kmeans":difficultyDegree[section-1],
											#"difficulty2":itemDifficulty2[section-1],
											#"difficultyDegree2":difficultyDegree2[section-1],											
											#"difficulty3":itemDifficulty3[section-1],
											#"difficultyDegree3":difficultyDegree3[section-1],											
											"avgCorrectness":dcorrect/dpeo
										   }
					if insertMode:	
						db.FirstRecord_sta.insert_many([FirstRecord_sta_dict])
					else:
						db.FirstRecord_sta.update_one({"gameCode":game, "sectionId":section, "gameStar":star, "tickTime":y, "seconds":dseconds},{'$set':FirstRecord_sta_dict}, upsert = True)
					FirstRecord_count += 1
			
			#Log秒		
			for dseconds_log, dpeo_log, dcorrect_log, in zip(np.arange(-2.4, m+n, n), people_log, starCorrectness_log):
				if dpeo_log > 0:
					FirstRecordLog_sta_dict = {"gameCode":game,
											   "sectionId":section,
											   "seconds_log":round(dseconds_log, 2),
											   "tickTime":n,
											   "gameStar":star,
											   "people":dpeo_log,
											   "difficulty":itemDifficulty[section-1],
											   "difficultyDegree_kmeans":difficultyDegree[section-1],
											   #"difficulty2":itemDifficulty2[section-1],
											   #"difficultyDegree2":difficultyDegree2[section-1],
											   #"difficulty3":itemDifficulty3[section-1],
											   #"difficultyDegree3":difficultyDegree3[section-1],											   
											   "avgCorrectness":dcorrect_log/dpeo_log
											  }
					if insertMode:
						db.FirstRecordLog_sta.insert_many([FirstRecordLog_sta_dict])
					else:	
						db.FirstRecordLog_sta.update_one({"gameCode":game, "sectionId": section, "gameStar":star, "tickTime":n, "seconds_log":round(dseconds_log, 2)},{'$set':FirstRecordLog_sta_dict}, upsert = True)
					FirstRecordLog_count += 1		
			del	people, starCorrectness, people_log, starCorrectness_log			
			gc.collect()
		
		#不分星星
		#秒
		for seconds_all, peo_all, correct_all, in zip(range(0, x+y, y), allPeople, allCorrectness):
			if peo_all > 0:
				cumulativePeo += peo_all
				FirstRecordAll_sta_dict = {"gameCode":game,
										   "sectionId":section,
										   "seconds":seconds_all,
										   "tickTime":y,
										   "gameStar":5,
										   "people":peo_all,
										   "difficulty":itemDifficulty[section-1],
										   "difficultyDegree_kmeans":difficultyDegree[section-1],
										   #"difficulty2":itemDifficulty2[section-1],
										   #"difficultyDegree2":difficultyDegree2[section-1],
										   #"difficulty3":itemDifficulty3[section-1],
										   #"difficultyDegree3":difficultyDegree3[section-1],
										   "avgCorrectness":correct_all/peo_all,
										   "cumulativePeo":cumulativePeo,
										   "cumulativePeoPercent":'%.4f' %(cumulativePeo/totalPeo)
									      }
				if insertMode:
					db.FirstRecord_sta.insert_many([FirstRecordAll_sta_dict])
				else:	
					db.FirstRecord_sta.update_one({"gameCode":game, "sectionId":section, "gameStar":5, "tickTime":y, "seconds": seconds_all},{'$set': FirstRecordAll_sta_dict}, upsert = True)      
				FirstRecord_count += 1
		db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1)])
				
		#log秒
		for seconds_all_log, peo_all_log, correct_all_log, in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log):
			if peo_all_log > 0:
				cumulativePeo_log += peo_all_log
				FirstRecordAllLog_sta_dict = {"gameCode":game,
											  "sectionId":section,
											  "seconds_log":round(seconds_all_log, 2),
											  "tickTime":n,
											  "gameStar":5,
											  "people":peo_all_log,
											  "difficulty":itemDifficulty[section-1],
											  "difficultyDegree_kmeans":difficultyDegree[section-1],
											  #"difficulty2":itemDifficulty2[section-1],
											  #"difficultyDegree2":difficultyDegree2[section-1],
											  #"difficulty3":itemDifficulty3[section-1],
											  #"difficultyDegree3":difficultyDegree3[section-1],											  
											  "avgCorrectness":correct_all_log/peo_all_log,
											  "cumulativePeo_log":cumulativePeo_log,
											  "cumulativePeoPercent_log":'%.4f' %(cumulativePeo_log/totalPeo)
											 }
				if insertMode:
					db.FirstRecordLog_sta.insert_many([FirstRecordAllLog_sta_dict])
				else:	
					db.FirstRecordLog_sta.update_one({"gameCode":game, "sectionId":section, "gameStar":5, "tickTime":n, "seconds_log":round(seconds_all_log, 2)},{'$set':FirstRecordAllLog_sta_dict}, upsert = True)
				FirstRecordLog_count += 1 		
		db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1)])
	
	
	##step2依難度等級
	print("insert %s data by difficulty degree" %game)
	for i in range(0, len(kmeansDegree)):
		cumulativePeo = 0
		allPeople = pc.create_lists(0, int(x//y+2), 0)
		allCorrectness = pc.create_lists(0, int(x//y+2), 0)
		
		cumulativePeo_log = 0
		allPeople_log = pc.create_lists(0, int(m//n+2), 0)
		allCorrectness_log = pc.create_lists(0, int(m//n+2), 0)
		
		cumulativePeo_z = 0
		allPeople_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)
		allCorrectness_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)
		allStars_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)	
		for star in range(0, 5):
			people = pc.create_lists(0, int(x//y+2), 0)
			starCorrectness = pc.create_lists(0, int(x//y+2), 0)
			
			people_log = pc.create_lists(0, int(m//n+2), 0)
			starCorrectness_log = pc.create_lists(0, int(m//n+2), 0)
			
			people_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)
			starCorrectness_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)			
			
			if eloChoice == '2':
				query = {"gameCode":game, "difficultyDegree2":degree[i], "gameStar":star, "gameTime_sec":{"$gt":0, "$lte":x}}
			elif eloChoice == '3':
				query = {"gameCode":game, "difficultyDegree3":degree[i], "gameStar":star, "gameTime_sec":{"$gt":0, "$lte":x}}
			else:
				query = {"gameCode":game, "difficultyDegree_kmeans":kmeansDegree[i], "gameStar":star, "gameTime_sec":{"$gt":0, "$lte":x}}
			for two in ct.find(query):					  
				a = int(two['gameTime_sec']//y)
				people[a] += 1
				allPeople[a] += 1

				b = int(two['logGameTime_sec']//n)+24
				people_log[b] += 1
				allPeople_log[b] += 1
				
				c = int(two['ZTime']//intervalZ)-int(minZ//intervalZ)
				people_z[c] += 1
				allPeople_z[c] += 1				
				
				correctness = 1 if(two['gameStar'] > 0) else 0
				
				starCorrectness[a] += correctness
				allCorrectness[a] += correctness
				
				starCorrectness_log[b] += correctness
				allCorrectness_log[b] += correctness
				
				starCorrectness_z[c] += correctness
				allCorrectness_z[c] += correctness				
				allStars_z[c] += two['gameStar']
				
			#分星星
			#秒
			for dseconds, dpeo, dcorrect in zip(range(0, x+y, y), people, starCorrectness):
				if dpeo > 0:
					dtime_dict = {"gameCode":game,
								  "sectionId":0,
								  "seconds":dseconds,
								  "tickTime":y,
								  "gameStar":star,
								  "people":dpeo,
								  "difficulty":None,
								  #"difficulty2":None,
								  #"difficulty3":None,
								  "avgCorrectness":dcorrect/dpeo
								 }
					if eloChoice == '2':
						elo_dict = {"difficultyDegree2":degree[i]}
						updateQuery = {"gameCode":game, "seconds":dseconds, "tickTime":y, "gameStar":star, "difficulty2":None, "difficultyDegree2":degree[i]}
					elif eloChoice == '3':
						elo_dict = {"difficultyDegree3":degree[i]}
						updateQuery = {"gameCode":game, "seconds":dseconds, "tickTime":y, "gameStar":star, "difficulty3":None, "difficultyDegree3":degree[i]}
					else:
						elo_dict = {"difficultyDegree_kmeans":kmeansDegree[i]}
						updateQuery = {"gameCode":game, "seconds":dseconds, "tickTime":y, "gameStar":star, "difficulty":None, "difficultyDegree_kmeans":kmeansDegree[i]}
					dtime_dict.update(elo_dict)
		 
					if insertMode:
						db.FirstRecord_sta.insert_many([dtime_dict])
					else:
						db.FirstRecord_sta.update_one(updateQuery, {'$set':dtime_dict}, upsert = True)			
					FirstRecord_count += 1
			#log秒
			for dseconds_log, dpeo_log, dcorrect_log in zip(np.arange(-2.4, m+n, n), people_log, starCorrectness_log):
				if dpeo_log > 0:
					dtimeLog_dict = {"gameCode":game,
									 "sectionId":0,
									 "seconds_log":round(dseconds_log, 2),
									 "tickTime":n,
									 "gameStar":star,
									 "people":dpeo_log,
									 "difficulty":None, 
									 #"difficulty2":None,
									 #"difficulty3":None,
									 "avgCorrectness":dcorrect_log/dpeo_log
									}
					if eloChoice == '2':
						elo_dict = {"difficultyDegree2":degree[i]}
						updateQuery = {"gameCode":game, "seconds_log":round(dseconds_log, 2), "tickTime":n, "gameStar":star, "difficulty2":None, "difficultyDegree2":degree[i]}
					elif eloChoice == '3':
						elo_dict = {"difficultyDegree3":degree[i]}
						updateQuery = {"gameCode":game, "seconds_log":round(dseconds_log, 2), "tickTime":n, "gameStar":star, "difficulty3":None, "difficultyDegree3":degree[i]}					
					else:
						elo_dict = {"difficultyDegree_kmeans":kmeansDegree[i]}
						updateQuery = {"gameCode":game, "seconds_log":round(dseconds_log, 2), "tickTime":n, "gameStar":star, "difficulty":None, "difficultyDegree_kmeans":kmeansDegree[i]}
					dtimeLog_dict.update(elo_dict)
					
					
					if insertMode:
						db.FirstRecordLog_sta.insert_many([dtimeLog_dict])
					else:
						db.FirstRecordLog_sta.update_one(updateQuery, {'$set':dtimeLog_dict}, upsert=True)
					FirstRecordLog_count += 1
			del	people, starCorrectness, people_log, starCorrectness_log			
			gc.collect()		

		#不分星星
		#秒
		for seconds_all, peo_all, correct_all in zip(range(0, x+y, y), allPeople, allCorrectness):
			if peo_all > 0:
				cumulativePeo += peo_all
				dtimeAll_dict = {"gameCode":game,
								 "sectionId":0,
								 "seconds":seconds_all,
								 "tickTime":y,
								 "gameStar":5,
								 "people":peo_all,
								 "difficulty":None,
								 #"difficulty2":None,
								 #"difficulty3":None,
								 "avgCorrectness":correct_all/peo_all,
								 "cumulativePeo":cumulativePeo,
								 "cumulativePeoPercent":'%.4f' %(cumulativePeo/totalPeo)				 
								}
				if eloChoice == '2':
					elo_dict = {"difficultyDegree2":degree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds":seconds_all, "tickTime":y, "gameStar":5, "difficulty2":None, "difficultyDegree2":degree[i]}
				elif eloChoice == '3':
					elo_dict = {"difficultyDegree3":degree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds":seconds_all, "tickTime":y, "gameStar":5, "difficulty3":None, "difficultyDegree3":degree[i]}				
				else:
					elo_dict = {"difficultyDegree_kmeans":kmeansDegree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds":seconds_all, "tickTime":y, "gameStar":5, "difficulty":None, "difficultyDegree_kmeans":kmeansDegree[i]}
				dtimeAll_dict.update(elo_dict)								
				
				if insertMode:
					db.FirstRecord_sta.insert_many([dtimeAll_dict])
				else:	
					db.FirstRecord_sta.update_one(updateQuery, {'$set': dtimeAll_dict}, upsert = True)
				FirstRecord_count += 1
		db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('difficultyDegree_kmeans', 1)])
		db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty2', 1), ('difficultyDegree2', 1)])
		db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty3', 1), ('difficultyDegree3', 1)])
		
		#log秒
		for seconds_all_log, peo_all_log, correct_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log):
			if peo_all_log > 0:
				cumulativePeo_log += peo_all_log
				dtimeAllLog_dict = {"gameCode":game,
									"sectionId":0,
									"seconds_log":round(seconds_all_log, 2),
									"tickTime":n,
									"gameStar":5,
									"people":peo_all_log,
									"difficulty":None,
									#"difficulty2":None,
									#"difficulty3":None,
									"avgCorrectness":correct_all_log/peo_all_log,
									"cumulativePeo_log":cumulativePeo_log,
									"cumulativePeoPercent_log":'%.4f' %(cumulativePeo_log/totalPeo)								   
								   }
				if eloChoice == '2':
					elo_dict = { "difficultyDegree2":degree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficulty2":None, "difficultyDegree2":degree[i]}
				elif eloChoice == '3':
					elo_dict = { "difficultyDegree3":degree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficulty3":None, "difficultyDegree3":degree[i]}
				else:
					elo_dict = {"difficultyDegree_kmeans":kmeansDegree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds_log":round(seconds_all_log, 2), "tickTime":n, "gameStar":5, "difficulty":None, "difficultyDegree_kmeans":kmeansDegree[i]}
				dtimeAllLog_dict.update(elo_dict)				
				
				if insertMode:	
					db.FirstRecordLog_sta.insert_many([dtimeAllLog_dict])
				else:	
					db.FirstRecordLog_sta.update_one(updateQuery, {'$set': dtimeAllLog_dict}, upsert = True)					
				FirstRecordLog_count += 1
		gc.collect()
		db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('difficultyDegree_kmeans', 1)])
		db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty2', 1), ('difficultyDegree2', 1)])
		db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_log', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty3', 1), ('difficultyDegree3', 1)])

		# Z秒
		for seconds_all_z, peo_all_z, correct_all_z, star_all_z in zip(np.arange(minZ, maxZ+minZ+2, intervalZ), allPeople_z, allCorrectness_z, allStars_z):
			if peo_all_z > 0:
				cumulativePeo_z += peo_all_z
				dtimeAllZ_dict = {"gameCode":game,
								  "sectionId":0,
								  "seconds_z":round(seconds_all_z, 2),
								  "tickTime":intervalZ,
								  "gameStar":5,
								  "people":peo_all_z,
								  "difficulty":None,
								  #"difficulty2":None,
								  #"difficulty3":None,
								  "avgStar":star_all_z/peo_all_z,
								  "avgCorrectness":correct_all_z/peo_all_z,
								  "cumulativePeo_z":cumulativePeo_z,
								  "cumulativePeoPercent_z":'%.4f' %(cumulativePeo_z/totalPeo)								   
								  }

				if eloChoice == '2':
					elo_dict = { "difficultyDegree2":degree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ, "gameStar":5, "difficulty2":None, "difficultyDegree2":degree[i]}
				elif eloChoice == '3':
					elo_dict = { "difficultyDegree3":degree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ, "gameStar":5, "difficulty3":None, "difficultyDegree3":degree[i]}
				else:
					elo_dict = {"difficultyDegree_kmeans":kmeansDegree[i]}
					updateQuery = {"gameCode":game, "sectionId":0, "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ, "gameStar":5, "difficulty":None, "difficultyDegree_kmeans":kmeansDegree[i]}
				dtimeAllZ_dict.update(elo_dict)				
				
				if insertMode:	
					db.FirstRecordZ_sta.insert_many([dtimeAllZ_dict])
				else:	
					db.FirstRecordZ_sta.update_one(updateQuery, {'$set':dtimeAllZ_dict}, upsert = True)					
				FirstRecordLog_count += 1
		del	allPeople, allCorrectness , allPeople_log, allCorrectness_log, allPeople_z, allCorrectness_z
		gc.collect()
		db.FirstRecordZ_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_z', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty', 1), ('difficultyDegree_kmeans', 1)])
		db.FirstRecordZ_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_z', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty2', 1), ('difficultyDegree2', 1)])
		db.FirstRecordZ_sta.create_index([('gameCode', 1), ('sectionId', 1), ('seconds_z', 1), ('tickTime', 1), ('gameStar', 1), ('difficulty3', 1), ('difficultyDegree3', 1)])
	
	
	##step3依時間 
	print("insert %s data by time" %game)	
	allPeople = pc.create_lists(0, int(x//y+2), 0)
	allCorrectness = pc.create_lists(0, int(x//y+2), 0)
	allDifficulty = pc.create_lists(0, int(x//y+2), 0)
	allDifficulty2 = pc.create_lists(0, int(x//y+2), 0)	
	allDifficulty3 = pc.create_lists(0, int(x//y+2), 0)
	
	allPeople_log = pc.create_lists(0, int(m//n+2), 0)
	allCorrectness_log = pc.create_lists(0, int(m//n+2), 0)
	allDifficulty_log = pc.create_lists(0, int(m//n+2), 0)
	allDifficulty2_log = pc.create_lists(0, int(m//n+2), 0)
	allDifficulty3_log = pc.create_lists(0, int(m//n+2), 0)
	
	for one in ct.find({"gameCode":game, "gameTime":{"$gt":0, "$lte":x}}):
		a = int(one['gameTime_sec']//y)
		allPeople[a] += 1
		
		b = int(one['logGameTime_sec']//n)+24
		allPeople_log[b] += 1					
		
		correctness = 1 if one['gameStar'] > 0 else 0
			
		allCorrectness[a] += correctness
		allDifficulty[a] += itemDifficulty[one['sectionId']-1]
		#allDifficulty2[a] += itemDifficulty2[one['sectionId']-1]
		#allDifficulty3[a] += itemDifficulty3[one['sectionId']-1]
		
		allCorrectness_log[b] += correctness
		allDifficulty_log[b] += itemDifficulty[one['sectionId']-1]
		#allDifficulty2_log[b] += itemDifficulty2[one['sectionId']-1]
		#allDifficulty3_log[b] += itemDifficulty3[one['sectionId']-1]
	
	#不分星星
	#秒
	for seconds_all, peo_all, correct_all, difficulty_all in zip(range(0, x+y, y), allPeople, allCorrectness, allDifficulty):
		if peo_all > 0:
			FirstRecordAll_sta_dict = {"gameCode":game,
									   "sectionId":0,
									   "seconds":seconds_all,
									   "tickTime":y,
									   "gameStar":5,
									   "people":peo_all,
									   "difficulty":difficulty_all/peo_all,
									   "difficultyDegree_kmeans":'n',
									   #"difficulty2":difficulty2_all/peo_all,
									   #"difficultyDegree2":'n',
									   #"difficulty3":difficulty3_all/peo_all,
									   #"difficultyDegree3":'n',									   
									   "avgCorrectness":correct_all/peo_all
								      }
			if insertMode:
				db.FirstRecord_sta.insert_many([FirstRecordAll_sta_dict])
			else:
				if eloChoice == '3':
					updateQuery = {"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":y, "seconds":seconds_all, "difficultyDegree3":'n'}
				elif eloChoice == '2':	
					updateQuery = {"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":y, "seconds":seconds_all, "difficultyDegree2":'n'}
				else:
					updateQuery = {"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":y, "seconds":seconds_all, "difficultyDegree_kmeans":'n'}
				db.FirstRecord_sta.update_one(updateQuery,{'$set': FirstRecordAll_sta_dict}, upsert = True)
			FirstRecord_count += 1
	db.FirstRecord_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds', 1), ('difficultyDegree_kmeans', 1)])
	
	#log秒
	for seconds_all_log, peo_all_log, correct_all_log, difficulty_all_log in zip(np.arange(-2.4, m+n, n), allPeople_log, allCorrectness_log, allDifficulty_log):
		if peo_all_log > 0:
			FirstRecordAllLog_sta_dict = {"gameCode":game,
										  "sectionId":0,
										  "seconds_log":round(seconds_all_log, 2),
										  "tickTime":n,
										  "gameStar":5,
										  "people":peo_all_log,
										  "difficulty":difficulty_all_log/peo_all_log,
										  "difficultyDegree_kmeans":'n',
										  #"difficulty2":difficulty2_all_log/peo_all_log,
										  #"difficultyDegree2":'n',										  
										  #"difficulty3":difficulty3_all_log/peo_all_log,
										  #"difficultyDegree3":'n',	
										  "avgCorrectness":correct_all_log/peo_all_log
										 }
			if insertMode:
				db.FirstRecordLog_sta.insert_many([FirstRecordAllLog_sta_dict])
			else:
				if eloChoice == '3':
					updateQuery = {"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":n, "seconds_log":round(seconds_all_log, 2), "difficultyDegree3":'n'}
				elif eloChoice == '2':
					updateQuery = {"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":n, "seconds_log":round(seconds_all_log, 2), "difficultyDegree2":'n'}
				else:
					updateQuery = {"gameCode":game, "sectionId":0, "gameStar":5, "tickTime":n, "seconds_log":round(seconds_all_log, 2), "difficultyDegree_kmeans":'n'}
				db.FirstRecordLog_sta.update_one(updateQuery,{'$set':FirstRecordAllLog_sta_dict}, upsert = True)   
			FirstRecordLog_count += 1
	del	allPeople, allCorrectness, allDifficulty
	del allPeople_log, allCorrectness_log, allDifficulty_log
	gc.collect()
	db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds_log', 1), ('difficultyDegree_kmeans', 1)])
	db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds_log', 1), ('difficultyDegree2', 1)])
	db.FirstRecordLog_sta.create_index([('gameCode', 1), ('sectionId', 1), ('gameStar', 1), ('tickTime', 1), ('seconds_log', 1), ('difficultyDegree3', 1)])
	
	
	## step4依玩家Elo等級
	print("insert %s data by player degree" %game)
	for i in range(0, len(playerKmeansDegree)):
		cumulativePeo_z = 0
		allPeople_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)
		allCorrectness_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)
		allStars_z = pc.create_lists(0, int((maxZ-minZ)//intervalZ+2), 0)
		if eloChoice == '2':
			query = {"gameCode":game, "playerDegree2":playerKmeansDegree[i], "gameTime_sec":{"$gt":0, "$lte":x}}
		elif eloChoice == '3':
			query = {"gameCode":game, "playerDegree3":playerKmeansDegree[i], "gameTime_sec":{"$gt":0, "$lte":x}}
		else:
			#query = {"gameCode":game, "playerDegree_kmeans":playerKmeansDegree[i], "gameTime_sec":{"$gt":0, "$lte":x}}
			query = {"gameCode":game, "playerDegree_kmeans":playerKmeansDegree[i], "gameTime_sec":{"$gt":0, "$lte":x}}
		for two in ct.find(query):
			c = int(two['ZTime']//intervalZ)-int(minZ//intervalZ)
			allPeople_z[c] += 1
			
			correctness = 1 if (two['gameStar'] > 0) else 0
			allCorrectness_z[c] += correctness	
			allStars_z[c] += two['gameStar']
	
		# z秒
		for seconds_all_z, peo_all_z, correct_all_z, star_all_z in zip(np.arange(minZ, maxZ+intervalZ, intervalZ), allPeople_z, allCorrectness_z, allStars_z):
			if peo_all_z > 0:
				cumulativePeo_z += peo_all_z
				dtimeAllZ_dict = {"gameCode":game,
								  "sectionId":0,
								  "seconds_z":round(seconds_all_z, 2),
								  "tickTime":intervalZ,
								  "gameStar":5,
								  "people":peo_all_z,
								  "avgCorrectness":correct_all_z/peo_all_z,
								  "avgStar":star_all_z/peo_all_z
								  #"cumulativePeo_z":cumulativePeo_z,
								  #"cumulativePeoPercent_z":'%.4f' %(cumulativePeo_z/totalPeo)								   
								 }
				if eloChoice == '2':
					elo_dict = {"playerDegree2":playerKmeansDegree[i]}
					updateQuery = {"gameCode":game, "playerDegree2":playerKmeansDegree[i], "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ}
				elif eloChoice == '3':
					elo_dict = {"playerDegree3":playerKmeansDegree[i]}
					updateQuery = {"gameCode":game, "playerDegree3":playerKmeansDegree[i], "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ}
				else:
					#elo_dict = {"playerDegree_kmeans":playerKmeansDegree[i]}
					elo_dict = {"playerDegree_kmeans":playerKmeansDegree[i]}
					#updateQuery = {"gameCode":game, "playerDegree_kmeans":playerKmeansDegree[i], "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ}
					updateQuery = {"gameCode":game, "playerDegree_kmeans":playerKmeansDegree[i], "seconds_z":round(seconds_all_z, 2), "tickTime":intervalZ}
				dtimeAllZ_dict.update(elo_dict)
	
				if insertMode:
					db.FirstRecordZ_sta.insert_many([dtimeAllZ_dict])
				else:	
					db.FirstRecordZ_sta.update_one(updateQuery, {'$set':dtimeAllZ_dict}, upsert = True)					
				FirstRecordZ_count += 1
		del	allPeople_z, allCorrectness_z, allStars_z
		gc.collect()
	db.FirstRecordZ_sta.create_index([('gameCode', 1), ('playerDegree_kmeans', 1), ('seconds_z', 1), ('tickTime', 1)])
	db.FirstRecordZ_sta.create_index([('gameCode', 1), ('playerDegree2', 1), ('seconds_z', 1), ('tickTime', 1)])
	db.FirstRecordZ_sta.create_index([('gameCode', 1), ('playerDegree3', 1), ('seconds_z', 1), ('tickTime', 1)])
	
	print("Insert FirstRecord_sta:", FirstRecord_count, "\nInsert FirstRecordLog_sta:", FirstRecordLog_count, "\nInsert FirstRecordZ_sta:", FirstRecordZ_count)	
	print("紀錄總人數:{}".format(peo))
	
	pc.pass_time(startTime, time.time())	
