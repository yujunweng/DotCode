#newestElo 要改成這一關全跑完才寫入，所以要用一個串列全部記錄下來，還要記錄usrId

from pymongo import MongoClient
import numpy as np
import traceback
import os
import time
import datetime
import gc
import csv

#函式
def clientDB(database):
	client = MongoClient()
	db = client[database]
	return db

def clientCT(database, collection):
	ct = clientDB(database)[collection]
	return ct
	
def sortFunc(x, y):	#大的往後排
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
			
def sectionColumnFunc(j, k, **elo):
	valueList = []
	elo.setdefault('elo', 0)
	for i in range(j, k):
		valueList.append(elo['elo'])
		
	return np.array(valueList)

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
	
def storFile(data, fileName):
	data = list(map(lambda x:[x],data))
	with open(fileName,'w',newline ='') as f:
		mywrite = csv.writer(f)
		for i, j in zip(data):
			mywrite.writerow(i)
			
def writeCSV(data, data2, fileName, path):
	fields = ['sectionElo', 'peoElo']
	file = os.path.join(path, fileName)
	if not (os.path.isdir(path)):
		os.makedirs(path)
	fout = open(file, 'w')
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
	
def readElo(eloList):
	database = 'dotCode'
	collection = 'dotCodeRecord_PeoElo'
	
	db = clientDB(database)
	ct = clientCT(database, collection)
	print("連接資料庫%s - collection%s" %(database, collection))
	print("reading newestElo...")
	for id in range(maxId):
		for one in ct.find({"userId":id}):
			#print(one['newestElo'])
			eloList[id] = one['newestElo']
	print("reading success!")		
	return eloList	


		
###主程式
#是否以Maze做前測
startTime = time.time()
print(time.localtime())

gameCode = ['Duck']

maxId = 679000

preTest = False

K_value = 'unsure'

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
	for id in range(1, maxId):
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
			
database = 'dotCode'
collection = 'Record'

db = clientDB(database)
ct = clientCT(database, collection)
print("連接資料庫%s - collection:%s" %(database, collection))

###要upsert資料的collection建立索引
print("開始建立索引!")
indexFlag = True
if indexFlag:
	db.Record.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.AccuTime.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1)])
	db.AccuTime.create_index([('gameCode', 1), ('userId', 1),('sectionId', 1)])
	db.FirstPass.create_index([('gameCode', 1), ('sectionId', 1), ('userId', 1),('lastUpdateTime',1)])
	db.FirstPass.create_index([('gameCode', 1), ('userId', 1), ('sectionId', 1),('lastUpdateTime',1)])
	db.Elo.create_index([('gameCode',1), ('userId', 1)])
	indexFlag = False
print("索引完成!")	

all_skill_peo = sectionColumnFunc(1, 67900, elo=0)

if preTest:
	x= 0
	while (x < len(player)):
		all_skill_peo[player[x]] = playerElo[x]
		x += 1
	
#all_skill_peo = readElo(all_skill_peo)

for game in gameCode:
	if(game == 'Maze'):
		maxSection = 40
	elif(game == 'Duck'):
		maxSection = 60
	
	#all_skill_sec = []

	secHeader = True
	for section in range(1, maxSection+1):
		sec_elo = []	#紀錄關卡的elo估值歷程
		opponent_elo = []	#紀錄關卡對手(人)的elo值
		newestElo = []  #記錄所有玩家最新的Elo值
		searchedRecord = 0	#這一關的紀錄筆數
		
		#print("start to find record of %s section %d!" %(game, section))
		skill_sec = 0	#關卡技能等級
		count_player = 0	#計算每一關的玩家
		count_firstpass = 0
		count_accutime = 0
		
		for id in range(1, maxId+1):
			recording = []
			sortedRecording = []
			###preTest才用				
			if preTest:
				if(id in player):
					preTestElo = {"userId" : id,
								  "preTestElo" : all_skill_peo[id]
								 }
					db.TestElo.update_one({'userId':id},{'$set': preTestElo}, upsert = True)
					#print(id)
			###一般用
			else:	
				for one in ct.find({"gameCode":game, "sectionId": section, "userId":id}):
					searchedRecord += 1	
					newGameTime = one['gameTime']
					if ('newGameTime' in one.keys()):
						newGameTime = one['newGameTime']

					recording.append([one['lastUpdateTime'], one['gameStar']])
					#print(len(recording))
				
				if(len(recording) > 0):		#代表這個人在這關有紀錄
					recording = np.array(recording)
					n = 0
					
					len_record = len(recording)
					count_player += 1
					Merge_Sort(recording, 0)
					
					skill_peo = all_skill_peo[id]	#找學生目前的技能等級，之前沒有紀錄就從0開始算	
					
					for subrecording in recording:
						star = subrecording[1]
						K = 0.01-(0.001*n)
						#if(K <= 0.001):
							#K = 0.001
						
						Ecorrect_peo = 1 / (1+np.exp(-(skill_peo-skill_sec)))  #一開始是 1/2
						###星星數 = 0  沒過關
						if(star  == 0):
							correct_peo = 0
							skill_sec = skill_sec + K*(Ecorrect_peo - correct_peo)
							skill_peo = skill_peo + K*(correct_peo - Ecorrect_peo)
							
							sec_elo.append(skill_sec)
							opponent_elo.append(skill_peo)
							
							peoElo_dict = {'elo_001':skill_peo}
							n += 1
							if(game == 'Duck'):
								db.FirstPass.update_one({'gameCode':game, 'sectionId':section, 'userId':id, 'lastUpdateTime':int(subrecording[0])}, {'$set':peoElo_dict}, upsert = True)

								count_firstpass += 1
		
						#星星數 > 0  過關
						else:
							K = 0.01
							#correct_peo = subRecord[1]/3	#以3顆星為基本，低於3顆星拿不到1分 ##沒有數學理論基礎證明
							correct_peo = 1
							skill_sec = skill_sec + K*(Ecorrect_peo - correct_peo)
							skill_peo = skill_peo + K*(correct_peo - Ecorrect_peo)
							
							sec_elo.append(skill_sec)
							opponent_elo.append(skill_peo)
							
							peoElo_dict = {'elo_001':skill_peo}
							
							db.FirstPass.update_one({'gameCode':game, 'sectionId':section, 'userId':id, 'lastUpdateTime':int(subrecording[0])}, {'$set':peoElo_dict}, upsert = True)
							db.AccuTime.update_one({'gameCode':game, 'sectionId':section, 'userId':id}, {'$set':peoElo_dict}, upsert = True)
							count_accutime += 1
							break
					
					#某人在某關最後結果
					all_skill_peo[id] = skill_peo
					newestElo.append([id, skill_peo])
					
					post_dict = {"gameCode" : game,
								 "userId" : id,		#記錄人的技能等級
								 "section%d_elo" %section : skill_peo,
								 "maxSection": section
								}
								
					db.Elo.update_one({'gameCode':game, 'userId':id},{'$set': post_dict}, upsert = True)
			#if(id//100000 == 0):
			#print("now searching id:", id+1)
		
		# transform list type to array type for improve speed 	
		newestElo = np.array(newestElo)
		sec_elo = np.array(sec_elo)
		opponent_elo = np.array(opponent_elo)
		
		### insert關卡難度
		difficulty_dict = {"difficulty" :skill_sec}
		db.Sec_sta.update_one({'gameCode':game, 'sectionId':section}, {'$set':difficulty_dict}, upsert = True) 

		
		try:
			#print("start to update newestElo...")
			
			j = 0
			while(j < len(newestElo)):
				newestElo_dict = {"newestElo" : newestElo[j][1]}
				
				### 要update資料的collection
				db.Elo.update_one({'userId':newestElo[j][0]}, {'$set': newestElo_dict}, upsert = True)
				if preTest:
					db.TestElo.update_one({"userId": newestElo[j][0]}, {'$set': newestElo_dict}, upsert = True)
				j += 1
			#print("newestElo update success!")

		except:
			traceback.print_exc("newestElo:" , newestElo[j])			
		
		
		savePath = "D:\\paper\\practice"
		fileName = "%s_sec.csv" %game
		saveFile = os.path.join(savePath, fileName)
		
		with open(saveFile , 'a+', newline = "") as csvfile:
			fieldnames = ["sectionId", "EloRating", "Players", "records"]
			writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
			#寫入第一列的欄位名稱
			if(secHeader):
				writer.writeheader()
				secHeader = False
			writer.writerow({"sectionId":section,
							 "EloRating":skill_sec,
							 "Players":count_player,
							 "records":searchedRecord
							})

		#storFile(sec_elo, 'EveryElo_%d.csv' %section)
		#storFile(opponent_elo, 'EveryElo_%d.csv' %section)
		wPath = "D:\\paper\\practice\\practice file\\EloRating\\%s\\%s" %(game, K_value)
		if(section < 10):
			writeCSV(sec_elo, opponent_elo, '%sElo_0%d.csv' %(game, section), wPath)
		else:
			writeCSV(sec_elo, opponent_elo, '%sElo_%d.csv' %(game, section), wPath)

		del sec_elo
		del opponent_elo
		del newestElo
		gc.collect()

	endTime = time.time()
	passTime = endTime - startTime
	print("經過時間：", passTime)

os.system("pause")	