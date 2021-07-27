import PaperCommon as pc
import os
import csv
import numpy as np
import gc
import copy

def export_choose_column(collection, filePath, fileName, query, column, database='dotCode'):
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)

	flag = True
	with open(os.path.join(filePath, fileName), 'w', newline='') as f:
		writer = csv.writer(f)
		for row in ct.find(query, column):
			if flag:
				writer.writerow(row.keys())
				flag = False
			writer.writerow(row.values())
	print("{}輸出完成！".format(fileName))


def export_collection(collection, filePath, fileName, query, database='dotCode'):
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)

	flag = True
	with open(os.path.join(filePath, fileName), 'w', newline='') as f:
		writer = csv.writer(f)
		for row in ct.find(query):
			if flag:
				writer.writerow(row.keys())
				flag = False
			writer.writerow(row.values())
	print("{}輸出完成！".format(fileName))




#主程式
if __name__ == '__main__':
	database = 'dotCode'
	game = 'Duck'
	choice = int(input("1.json to csv\n2.csv to json\n:"))
	maxSection = pc.find_maxSection(game)
	db = pc.clientDB(database)
	
	if choice == 1:
		keys = ['userId', 'maxSection', 'avearageElo']
		pc.json_to_csv(r"D:\MongoDB\Server\4.2\data\DATA\dotCode", keys)


	elif choice == 2:
		pc.CsvToJson(r"D:\dotCodeRecord_PeoElo")
	
	
	elif choice == 3:
		collection = 'AccuTime'
		textFilePath = r'D:\paper\practice\practice file\textdata\%s' %collection
		pc.create_path(textFilePath)
		textFileName = '%s.csv' %collection
		query = {}
		columns = {}
		#export_choose_column(collection, textFilePath, textFileName, query, columns)
		export_collection(collection, textFilePath, textFileName, query)
		'''
		for section in range(1, maxSection+1):
			textFileName = '%s.csv' %section
			query = {"sectionId":section}
			columns = {"_id":0, "gameStar":1, "gameTime_sec":1, "ZTime":1, "elo_001":1, "playerDegree_kmeans":1}
			columns = {"_id":0, "gameStar":1, "accuTime_sec":1, "wrongTime_sec":1, 
						"correctPercentage":1, "tryCount":1, "ZTime":1, "elo_001":1, "playerDegree_kmeans":1}			
			export_choose_column('FirstRecord', textFilePath, textFileName, query, columns)
		'''


	elif choice == 4:
		collection = 'AccuTime'
		ct = pc.clientCT(database, collection)

		textFilePath = r'D:\paper\practice\practice file\textdata'
		i = 0
		sectionId = []
		'''
		for section in range(1, maxSection+1):
			fileName = 'section%d.csv' %section
		'''
		
		flag = True
		fileName = 'All_Sections_1000.csv'
		with open(os.path.join(textFilePath,fileName), 'w', newline='') as f:
			writer = csv.writer(f)
			#for data in ct.find({"sectionId":section}):

			for data in ct.find({}).sort([("elo_001", -1)]):
				sectionId.append(data['sectionId']) 
				i += 1
				if flag:
					writer.writerow(data.keys())
					flag = False
				writer.writerow(data.values())
				if i == 1000:
					break
		sectionCount = {section:sectionId.count(section) for section in set(sectionId)}	
		print(sectionCount)
		print("輸出完成！")
		

	elif choice == 5:
		ct = pc.clientCT(database, 'FirstRecordZ_sta')
		ct.create_index([('gameCode', 1), ('playerDegree', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
		ct.create_index([('gameCode', 1), ('playerDegree_kmeans', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
		minZ = -1.1
		maxZ = 333.4
		intervalZ = 0.01
		tickTime = 0.01
		degrees = [0, 1]
		people = pc.create_lists(0, len(degrees), x=[])			
		for degree in range(0, len(degrees)):
			for second in np.arange(minZ, maxZ, intervalZ):
				second = round(second, 2)
				for one in ct.find({'gameCode':game, 'playerDegree_kmeans':degrees[degree] ,'tickTime':tickTime, 'gameStar':5, 'seconds_z':second}):
					people[degree].append(one['people'])	
		
		textFilePath = r'D:\paper\practice\practice file\textdata'
		fileName = '標準化時間人數比例.csv'
		with open(os.path.join(textFilePath, fileName), 'w', newline='') as f:
			flag = True
			writer = csv.writer(f)
			for second, people1, people2 in zip(np.arange(minZ, maxZ, intervalZ), people[0], people[1]):
				if flag:
					writer.writerow(["second", "people1", "people2"])
					flag = False
				writer.writerow([round(second, 2), people1, people2])
		del people		
		gc.collect()


	elif choice == 6:
		db.FirstPass.create_index([('sectionId', 1), ('userId', 1), ('tryCount', 1)])
		filePath = r'D:\paper\practice\practice file\textdata\accumulated worng time'
		pc.create_path(filePath)	
		
		ct = pc.clientCT(database, 'AccuTime')
		for section in range(1, maxSection+1):
			print("section {}".format(section)) 
			tryCounts = pc.create_lists(0, 690000, x=0)
			star = pc.create_lists(0, 690000, x=0) 
			elo = []
			accuTime = []
			for one in ct.find({'sectionId':section}):
				tryCounts[one['userId']] = one['tryCount']
				star[one['userId']] = one['gameStar']
				
			ct = pc.clientCT(database, 'FirstPass')
			for id in range(1, 690000): 
				if tryCounts[id] > 0:
					if star[id] > 0:
						tryCount = tryCounts[id] - 1
					else: 
						tryCount = tryCounts[id]
					for two in ct.find({'sectionId':section, 'userId':id, 'tryCount':tryCount}):
						try:
							elo.append(two['elo_001'])
							accuTime.append(two['accuTime_sec'])	
						except KeyError:
							print("lack key", two)
			fileName = 'section%s.csv' %section
			fieldNames = ['elo', 'accuTime']
			datas = [elo, accuTime]
			pc.list_write_csv(filePath, fileName, fieldNames, datas)
			del tryCounts, star, elo, accuTime
		gc.collect()	


	elif choice == 7:
		filePath = r'D:\paper\practice\practice file\textdata\try count'
		for tryCount in range(1, 10):
			fileName = 'tryCount.csv'
			query = {'sectionId':1, 'tryCount':tryCount}
			pc.list_write_csv(filePath, fileName, fieldNames, datas)
			