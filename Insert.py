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
import traceback
import os
import time
import datetime
import gc
import json
import PaperCommon as pc


def pickInser(key, value, db, ct):
	copyCount = 0
	if value.upper() == "NULL":
		value = None
	if key == "userId":
		value1 = int(input("請輸入ID起號:"))
		value2 = int(input("請輸入ID迄號:"))
		for id in range(value1, value2):
			for post in ct.find({key:id}):
				db.dotCodeRecord_Duck_test.insert(post)
				copyCount += 1
				print("%s 寫入 %d 筆!" %(key, copyCount))
	else:
		for post in ct.find({key:value}):
				db.dotCodeRecord_Duck_test.insert(post)
				copyCount += 1
				print("%s 寫入 %d 筆!" %(key, copyCount))
				

if __name__ == '__main__':
	value = int(input('''(1)Insert score and distinguish player's elo degree
(2)Insert section statistic information to Sec_sta\n:'''))
	startTime = time.time()
	tran_startTime = pc.to_vids_time(startTime)
	database = 'dotCode'
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	playersDegrees = pc.players_degrees():
	sectionsDegrees = pc.sections_degrees()
	sectionId, itemDifficulty, difficultyDegree = pc.add_difficulty(game, '1')
	#sectionId2, itemDifficulty2, difficultyDegree2 = pc.add_difficulty(game, '2')
	#sectionId3, itemDifficulty3, difficultyDegree3 = pc.add_difficulty(game, '3')
	maxId = pc.max_user()
	peo = 0 #有紀錄的玩家
	countInsert = 0 #insert的筆數
	db = pc.clientDB(database)
	

	if value == 1:
		choice = int(input("(1)Insert Score\n(4)Distinguish player's elo degree\n："))
		if choice == 1:		
			''' 插入score, Score的計算方式是官方的計算方式, 詳情見官方說明書'''
			for one in ct.find({"gameCode":game}):
				score_dict = {"score":(one['sectionId']+9) * one['gameStar']}
				db.FirstRecord.update_one({'_id':one['_id']}, {'$set': score_dict}, upsert = True)
				countInsert += 1
	
		elif choice == 2:
			'''對玩家elo區分等級'''
			ct = pc.clientCT(database, 'FirstRecord')
			for section in range(1, maxSection+1):
				elo1 = []
				for one in ct.find({"sectionId":section}):
					try:
						elo1.append(one['elo_001'])
					except:
						traceback.print_exc()
				meanElo1, stdElo1 = calculate_mean_std(elo1)
				print("meanElo1={:.10f}, stdElo1={:.5f}".format(meanElo1, stdElo1))
				for one in ct.find({"sectionId":section}):
					if (one['elo_001'] < meanElo1 - 1.5*stdElo1):
						degree = -2
					elif (meanElo1 - 1.5*stdElo1 <= one['elo_001'] < meanElo1 - 0.5*stdElo1):
						degree = -1	
					elif (meanElo1 - 0.5*stdElo1 <= one['elo_001'] < meanElo1 + 0.5*stdElo1):
						degree = 0
					elif (meanElo1 + 0.5*stdElo1 <= one['elo_001'] < meanElo1 + 1.5*stdElo1):
						degree = 1
					elif (meanElo1 + 1.5*stdElo1 <= one['elo_001']):
						degree = 2

					eloDict = {'playerDegree':degree} 	
					ct.update_one({'_id':one['_id']},{'$set':eloDict}, upsert=True)
					#print(section, one['userId'], eloDict)


	elif value == 2:	
		''' Insert section statistic information(Sec_sta)'''
		choice = int(input("""1.amount of people of get how many stars in every section
2.base on the 30th of spent time until pass the section to calculate mutiple of use time of every sections
3.Degree of difficulty of sections
4.find the best performance\n:"""))   

		# Check data counts 
		if 'Sec_sta' in db.list_collection_names():   
			collection = db['Sec_sta']
			print("data counts：{}".format(collection.estimated_document_count()))
		
		if choice == 1:
			'''amount of people of get how many stars in every section'''
			ct = pc.clientCT(database, 'AccuTime')
			for section in range(1, maxSection+1):
				print("collcting data of %s section %d..." %(game, section))
				allCorrectPercentage = []
				allTruCount = []
				count_peo = pc.create_lists(0, 5, x=0)
				for one in ct.find({"gameCode":game, "sectionId":section}):
					try:
						count_peo[one['gameStar']] += 1
						allCorrectPercentage.append(one['correctPercentage'])
						allTruCount.append(one['tryCount'])
						peo = np.sum(count_peo)
					except KeyError:
						print(one, "lacks key gameStar")
				if peo > 0:
					zeroStar, oneStar, twoStar, threeStar, fourStar = count_peo
					section_dict = 	{"gameCode":game,
									 "sectionId":section,
									 "peo":int(peo),
									 "peo_pass":oneStar+twoStar+threeStar+fourStar,
									 "zeroStarPercentage":zeroStar/peo,
									 "oneStarPercentage":oneStar/peo,
									 "twoStarPercentage":twoStar/peo,
									 "threeStarPercentage":threeStar/peo,
									 "fourStarPercentage":fourStar/peo,
									 "avgCorrectPercentage":np.mean(allCorrectPercentage),
									 "avgTryCount":np.mean(allTruCount),
									}
					pc.judge_isinstance_numpy(section_dict)				
					db.Sec_sta.update_one({'gameCode':game, 'sectionId':section},{'$set':section_dict}, upsert=True)
					countInsert += 1

			ct = pc.clientCT(database, 'FirstRecord')
			for section in range(1, maxSection+1):
				print("collcting data of %s section %d..." %(game, section))
				allCorrects = []
				for one in ct.find({"gameCode":game, "sectionId":section}):
					try:
						correctPercentage = 1 if one['gameStar'] > 0 else 0
						allCorrects.append(correctPercentage)
					except KeyError:
						print(one, "lacks key gameStar")
				
				if len(allCorrects) > 0:
					section_dict =  {"avgFirstCorrectPercentage":np.mean(allCorrects)}
					db.Sec_sta.update_one({'gameCode':game, 'sectionId':section}, {'$set':section_dict}, upsert=True)
					countInsert += 1

		elif choice == 2:
			'''base on the 30th of spent time until pass the section to calculate mutiple of use time of every sections'''
			ct = pc.clientCT(database, 'Sec_sta')
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
					ct.update_one({'_id':three['_id']}, {'$set': times_dict}, upsert = True)
					countInsert += 1

		elif choice == 3:	
			'''
			Degree of difficulty of sections
			區分關卡難度等級
			'''	
			eloChoice = input("請選擇elo分級欄位\n(1)elo1:0.01\n(2)elo2:0.01-0.002n\n(3)elo3：0.02\n：")
			ct = pc.clientCT(database, 'Sec_sta')
			itemDifficulties = []
			for section in range(1, maxSection+1):
				for one in ct.find({"gameCode": game, "sectionId" : section}):
					if eloChoice == '2':
						itemDifficulties.append(one['elo2_difficulty'])
					elif eloChoice == '3':
						itemDifficulties.append(one['elo3_difficulty'])
					else:
						itemDifficulties.append(one['elo_difficulty'])
			avgDifficulty = np.mean(itemDifficulties)
			difficultyStd = np.std(itemDifficulties)
			print("Average Difficulty, Standard deviation of %s is %f, %f  " %(game, avgDifficulty, difficultyStd))

			for section in range(1,maxSection+1):
				dDegree_dict = {}
				for one in ct.find({"gameCode":game, "sectionId":section}):
					if eloChoice == '2':
						oneDifficulty = one['elo2_difficulty']  
					elif eloChoice == '3':
						oneDifficulty = one['elo3_difficulty'] 
					else: 
						oneDifficulty = one['elo_difficulty']
					
					if (oneDifficulty < avgDifficulty - 1.5*difficultyStd):
						degree = -2					
					elif (avgDifficulty - 1.5*difficultyStd <= oneDifficulty < avgDifficulty - 0.5*difficultyStd):
						degree = -1					
					elif (avgDifficulty - 0.5*difficultyStd <= oneDifficulty < avgDifficulty + 0.5*difficultyStd):
						degree = 0
					elif (avgDifficulty + 0.5*difficultyStd <= oneDifficulty < avgDifficulty + 1.5*difficultyStd):
						degree = 1
					elif (avgDifficulty + 1.5*difficultyStd <= oneDifficulty):
						degree = 2

				
					if eloChoice == '2':
						dDegree_dict = {'difficultyDegree2':degree}
					elif eloChoice == '3':
						dDegree_dict = {'difficultyDegree3':degree}
					else:
						dDegree_dict = {'difficultyDegree':degree}
					ct.update_one({"gameCode":game, "sectionId":section}, {'$set':dDegree_dict}, upsert = True)
					countInsert += 1
		
		elif choice == 4:
			'''find the best performance''' 
			midTimePass = []
			ct = pc.clientCT(database, 'Sec_sta')
			# 計算過關時間的中位數
			for section in range(1, maxSection+1):
				for one in ct.find({"sectionId":section}):
					midTimePass.append(one['FirstMidTime_Pass'])
			
			ct = pc.clientCT(database, 'FirstRecord_sta')
			for section in range(1, maxSection+1):
				findTheBest = False
				bestCorrectness = -1
				bestSecond = -1
				maxPeo = 0
				for second in range(1, 57600):
					for one in ct.find({"gameCode":game, "sectionId":section, "gameStar":5, "tickTime":1, "seconds":second}):
						if one['people'] > maxPeo:
							maxPeo = one['people']
							maxPeoSecond = one['seconds']
							maxPeoCorrectness = one['avgCorrectness']
						if one['avgCorrectness'] > bestCorrectness and one['people'] > 1:
							bestCorrectness = one['avgCorrectness']
							bestSecond = one['seconds']
							bestPeo = one['people']
							bestCumulativePeoPercent = one['cumulativePeoPercent']
						cumulativePeoPercent = float(one['cumulativePeoPercent'])
						if cumulativePeoPercent > 0.6:#second > midTimePass[section-1]:
							stopSecond = one['seconds']
							findTheBest = True
							break
					if 	findTheBest:
						bestDict = {"firstBestCorrectness":bestCorrectness,
									"firstBestSecond":bestSecond,
									"firstBestPeo":bestPeo,
									"firstMaxPeoSecond":maxPeoSecond,
									"firstMaxPeoCorrectness":maxPeoCorrectness
									#"bestCumulativePeoPercent":bestCumulativePeoPercent,
									}
						print('{0:<4d} {1:<1.4f} {2:>6d} {3:>8s} {4:>6d} {5:>4d}'.format(section, bestCorrectness, bestSecond, bestCumulativePeoPercent, bestPeo, stopSecond))
						db.Sec_sta.update_one({'gameCode':game, 'sectionId':section}, {'$set':bestDict}, upsert=True)
						break
						
						
	elif value == 4:		
		database = 'dotCode'
		collection = 'AccuTime'
		game = 'Duck'
		maxSection = pc.find_maxSection(game)
		maxId = pc.max_user()
		
		db = pc.clientDB(database)
		ct = pc.clientCT(database, collection)
		
		ct.create_index([('userId', 1), ('sectionId', 1)])
		db.Elo.create_index([('userId', 1)])
		
		for id in range(1, maxId):
			sectionCount = 0
			totalElo = 0
			for section in range(1, maxSection):
				for one in ct.find({"userId":id, "sectionId":section}):
					sectionCount += 1
					totalElo += one['elo_001']
			if sectionCount > 0:
				averageElo = totalElo / sectionCount
				updateDict = {"avearageElo":averageElo}
				db.Elo.update_one({"userId":id},{"$set":updateDict}, upsert = True)
						
			
		
	elif value == 5:
		database = 'test'
		collection = 'FirstPass'
		ct = pc.clientCT(database, collection)
		ct.create_index([('sectionId', 1), ('userId', 1)])
		for section in range(1, maxSection+1):
			for id in range(1, 690000):
				x = ct.count_documents({'sectionId':section, 'userId':id})
				countTryTimes_dict = {'maxTryCount':x}
				if x > 0:
					ct.update_many({"sectionId":section, "userId":id}, {'$set':countTryTimes_dict}, upsert=True) 
					print(id)
					os.system("pause")
					
					
	elif value == 0:
		'''delete data'''
		print('大量修改或刪除資料前, 先刪除該與該資料或欄位相關的index可大幅加快速度, 避免硬碟寫入滿載, 因修改或刪除資料必須重新排序index')
		choice = int(input("(1)delete data\n(2)update data\n(3)count data\n："))
		if choice == 1:
			collection = 'FirstRecord'
			ct = pc.clientCT(database, collection)
			
			print("delete %s data" %collection)
			#myquery = {'gameCode':'Maze'}
			#myquery = {"tryCount":{"$gt":0}}
			myquery = {'sectionId':11}
			#myquery = {'$and':[{'gameCode':{'$ne':'Maze'}}, {'gameCode':{'$ne':None}}, {'gamecode':'Maze'}]}

			x = ct.delete_many(myquery)
			countInsert = x.deleted_count
			print(countInsert, "documents deleted.")
		
		elif choice == 2:
			collection = 'FirstRecord'
			ct = pc.clientCT(database, collection)

			# 刪除欄位
			print("unset %s data" %collection)
			unset_keys = []
			'''
			one = ct.find_one()
			for key in one.keys():
				if key not in ('_id', 'gameCode', 'sectionId', 'elo_difficulty', 'elo2_difficulty'):
					unset_keys.append([key, ""])		
			unset_dict = dict(unset_keys)
			x = ct.update_many({"gameCode":"Duck"}, {'$unset':unset_dict}, upsert=False)
			'''
			x = ct.update_many({}, {'$unset':{"difficultyDegree_kmeans":''}}, upsert=False)
			countInsert = x.modified_count
			print(countInsert, "documents modified.")
			
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
			
			print("upsert data")
			ids = []
			sections = []
			# 增加欄位
			for one in ct.find():
				if one.get('elo2', 0) == 0:
					ids.append(one['userId'])
					sections.append(one['sectionId'])
			collection = 'Elo2'
			ct = clientCT(database, collection)			
			for id, section in zip(ids, sections):
				for one in ct.find({"gameCode":"Duck", "userId":id}): 
					key = 'section%d_elo' %section
					update_dict = {'elo2':one[key] }
					print("id:", id, "section:", section)
					db.AccuTime.update_one({'gameCode':'Duck', 'sectionId':section, 'userId':id}, {'$set':update_dict}, upsert=False)
				
			
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
			
	print("total inserted data:", countInsert, "列入紀錄總人數:", peo)
	pc.pass_time(startTime, time.time())