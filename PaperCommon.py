'''
Created
@author: Y.J.Weng
'''

from pymongo import MongoClient
import pymongo
import traceback
import os
import json
import csv
import datetime
import time
import numpy as np
import copy	
import codecs


def clientDB(database, host='localhost', port=27017):
	#connection = MongoClient('localhost', 27017)
	#print(connection.list_database_names())  #Return a list of db, equal to: > show dbs
	#print(db.list_collection_names())        #Return a list of collections in 'testdb1'
	#collection.drop()	# Delete(drop) collection named 'posts' from db
	#print("drop collection %s" %str(collection))

	client = MongoClient(host, port)
	db = client[database]
	return db


def clientCT(database, collection):
	ct = clientDB(database)[collection]
	#print('連接資料庫:%s - collection:%s\n' %(database, collection))
	return ct


def max_section(game='Duck', database='dotCode', collection='Record'):	
	ct = clientCT(database, collection)
	ct.create_index([('gameCode', 1), ('sectionId', 1)])
	for one in ct.find({"gameCode":game}).sort([("sectionId", -1)]).limit(1):
		#print(one['sectionId'])
		maxSection = one['sectionId']
	return maxSection


def max_user(game='Duck', database='dotCode', collection='Record'):
	ct = clientCT(database, collection)
	ct.create_index([('gameCode', 1), ('userId', 1)])
	for one in ct.find({"gameCode":game}).sort([("userId", -1)]).limit(1):
		#print(one['userId'])
		maxUserId = one["userId"]
	return maxUserId


def	players_degrees():
	return ['Low', 'High']


def sections_degrees(difficultyDegreeKey, game='Duck'):
	maxSection = find_maxSection()
	ct = clientCT('dotCode', 'Sec_sta')
	sectionDegrees = []
	for section in range(0, maxSection+1):
		for one in ct.find({"sectionId":section}):
			sectionDegrees.append(one[difficultyDegreeKey])
	return 	sectionDegrees


def elo_degrees():
	ct = clientCT('dotCode', 'Sec_sta')
	for one in ct.find({"gameCode":'Duck'}).sort([("difficultyDegree_kmeans", -1)]).limit(1):
		maxDifficulty = one["difficultyDegree_kmeans"]
	if maxDifficulty == 3:
		return ['Simple', 'Normal', 'Hard']
	elif maxDifficulty == 4:
		return ['Very Simple', 'Simple', 'Normal', 'Hard', 'Very Hard']
	elif maxDifficulty == 5:
		return ['Very Simple', 'Simple', 'Normal', 'Hard', 'Very Hard', 'Unbelievable Hard']


def stars_legends():
	return ['0star', '★', '★★', '★★★', '★★★★']
	

def color_degrees(degrees=5):
	if degrees == 5:
		return ['blue', 'skyblue', 'yellow', 'orange', 'red']
	elif degrees == 7:
		return ['springgreen', 'blue', 'skyblue', 'white', 'yellow', 'orange', 'red']	


def add_difficulty(game, difficultySeq):
	ct = clientCT('dotCode', 'Sec_sta')
	
	maxSection = find_maxSection(game)
	
	itemDifficulty, difficultyDegree, sections = [], [], []
	
	if difficultySeq == '2':
		eloDiffcultyColumn = 'elo2_difficulty'
		elodifficultyDegreeColumn = 'difficultyDegree2'
	elif difficultySeq == '3':
		eloDiffcultyColumn = 'elo3_difficulty'
		elodifficultyDegreeColumn = 'difficultyDegree3'
	else:
		if difficultySeq not in ('1', '2', '3'):
			print("沒有這個選項, 我幫你選elo1")
		eloDiffcultyColumn = 'difficulty_01'
		eloDifficultyDegreeColumn = 'difficultyDegree_kmeans'
		
	for section in range(1, maxSection+1):
		for one in ct.find({'gameCode': game, 'sectionId':section}):
			try:
				sections.append(one['sectionId'])
				itemDifficulty.append(one[eloDiffcultyColumn])
				difficultyDegree.append(one[eloDifficultyDegreeColumn])
			except:
				traceback.print_exc()
	return sections, itemDifficulty, difficultyDegree


def bubbleSort(x):
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


def bubbleSort_twoLayer(x, y=0):	#大的往後排
	matrix = []
	i = len(x)-1
	while (i > 0):
		j = 0
		while (j < i):	
			if (x[j][y] > x[j+1][y]):
				matrix = copy.deepcopy(x[j+1])
				x[j+1] = copy.deepcopy(x[j])
				x[j] = copy.deepcopy(matrix)
			j += 1
		i -= 1
	return x
			
	
def choose_collection(database='dotCode'):
	db = clientDB(database)
	collections = db.list_collection_names()
	for c in enumerate(collections, start=1):
		print(c)
	
	choice = int(input('請選擇collection：'))
	return collections[choice-1]


def choose_database(host='localhost', port=27017):
	connection = MongoClient(host, port)
	databases = connection.list_database_names()  #Return a list of db, equal to: > show dbs
	if databases is None:
		return 'dotCode'
	else:
		for d in enumerate(databases):
			print("({}){}".format(d[0]+1, d[1]))
		dbChoice = int(input("請選擇資料庫："))
		database = databases[dbChoice-1]
		return database
		
	
def collect_data(collection, query, keys, database='dotCode'):
	'''	keys are the columns we want, and should be a list.'''
	ct = clientCT(database, collection)
	#players = np.array(players)
	returnList = []
	for _ in range(len(keys)):
		locals()['list%s' %_] = []
	
	for one in ct.find(query):
		try:
			for key in enumerate(keys):
				locals()['list%s' %i].append(one[key])
		except KeyError:
			print(id, "lack of the key" )
	
	for _ in range(len(keys)): 
		returnList.append(locals()['list%s' %_])
	return returnList
	

def count_data(collection, field='_id', query={}, unique=True, database='dotCode'):
	''' if unique is True, count distinct value of field
		else count quantity of query'''

	ct = clientCT(database, collection)
	if unique:
		userCounts = len(ct.distinct(field))
	else:
		userCounts = ct.count_documents(query)
	#print(userCounts)	
	return userCounts


def create_lists(j, k, x=0):
    if isinstance(x, list):
        return [list(x) for _ in range(j, k)]
    else:
        return [x for _ in range(j, k)]  


def create_path(filePath):	
	if not os.path.isdir(filePath):
		os.makedirs(filePath)
	

def csv_to_json(path):
	jsonfile = codecs.open(path+'.json', 'w', 'utf-8')
	csvfile = codecs.open(path+'.csv', 'r', 'utf-8')
	reader = csv.DictReader(csvfile)
	#取得表頭
	head_row = next(reader)
	print(head_row)
	flag = True
	for row in reader:
		if flag:
			json.dump(head_row, jsonfile)
			jsonfile.write('\n')
			flag = False
		json.dump(row, jsonfile)
		jsonfile.write('\n')
	jsonfile.close()
	csvfile.close()
	

def follow_sort(x, seq):
	new_x = []
	for i in seq:
		new_x.append(x[i])
	#print(new_x)
	return new_x


def get_min_value(collection, field, database='dotCode'):
	ct = clientCT(database, collection)
	results = ct.find({}).sort([(field, 1)])
	for result in results:
		minValue = result[field]
		break
	return minValue 


def get_max_value(collection, field, database='dotCode'):
	ct = clientCT(database, collection)
	results = ct.find({}).sort([(field, -1)])
	for result in results:
		maxValue = result[field]
		break
	return maxValue 


def to_str(listX):
	return [str(i) for i in listX]
	

def json_to_int(x):
	if isinstance(x, dict):
		#return {k:(int(v) if isinstance(v, unicode) else v) for k,v in x.items()}
		return {k:(float(v)) for k, v in x.items()}
	return x

	
def json_to_csv(path, key):
	jsonData = codecs.open(path+'.json', 'r', 'utf-8')
	# csvfile = open(path+'.csv', 'w') # 此处这样写会导致写出来的文件会有空行
	# csvfile = open(path+'.csv', 'wb') # python2下
	csvfile = open(path+'.csv', 'w', newline='') # python3下
	writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
	flag = True
	for line in jsonData:
		dic = json.loads(line[0:-1])
		if flag:
			# 获取属性列表
			#keys = list(dic.keys())
			keys = key
			print (keys)
			writer.writerow(key) # 将属性列表写入csv中
			flag = False
		# 读取json数据的每一行，将values数据一次一行的写入csv中
		writer.writerow(list(dic.values()))
	jsonData.close()
	csvfile.close()
	

def judge_isinstance_numpy(x):
	'''x should be a dict'''
	for items in x.items():
		#print(items)
		if isinstance(items[1], np.int32):
			print(items[0])
			s =input("請修改成int後再執行")
			
		elif isinstance(items[1], np.int64):
			print(items[0])
			s =input("請修改成int後再執行")
		

def qualify_files(filePath, fileType):
	files = []
	for file in os.listdir(filePath):
		newFilePath = os.path.join(filePath, file)
		if os.path.isfile(newFilePath):
			name, slaveName = file.split('.')
			if slaveName == fileType:
				files.append(file)
	return files
	

def list_columns(database, collection, message=None):
	'''list fields for choose, 
		if choosed field more than one, use "," between choice to distinguish
	'''		
	ct = clientCT(database, collection)
	keys = list(ct.find_one().keys())
	for key in enumerate(keys, start=1):
		print(key)
	
	chooseKeysNums = input("{}代號間以逗號分隔\n：".format(message))
	chooseKeys = []
	for chooseKeysNum in chooseKeysNums.split(','):
		try:
			chooseKeysNum = int(chooseKeysNum)
			chooseKeys.append(keys[chooseKeysNum-1])
		except ValueError:
			continue    
	return chooseKeys


def list_write_csv(datas, fields, filePath, fileName):
	'''	datas should be a list, and could include of many kind of data.
		fields should be a list.
		ex. datas = [accuTimeTaken, wrongTimeTaken, tryCount, elo1, elo2]
		the column order of fields must accord the column order of datas. 
		all columns must have the same shape
	'''
	#print(len(datas))
	#print(len(datas[0]))
	datas = np.array(datas)
	with open(os.path.join(filePath, fileName), 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=fields)
		flag = True
		print("writing data...")
		if flag:
			writer.writeheader()
			flag = False
		for i in range(0, len(datas[0])):
			values = []
			for data in datas:
				values.append(data[i])
			dataDict = dict(zip(fields, values))
			#print(dataDict)
			writer.writerow(dataDict)	


def merge_sort(array, y, print_array=False):
	if len(array) > 1:
		mid = len(array) // 2
		
		left_array = copy.deepcopy(array[:mid])
		right_array = copy.deepcopy(array[mid:])

		merge_sort(left_array, y)
		merge_sort(right_array, y)
		
		right_index = 0
		left_index = 0
		merged_index = 0
		while right_index < len(right_array) and left_index < len(left_array):
			if(right_array[right_index][y] < left_array[left_index][y]):
				array[merged_index] = copy.deepcopy(right_array[right_index])
				right_index = right_index + 1
			else:
				array[merged_index] = copy.deepcopy(left_array[left_index])
				left_index = left_index + 1
				
			merged_index = merged_index + 1
		
		while right_index < len(right_array):
			array[merged_index] = copy.deepcopy(right_array[right_index])
			right_index = right_index + 1
			merged_index = merged_index + 1
		
		while left_index < len(left_array):
			array[merged_index] = copy.deepcopy(left_array[left_index])
			left_index = left_index + 1
			merged_index = merged_index + 1
	

def pass_time(startTime, endTime):
	print("used time {:.2f} 秒\n".format(endTime - startTime))	
	
	
def read_csv(filePath, fileName, columnName='all'):
	path = os.path.join(filePath, fileName)
	with open(path, newline = '', encoding='UTF-8') as csvfile:
		#讀取CSV檔案內容
		rows = csv.DictReader(csvfile)
		if columnName == 'all':
			data = [row for row in rows]
		else:	
			data = [row[columnName] for row in rows]

	return data


def remove_file(filePath, fileName):
	filePath = os.path.join(filePath, fileName)
	if os.path.isfile(filePath):
		os.remove(filePath)	


def sort_seq(x):
	# 給編號
	i = 0
	new_x = []
	while i < len(x):
		new_x.append([i,x[i]])
		i += 1
	
	new_x = bubbleSort_twoLayer(new_x, y=1)
	seq = []
	for ele in new_x:
		seq.append(ele[0])
	return seq 


def test_insert():
	for i in range(1000): 
		post = {"name":"test"+str(i), "lastTime":time.time()}
		db.test.insert(post, w=1, j=True, wtimeout=500)
		print(post)
		#writeLog("test.txt")


def to_vids_time(time_sec):
	return datetime.datetime.fromtimestamp(time_sec).strftime("%Y-%m-%d %H:%M:%S")		
	

def write_log(recordPath, fileName, *massage):
	try:
		create_path(recordPath)
		file = os.path.join(recordPath, fileName) 	
		fout2 = open(file, "a+") # a:只可寫不可讀, a+:可讀寫
	except:
		print("開啟檔案失敗!")
		traceback.print_exc()	
	
	for mas in massage:
		mas = str(mas)
		fout2.write(mas+"\n")
	fout2.close()
	
	
def write_dict(**kwargs):
	'''print dict content'''
	for key, item in kwargs.items():
		#print(key, item)
		for k, v in item.items():
			print('k={}, v={}'.format(k,v))
