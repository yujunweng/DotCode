#newestElo 要改成這一關全跑完才寫入，所以要用一個串列全部記錄下來，還要記錄usrId

from pymongo import MongoClient
import numpy as np
import traceback
import os
import time
import datetime
import gc
import csv
import PaperCommon as pc


#函式
def writeCSV(data, data2, filePath, fileName):
	fields = ['sectionElo', 'peoElo']
	pc.create_path(filePath)
	saveFile = os.path.join(filePath, fileName)
	with open(saveFile , 'w', newline="") as csvfile:
		flag = True
		for i, j in zip(data, data2):
			if flag:
				fout.write(fields[0])
				fout.write(",")
				fout.write(fields[1])
				fout.write("\n")
				flag = False
			fout.write(str(i))
			fout.write(",")
			fout.write(str(j))
			fout.write("\n")
		fout.close()
	
	
def readElo(eloList, collection, database='dotCode'):
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)
	print("連接資料庫%s - collection%s" %(database, collection))
	print("reading newestElo...")
	for id in range(maxId):
		for one in ct.find({"userId":id}):
			#print(one['newestElo'])
			eloList[id] = one['newestElo']
	print("reading success!")		
	return eloList	



###主程式
if __name__ == '__main__':
	startTime = time.time()
	print(time.localtime())
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	maxId = pc.max_user()
	
	#是否以Maze做前測
	preTest = False
	
	K = 0.1
	K_value = str(K).replace('.', '')
	keyElo = 'elo_'+K_value
	keyDifficulty = 'difficulty_'+K_value
	print("key:", keyElo, keyDifficulty)
	'''
	if preTest:
		database = 'dotCode'
		collection = 'MazeElo'
		
		db = clientDB(database)
		ct = clientCT(database, collection)
		print("連接資料庫%s - collection:%s" %(database, collection))
		
		ct.create_index([('userId', 1), ('maxSection', 1)])
		testPlayer = 0
		player = []
		playerElo = []
		for id in range(1, maxId+1):
			for one in ct.find({"userId":id}):
				#print(one.keys())
				if(one['maxSection'] >= 15):
					for section in range(1, one['maxSection']+1):
						#print(one)
						#os.system("pause")
						if(one.get('section%d_elo' %section) is None):
							#print(section)
							break
						elif(section == one['maxSection']):
							print(id)
							player.append(id)
							playerElo.append(one['newestElo'])
							testPlayer += 1
	'''			
	database = 'dotCode'
	collection = 'FirstPass'

	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)
	print("連接資料庫%s - collection:%s" %(database, collection))

	###要upsert資料的collection建立索引
	print("Start to creat index")
	db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1),('lastUpdateTime',1)])
	db.FirstPass.create_index([('gameCode', 1), ('userId', 1), ('sectionId', 1),('lastUpdateTime',1)])
	db.AccuTime.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.AccuTime.create_index([('gameCode', 1), ('userId', 1),('sectionId', 1)])	
	db.Elo.create_index([('gameCode',1), ('userId', 1)])
	print("Indexes created!")	

	all_skill_peo = pc.create_lists(1, maxId+1, x=0)
	'''
	if preTest:
		x= 0
		while (x < len(player)):
			all_skill_peo[player[x]] = playerElo[x]
			x += 1
	'''	
	#all_skill_peo = readElo(all_skill_peo)

	secHeader = True
	for section in range(1, maxSection+1):
		print("start elo rating section %d..." %section)
		sec_elo = []	#紀錄關卡的elo估值歷程
		player_elo = []	#紀錄關卡對手(人)的elo值
		newestElo = []  #記錄所有玩家最新的Elo值
		searchedRecord = 0	#這一關的紀錄筆數
		
		skill_sec = 0	#關卡技能等級
		count_player = 0	#計算每一關的玩家
		count_firstpass = 0
		count_accutime = 0
		
		for id in range(1, maxId):
			recording = []
			sortedRecording = []
			
			###preTest才用				
			if preTest:
				if(id in player):
					preTestElo = {'userId' : id,
								  'preTestElo' : all_skill_peo[id]
								 }
					db.TestElo.update_one({'userId':id},{'$set': preTestElo}, upsert = True)
					#print(id)
			
			###一般用
			else:	
				for one in ct.find({"gameCode":game, "sectionId":section, "userId":id}):
					searchedRecord += 1	
					recording.append([one['lastUpdateTime'], one['gameStar']])
					#print(len(recording))
				
				if len(recording) > 0:		#代表這個人在這關有紀錄
					recording = np.array(recording)
					n = 0
					
					len_record = len(recording)
					count_player += 1
					pc.merge_sort(recording, 0)
					
					skill_peo = all_skill_peo[id]	#找學生目前的技能等級，之前沒有紀錄就從0開始算	
					
					i = 0
					while i < len_record: 
						star = recording[i][1]
						
						Ecorrect_peo = 1 / (1+np.exp(-(skill_peo-skill_sec)))  #一開始是 1/2
						###星星數 = 0  沒過關
						if star == 0:
							correct_peo = 0
							skill_sec = skill_sec + K*(Ecorrect_peo - correct_peo)
							skill_peo = skill_peo + K*(correct_peo - Ecorrect_peo)
							
							sec_elo.append(skill_sec)
							player_elo.append(skill_peo)
							
							peoElo_dict = {keyElo:skill_peo}
							db.FirstPass.update_one({'gameCode':game, 'sectionId':section, 'userId':id, 'lastUpdateTime':int(recording[i][0])}, {'$set':peoElo_dict}, upsert=True)
							if i == (len_record - 1):
								db.AccuTime.update_one({'gameCode':game, 'sectionId':section, 'userId':id}, {'$set':peoElo_dict}, upsert=True)
							if i == 0:
								db.FirstRecord.update_one({'gameCode':game, 'sectionId':section, 'userId':id}, {'$set':peoElo_dict}, upsert=True)
							
							count_firstpass += 1
							i += 1
						
						#星星數 > 0  過關
						else:
							#correct_peo = subRecord[1]/3	#以3顆星為基本，低於3顆星拿不到1分 ##沒有數學理論基礎證明
							correct_peo = 1
							skill_sec = skill_sec + K*(Ecorrect_peo - correct_peo)
							skill_peo = skill_peo + K*(correct_peo - Ecorrect_peo)
							
							sec_elo.append(skill_sec)
							player_elo.append(skill_peo)
							
							peoElo_dict = {keyElo:skill_peo}
							
							db.FirstPass.update_one({'gameCode':game, 'sectionId':section, 'userId':id, 'lastUpdateTime':int(recording[i][0])}, {'$set':peoElo_dict}, upsert=True)
							db.AccuTime.update_one({'gameCode':game, 'sectionId':section, 'userId':id}, {'$set':peoElo_dict}, upsert = True)
							if i == 0:
								db.FirstRecord.update_one({'gameCode':game, 'sectionId':section, 'userId':id}, {'$set':peoElo_dict}, upsert=True)
							
							count_accutime += 1
							break
					
					#某人在某關最後結果
					all_skill_peo[id] = skill_peo
					newestElo.append([id, skill_peo])
					
					post_dict = {'gameCode':game,
								 'userId':id,		#記錄人的技能等級
								 'section%d_elo' %section :skill_peo,
								 'maxSection':section
								}
								
					db.Elo.update_one({'gameCode':game, 'userId':id}, {'$set':post_dict}, upsert=True)
			#if(id//100000 == 0):
			#print("now searching id:", id+1)
		
		# transform list type to array type for improve speed 	
		newestElo = np.array(newestElo)
		sec_elo = np.array(sec_elo)
		player_elo = np.array(player_elo)
		
		### insert關卡難度
		difficulty_dict = {keyDifficulty:skill_sec}
		db.Sec_sta.update_one({'gameCode':game, 'sectionId':section}, {'$set':difficulty_dict}, upsert=True) 

		try:
			print("start to update newestElo...")
			j = 0
			while j < len(newestElo):
				newestElo_dict = {'newestElo':newestElo[j][1]}
				
				### 要update資料的collection
				db.Elo.update_one({'gameCode':game, 'userId':newestElo[j][0]}, {'$set':newestElo_dict}, upsert=True)
				if preTest:
					db.TestElo.update_one({'gameCode':game, 'userId':newestElo[j][0]}, {'$set':newestElo_dict}, upsert=True)
				j += 1
			print("newestElo update success!")

		except:
			traceback.print_exc("newestElo:" , newestElo[j])			
		
		wPath = r"D:\paper\practice\practice file\EloRating\%s\%s" %(game, K_value)
		datas = []
		datas.append(sec_elo)
		datas.append(player_elo)
		fields = ['sec_elo', 'player_elo']
		if section < 10:
			#writeCSV(sec_elo, player_elo, '%sElo_0%d.csv' %(game, section), wPath)
			pc.list_write_csv(datas, fields, wPath, '%sElo_0%d.csv' %(game, section))
		else:
			#writeCSV(sec_elo, player_elo, '%sElo_%d.csv' %(game, section), wPath)
			pc.list_write_csv(datas, fields, wPath, '%sElo_%d.csv' %(game, section))
		
		del sec_elo, player_elo, newestElo, datas
		gc.collect()

		pc.pass_time(startTime, time.time())