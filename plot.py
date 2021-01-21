'''
Created on 2019年10月6日
20191006    增加畫圖
20191207    增加畫折線圖
20200329    完成難度、學生程度與累積時間關係的散布圖
20200908	在plotMultiScatter加1個參數，控制要畫幾個子圖，可以傳一個多子陣列的X,Y，但不用全畫
@author: 翁毓駿
'''

from pymongo import MongoClient
from sklearn import cluster, datasets, preprocessing, metrics
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from scipy.spatial.distance import cdist
import scipy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import traceback
import csv
import os
import time
import datetime
import gc

def clientDB(database):
	client = MongoClient()
	db = client[database]
	return db

def clientCT(database, collection):
	ct = clientDB(database)[collection]
	#print('連接資料庫:%s - collection:%s\n' %(database, collection))
	return ct

def plotScatter(xList, yList, color, scale, title, xLabel, yLabel, cbar_label=None, xlimit=100, ylimit=1, filePath=None, filename=None):
	#有cmap
	#xLabel and yLabel must be word
	plt.style.use('dark_background')
	fig, ax = plt.subplots(figsize=(10, 6)) #plt.subplots是開出總畫布
	plt.title(title, fontsize = 14)
	#等同於 fig = plt.figure() ax = plt.subplot(111)
	#ax = plt.subplot(111)
	#ax = plt.subplots()
	
	#給子圖一個名稱後面設定給color
	sc = ax.scatter(xList, yList, c = color, s = scale, cmap = 'bwr', alpha = 0.7) 

	#設定X軸與Y軸字體大小
	ax.set_xlabel(xLabel, fontsize = 12)
	ax.set_ylabel(yLabel, fontsize = 12)
	
	#设置坐标轴刻度
	my_x_ticks = np.arange(0, (xlimit+1), (xlimit/10))
	my_y_ticks = np.arange(0, (ylimit+1), (ylimit/10))
	#plt.xticks(my_x_ticks)
	#plt.yticks(my_y_ticks)
	
	#设置刻度字体大小
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	
	#設置格線
	ax.grid(True)
	
	#有子圖時需將子圖設定給colorbar當對象
	cbar = plt.colorbar(sc)
	cbar.set_label(cbar_label,fontsize = 12)
	
	#设置图例
	#plt.legend(loc = 'best', fontsize = 12)
	
	#圖表過度集中可以使用.tight_layout分開
	plt.tight_layout()
	
	if filePath is not None:
		if not os.path.isdir(filePath):
			os.makedirs(filePath)
		filePath = os.path.join(filePath, filename)
		plt.savefig(filePath)   #儲存圖檔
	
	#显示图片
	#plt.show()
	plt.close()

def plotSingleScatter(xList, yList, s, color, title, xLabel, yLabel, xlimit=100, ylimit=1, filePath=None, filename=None):
	#沒有cmap
	#xLabel and yLabel must be word
	plt.style.use('dark_background')
	fig, ax = plt.subplots(figsize=(10, 6)) #plt.subplots是開出總畫布
	plt.title(title, fontsize = 14)
	
	#給子圖一個名稱後面設定給color
	sc = ax.scatter(xList, yList, c = color, s = s, alpha = 0.7) 

	#設定X軸與Y軸字體大小
	ax.set_xlabel(xLabel, fontsize = 12)
	ax.set_ylabel(yLabel, fontsize = 12)
	
	#设置坐标轴刻度
	my_x_ticks = np.arange(0, (xlimit+1), (xlimit/10))
	my_y_ticks = np.arange(0, (ylimit+1), (ylimit/10))
	#plt.xticks(my_x_ticks)
	#plt.yticks(my_y_ticks)
	
	#设置刻度字体大小
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	
	#設置格線
	ax.grid(True)
	
	#设置图例
	#plt.legend(loc = 'best', fontsize = 12)
	
	#圖表過度集中可以使用.tight_layout分開
	plt.tight_layout()
	
	if filePath is not None:
		if not os.path.isdir(filePath):
			os.makedirs(filePath)
		filePath = os.path.join(filePath, filename)
		plt.savefig(filePath)   #儲存圖檔
	
	#显示图片
	#plt.show()
	plt.close()

def plotMultiScatter(x, y, ax_num, inScale=None, inTitle=None, inXlabel=None, inYlabel=None, inPath=None, filename=None, legendillustration=None):
	#ax_num決定畫幾個陣列，例如傳5個陣列只畫3個
	#設置畫布背景顏色
	plt.style.use('dark_background')
	#設置畫布大小
	plt.figure(figsize=(13.66, 7.68)) 
	
	colorList = ['white', 'blue', 'green', 'yellow', 'red']
	#開一個畫布，所有圖共用
	
	if inScale == None:
		inScale = []
		for i in range(len(x)):
			inScale.append([])
			for j in range(len(x[i])):
				inScale[i].append(5)
	
	if ax_num == 2:
		#分有過關和沒過關
		if legendillustration is None:
			legendillustration = ['pass', 'loss']
		
		#print(x[0])
		#pass
		ax0 = plt.scatter(x[6], y[6], s = inScale[6], color = 'yellow', label=legendillustration[1], alpha = 0.7)
		#loss
		ax1 = plt.scatter(x[0], y[0], s = inScale[0], color = 'white', label=legendillustration[0], alpha = 0.7)	
		
		plt.legend([ax0, ax1], legendillustration, loc='best', edgecolor='w',  prop={'size':10})
	
	elif ax_num == 5:
		#星星用
		#设置图例
		if legendillustration is None:
			legendillustration = ['0star', '★', '★★', '★★★', '★★★★']
		
		#print(x[0])	
		ax0 = plt.scatter(x[0], y[0], s = inScale[0], color = 'white', label=legendillustration[0],  alpha = 0.7)
		ax1 = plt.scatter(x[1], y[1], s = inScale[1], color = 'blue', label=legendillustration[1],  alpha = 0.7)
		ax2 = plt.scatter(x[2], y[2], s = inScale[2], color = 'green', label=legendillustration[2],  alpha = 0.7)
		ax3 = plt.scatter(x[3], y[3], s = inScale[3], color = 'yellow', label=legendillustration[3],  alpha = 0.7)        
		ax4 = plt.scatter(x[4], y[4], s = inScale[4], color = 'red', label=legendillustration[4],  alpha = 0.7)
		#plt.legend([ax0, ax1, ax2, ax3, ax4], legendillustration, loc='best', edgecolor='w',  prop={'size':10})

	elif ax_num == 6:
		#難度等級用
		#设置图例
		if legendillustration is None:
			legendillustration = ['-3', '-2', '-1', '0', '1', '2']

		ax1 = plt.scatter(x[0], y[0], s = inScale[0], color = 'blue', label=legendillustration[0],  alpha = 0.7)
		ax2 = plt.scatter(x[1], y[1], s = inScale[1], color = 'skyblue', label=legendillustration[1],  alpha = 0.7)
		ax3 = plt.scatter(x[2], y[2], s = inScale[2], color = 'white', label=legendillustration[2],  alpha = 0.7)        
		ax4 = plt.scatter(x[3], y[3], s = inScale[3], color = 'yellow', label=legendillustration[3],  alpha = 0.7)
		ax5 = plt.scatter(x[4], y[4], s = inScale[4], color = 'orange', label=legendillustration[4],  alpha = 0.7)
		ax6 = plt.scatter(x[5], y[5], s = inScale[5], color = 'red', label=legendillustration[5],  alpha = 0.7)
		plt.legend([ax1, ax2, ax3, ax4, ax5, ax6], legendillustration, loc='best', edgecolor='w',  prop={'size':10})

	#設定X, Y軸標籤
	plt.xlabel(inXlabel, fontsize = 15)
	plt.ylabel(inYlabel, fontsize = 15)
	
	plt.title(inTitle, fontsize = 15)
	
	#設置格線
	plt.grid(True)     #格線為虛線，minor為次要格線
	
	#儲存圖片
	if inPath is not None:
		if not os.path.isdir(inPath):
			os.makedirs(inPath)
		fullpath = os.path.join(inPath, filename)
		plt.savefig(fullpath)

	#显示图片
	#plt.show()
	plt.close()
	
def plotLine(xList, YList, title, category, kvalue):
	#plt.style.use('dark_background')
	
	#設置畫布大小
	plt.figure(figsize=(13.66, 7.68))
	
	#plt.plot(xList, YList,'s-', color = 'g', label='Elo estimating')
	plt.plot(xList, YList, color = 'r', label='Elo estimating')
	
	# 標示x軸(labelpad代表與圖片的距離)
	plt.xlabel('answers', fontsize=30, labelpad = 15)
	# 標示y軸(labelpad代表與圖片的距離)
	plt.ylabel('elo', fontsize=30, labelpad = 20)
	# 標示title
	plt.title(title, fontsize = 15)
	
	# 顯示出線條標記位置
	plt.legend(loc = 'best', fontsize=20)
	#设置坐标轴范围
	#plt.xlim((-5, 5))     #也可写成plt.xlim(-5, 5) 
	plt.ylim((-3,3))     #也可写成plt.ylim(-4, 4)
	
	#设置坐标轴刻度
	#my_x_ticks = np.arange(-5, 5, 0.5)
	my_y_ticks = np.arange(-3, 4, 0.5)
	#plt.xticks(my_x_ticks)
	#plt.yticks(my_y_ticks)
	#設置格線
	plt.grid(True)     #格線為虛線，minor為次要格線 
	
	plt.xticks(fontsize=15)
	plt.yticks(fontsize=15)
	
	outpath = os.path.join('D:\\paper\\practice\\practice file\\EloRating\\Duck\\%s' %kvalue, category)
	if not os.path.isdir(outpath):
		os.makedirs(outpath)
	
	outpath = os.path.join(outpath, '%s.png' %title)
	plt.savefig(outpath)
	#plt.show()
	plt.close()

def plotBox(data, filePath, fileName, title = None, xLabel = None, yLabel = None, labels = None):
	#設置畫布大小
	plt.figure(figsize=(13.66, 7.68)) 
	if not os.path.isdir(filePath):
		os.makedirs(filePath)
	outPath = os.path.join(filePath, fileName)	
	plt.boxplot(data, labels = labels)    #作圖
	plt.title(title)
	plt.xlabel(xLabel)
	plt.ylabel(yLabel)
	plt.savefig(outPath)
	#plt.show()
	plt.close()

def columnFunc(j, k, x=0):
	columnList = []
	for i in range(j,k):
		columnList.append(x)
	return columnList

def readCSV(path):
	with open(path, newline = '') as csvfile:
		#讀取CSV檔案內容
		rows = csv.DictReader(csvfile)
		#column = [row[0] for row in rows]
		flag = False
		for row in rows:
			#第1行標頭不寫入串列
			if flag:
				sectionElo.append(float(row['sectionElo']))
			#第2行開始寫入    
			flag = True    
	return sectionElo

def Add_Difficulty(game):
	database = 'dotCode'
	collection = 'Sec_sta'
	ct = clientCT(database, collection)

	if game == 'Maze':
		maxsection = 40
	else:
		maxsection = 60

	Item_Difficulty = []
	Difficulty_Degree = []

	for section in range(1, maxsection+1):
		for one in ct.find({'gameCode': game, 'sectionId':section}):
			Item_Difficulty.append([one['sectionId'], one['difficulty']])
			Difficulty_Degree.append([one['sectionId'], one['difficultyDegree']])
	return Item_Difficulty, Difficulty_Degree

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

def calculate_standarderror(x):
	print(len(x))
	total_x = 0
	for num in x:
		total_x += num
	mu = total_x/len(x)
	
	error_square = 0
	total_errorSquare = 0
	for num in x:
		error_square = (num - mu)**2
		total_errorSquare += error_square
		
	sigma = (total_errorSquare/len(x))**0.5
	print("sigma=", sigma)
	return sigma


gameCode =['Maze', 'Duck']
game = 'Duck'
if (game == 'Maze'):
	maxSection = 40
elif (game == 'Duck'):	
	maxSection = 60

degree = [-3, -2, -1, 0, 1, 2]
item_difficulty = Add_Difficulty('Duck')
difficulty_list = []
for item in item_difficulty[0]:
	difficulty_list.append(item[1])
	
while 1:
	value = int(input('''(1)Plot ralation between correct percentage and accumulated time(AccuTime)
(2)Plot Relation Between Difficulty and Game Time and Star On First Record(FirstRecord)
(3)Relation between time taken to respond to an item and try times(AccuTime)
(4)Relation between time taken(every y seconds) and average correct percentage(AccuTime_sta)
(5)Relation between time taken(per second) and average correct percentage(FirstRecord_sta)
(6)Section and User's Elo
(7)時間的盒鬚圖\n:'''))
			

	## value = 1
	# 散佈點圖，所有關卡合在一起，每筆資料1個點
	if(value == 1):
		startTime = time.time()     
		database = 'dotCode'
		collection = 'AccuTime'
		
		ct = clientCT(database, collection)
		
		limitTime = 21600
		for section in range(1, 61):    
			avgCorrect = []       # Y軸
			timeTaken = []        # X軸
			logTime = []
			log_ZTime = []
			color_axis = []    
			for i in range(0,5):
				timeTaken.append([])
				avgCorrect.append([])
				logTime.append([])
				log_ZTime.append([])
				for one in ct.find({'sectionId':section, 'accumulatedTime':{'$lte':limitTime}, 'gameStar':i}):
					avgCorrect[i].append(one['correctPercentage'])
					timeTaken[i].append(one['accumulatedTime'])
					logTime[i].append(one['logTime_sec'])
					log_ZTime[i].append(one['ZTimeLog'])
		
			## plot Accumulated Time 
			labelList = ['0star points', '1star points', '2star points', '3star points', '4star points']
			
			#設定X, Y軸標籤
			xlabel = 'Accumulated Time, limit:%d seconds, section:%d' %(limitTime, section)
			ylabel = 'Correct Percentage'
			
			path = 'D:\\paper\\practice\\practice file\\Scatter\\Accumulated Time\second'
			file = 'section%d.png' %section 
			plotMultiScatter(timeTaken, avgCorrect, labelList, inScale=None, inAlpha=0.5, inXlabel=xlabel, inYlabel=ylabel, inPath=path, filename=file)
		
			## Plot Log10 of Accumulated Time
			print('Log10 of Accumulated Time') 
			
			# 設定X, Y軸標籤
			xlabel = 'Log10 Accumulated Time'
			ylabel = 'Correct Percentage'
			
			path = 'D:\\paper\\practice\\practice file\\Scatter\\Accumulated Time\\log'
			file = 'section%d.png' %section
			plotMultiScatter(logTime, avgCorrect, labelList, inScale=None, inAlpha=0.5, inXlabel=xlabel, inYlabel=ylabel, inPath=path, filename=file)
			
			## Plot Z of Log10 Accumulated Time
			print('Z of Log10 Accumulated Time')
		
			# 設定X, Y軸標籤
			xlabel = 'Z of Log10 Accumulated Time'
			ylabel = 'Correct Percentage'
			
			path = 'D:\\paper\\practice\\practice file\\Scatter\\Accumulated Time\\Z-log'
			file = 'section%d.png' %section 
			plotMultiScatter(log_ZTime, avgCorrect, labelList, inScale=None, inAlpha=0.5, inXlabel=xlabel, inYlabel=ylabel, inPath=path, filename=file)
		

	## value = 2  Relation Between Difficulty and Time and Stars On The First Record
	if(value == 2):
		startTime = time.time()  
		database = 'dotCode'
		collection = 'FirstRecord'
			
		ct = clientCT(database, collection)
		
		#每一關第1次遊戲時間與難度的關係
		timeLimit = 3600000
		colorList= ['w', 'b', 'g', 'y', 'r']
		labelList = ['0star', '★', '★★', '★★★', '★★★★']
		
		print('collecting data...')
		for i in range(0,5):
			timeTaken = []
			difficulty = []
			for section in range(1, 61):
				for one in ct.find({'sectionId':section, 'gameTime':{'$lte':timeLimit}, 'gameStar':i}):
					timeTaken.append(one['gameTime']/1000)
					difficulty.append(one['difficulty'])
			
			xlabel = 'Time'
			ylabel = 'Difficulty'
			title = 'Relation between game time and item difficulty\n and stars on the first record'
			
			p = 'D:\\paper\\practice\\practice file\\Scatter\\every points\\Time'
			fileName = '%dstar.png' %i
			plotSingleScatter(timeTaken, difficulty, 12, colorList[i], title, xlabel, ylabel, xlimit=timeLimit, ylimit=1, filePath=p, filename=fileName)    


	# value = 3
	## relationship between time taken to respond to an item and try times
	if(value == 3):
		startTime = time.time()
		database = 'dotCode'
		collection = 'AccuTime'
		ct = clientCT(database, collection)
		ct.create_index([('gameCode', 1), ('sectionId', 1), ('accumulatedTime_sec', 1), ('tryCount', 1), ('gameStar', 1)])
		
		xlabel = 'Time Taken(second)'
		ylabel = 'difficulty'
		#labels = ['0star', '1star', '2star', '3star', '4star']
		labels = ['0star', '★', '★★', '★★★', '★★★★']
		
		color = 'difficulty' 
		
		timeLimit = 6000
		ylimit = 1
		#c sequence
		if (color == 'difficulty'):
			c = difficulty_list
			colorBar_label = 'Difficulty'
		elif (color == 'student'):
			c = student_elo
			colorBar_label = 'Student Elo' 
		else:
			c = None
			
		difficulty_all = []
		student_elo_all = []
		tryTimes_all = []
		logtimeTaken_all = []	
		timeTaken_all = []
		correctness_all = []
		people_all = []
		for section in range(1, maxSection+1):
			difficulty = []
			student_elo = []
			tryTimes = []
			logtimeTaken = []
			timeTaken = []
			people = []
			correctness = []
			
			for i in range(0,5):
				difficulty.append([])
				student_elo.append([])
				tryTimes.append([])
				logtimeTaken.append([])
				timeTaken.append([])
				correctness.append([])
				people.append([])
				for one in ct.find({'gameCode':'Duck', 'sectionId':section, 'accumulatedTime_sec':{'$lt':timeLimit}, 'tryCount':{'$lt':300}, 'gameStar':i}):
					difficulty[i].append(one['difficulty'])
					#student_elo[i].append(one['elo_001'])
					tryTimes[i].append(one['tryCount'])
					logtimeTaken[i].append(one['logTime_sec'])
					timeTaken[i].append(one['accumulatedTime_sec'])
					correctness[i].append(one['correctPercentage'])
					people[i].append(5)
					
					difficulty_all.append(one['difficulty'])
					tryTimes_all.append(one['tryCount'])
					logtimeTaken_all.append(one['logTime_sec'])	
					timeTaken_all.append(one['accumulatedTime_sec'])
					correctness_all.append(one['correctPercentage'])
					people_all.append(5)
					
			## 各關卡
			title = 'The relationship between time taken and try times.\nSection%d, Difficulty = %f' %(section, difficulty_list[section-1])
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Every Points\\Accumulated Time\\Time Taken And Elo'
			fileName = 'section%d' %section
			plotMultiScatter(timeTaken, difficulty, 5, people, title, inXlabel=xlabel, inYlabel=ylabel, inPath=p, filename=fileName, legendillustration=labels)

		## 所有關卡全覽
		title = 'The relationship between the time taken to respond to an item,and try times.'
		plotScatter(timeTaken_all, tryTimes_all, difficulty_all, people_all, title, xlabel, 'try times', colorBar_label, timeLimit, ylimit, filePath=p, filename='All sections') 
		#plotScatter(timeTaken_all, student_elo_all, difficulty_all, 5, title, 'Time Taken(second)', 'Student Elo', colorBar_label, timeLimit, ylimit, filePath=p, filename='Time taken and student elo(All sections).png')


	# value = 4 AccuTime
	### 4-1 AccuTime_sta
	if(value == 4):
		database = 'dotCode'
		collection = 'AccuTime_sta'

		ct = clientCT(database, collection)
		
		ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('difficultyDegree', 1)])
		ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('difficultyDegree', 1)])

		timelimit = 55000
		size = 0.55
		multiple = 3
		y = 10
		
		print('plot relation between accumulated time taken(second) and average correct percentage')
		startTime = time.time()        
		## 依關卡
		for section in range(1, maxSection+1):
			timeTaken_all = []
			avgTryCount_all = []
			avgCorrect_all = []
			countness_all = []
			difficulty_all = []
			star_all = []
			for i in range(0, 7):	# 星星數 5是全部 6是有過關
				timeTaken_all.append([])
				avgTryCount_all.append([])
				avgCorrect_all.append([])
				countness_all.append([])
				difficulty_all.append([])
				star_all.append([])
				for second in range(0, timelimit, y):
					for one in ct.find({'sectionId':section, 'tickTime':10, 'gameStar':i, 'seconds':second, 'avgTryCount':{'$lt':100}}):
						timeTaken_all[i].append(one['seconds'])
						avgTryCount_all[i].append(one['avgTryCount'])
						avgCorrect_all[i].append(one['avgCorrectness'])
						countness_all[i].append(one['people']**size*multiple)
						difficulty_all[i].append(one['difficulty'])
						star_all[i].append(one['gameStar'])
			
			# 設定X, Y軸標籤(要在pltscatter前面設定好)
			xlabel = 'Accumulated Time Taken(seconds)'
			ylabel = 'Average Try Times'
			title = 'Relation Between Accumulated Time And Average Try Times \n Section:%d Difficulty:%f' %(section, difficulty_list[section-1])
			# 檔名
			fileName = 'section%d.png' %section
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Accumulated Time\\%s\\section\\mixstar' %timelimit
			
			# 合併星星
			plotSingleScatter(timeTaken_all[5], avgTryCount_all[5], countness_all[5], 'skyblue', title, xlabel, ylabel, xlimit=timelimit, ylimit=1, filePath=p, filename=fileName)
			
			# 分開星星
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Accumulated Time\\%s\\section\\allstar' %timelimit
			plotMultiScatter(timeTaken_all, avgTryCount_all, 5, countness_all, title, xlabel, ylabel, inPath=p, filename=fileName)

			# 有過關和沒過關section\\
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Accumulated Time\\%s\\section\\過關和沒過關' %timelimit
			plotMultiScatter(timeTaken_all, avgTryCount_all, 2, countness_all, title, xlabel, ylabel, inPath=p, filename=fileName)
			
			del timeTaken_all, avgTryCount_all, avgCorrect_all, countness_all, difficulty_all
			

		## 依難度等級	
		
		dtimeTaken_all = []
		davgCorrect_all = []
		davgTryCount_all = []
		dcountness_all = []
		
		for i in range(0, len(degree)):
			dtimeTaken = []
			davgCorrect = []
			davgTryCount = []
			dcountness = []
		
			dtimeTaken_all.append([])
			davgCorrect_all.append([])
			davgTryCount_all.append([])
			dcountness_all.append([])
			for j in range(0,7):
				dtimeTaken.append([])
				davgCorrect.append([])
				davgTryCount.append([])
				dcountness.append([])
				for second in range(0, timelimit, y):
					for one in ct.find({'sectionId':0, 'tickTime':10, 'gameStar':j, 'seconds':second, 'difficultyDegree':degree[i]}):
						dtimeTaken[j].append(one['seconds'])
						davgCorrect[j].append(one['avgCorrectness'])
						davgTryCount[j].append(one['avgTryCount'])
						dcountness[j].append(one['people']**size*multiple)

						#if j == 5:	# 每一個難度級別在不分星的時候才加
						if j == 6: # 每一個難度級別只算有過關
							dtimeTaken_all[i].append(one['seconds'])
							davgCorrect_all[i].append(one['avgCorrectness'])
							davgTryCount_all[i].append(one['avgTryCount'])
							dcountness_all[i].append(one['people']**size*multiple)						
						
			# 設定X, Y軸標籤(要在pltscatter前面設定好)
			xlabel = 'Accumulated Time Taken(second)'
			ylabel = 'Average Try Times'
			
			# 同一難度不同星星間的比較
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Accumulated Time\\%s\\difficulty' %timelimit
			title = 'Relation Between Different Stars on the Difficulty%s' %degree[i]
			fileName = '(%s)stars_difficulty%s.png' %(j, degree[i])
			plotMultiScatter(dtimeTaken, davgTryCount, 5, dcountness, title, xlabel, ylabel, inPath=p, filename=fileName)
			
			# 同一難度有過關和沒過關的比較
			title = 'Relation Between Pass And Loss On the Difficulty%s' %degree[i]
			fileName = '%s.pass & loss_difficulty%s.png' %(i+1, degree[i])
			plotMultiScatter(dtimeTaken, davgTryCount, 2, dcountness, title, xlabel, ylabel, inPath=p, filename=fileName)
			
			del dtimeTaken, davgCorrect, davgTryCount, dcountness
		
		# 不分星星
		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Accumulated Time\\%s\\difficulty' %timelimit
		fileName = '不分星平均.png'
		title = 'Relation Between Different Difficulty'
		plotMultiScatter(dtimeTaken_all, davgTryCount_all, 6, dcountness_all, title, xlabel, ylabel, inPath=p, filename=fileName)
			
		del dtimeTaken_all, davgCorrect_all, davgTryCount_all, dcountness_all
		
		## 依時間
		timeTaken = []
		avgCorrect = []
		avgTryCount = []
		difficulty = []
		countness = []
		for second in range(0, timelimit, y):
			for one in ct.find({'sectionId':0, 'tickTime':10, 'gameStar':6, 'seconds':second, 'difficultyDegree':'n'}):
				timeTaken.append(one['seconds'])
				avgCorrect.append(one['avgCorrectness'])
				avgTryCount.append(one['avgTryCount'])
				difficulty.append(one['difficulty'])
				countness.append(one['people']**size*multiple)
			
		# 設定各項標籤
		xlabel = 'Time Taken(second)'
		ylabel = 'Average Try Times'
		title = 'Relation Between Accumulated Time And Average Try Times'
		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Accumulated Time\\%s' %timelimit
		fileName = 'Average Difficulty On Second'
		if one['gameStar'] == 6:
			title = 'Relation Between Accumulated Time And Average Try Times(Pass)'
			fileName = 'Average Difficulty On Second(Pass)'
		colorbar_label = 'Difficulty'

		
		plotScatter(timeTaken, avgTryCount, difficulty, countness, title, xlabel, ylabel, cbar_label=colorbar_label, xlimit=100, ylimit=1, filePath=p, filename=fileName)
		
		#for i, j, k in zip(timeTaken, difficulty, avgCorrect):
			#print("timeTaken:", i, "difficulty:", j, "avgCorrect:", k)
		
		### 4-2 AccuTimeLog_sta

		database = 'dotCode'
		collection = 'AccuTimeLog_sta'

		ct = clientCT(database, collection)
		ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_log', 1), ('difficultyDegree', 1)])
		ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_log', 1), ('difficultyDegree', 1)])
		
		timelimit = 20
		size = 0.55
		multiple = 3
		
		print('plot relation between log accumulated time and average correct percentage')	
		##依關卡
		for section in range(1, maxSection+1):
			#if(section >= 50):
				#size = 1
				#multiple = 1
			timeTaken_all = []
			avgTryCount_all = []
			avgCorrect_all = []
			countness_all = []
			difficulty_all = []
			star_all = []
			for i in range(0, 7):	# 星星數 5是全部 6是有過關
				timeTaken_all.append([])
				avgTryCount_all.append([])
				avgCorrect_all.append([])
				countness_all.append([])
				difficulty_all.append([])
				star_all.append([])
				for second in np.arange(-2.5, timelimit, 0.1):
					second = round(second, 2)
					for one in ct.find({'sectionId':section, 'tickTime':0.1, 'gameStar':5, 'seconds_log':second}):
						timeTaken_all[i].append(one['seconds_log'])
						avgTryCount_all[i].append(one['avgTryCount'])
						avgCorrect_all[i].append(one['avgCorrectness'])
						countness_all[i].append(one['people']**size*multiple)
						difficulty_all[i].append(one['difficulty'])
						star_all[i].append(one['gameStar'])
			
			# 設定X, Y軸標籤(要在pltscatter前面設定好)        
			xLabel = 'Log Accumulated Time Taken'
			yLabel = 'Average Try Times'
			title = 'Relation Between Log Accumulated Time Taken And Average Try Times \n Section:%d Difficulty:%f' %(section, difficulty_list[section-1])
			# 檔名
			fileName = 'section%d.png' %section
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Log Accumulated Time\\%s\\section' %timelimit
			
			# 合併星星
			plotSingleScatter(timeTaken_all[5], avgTryCount_all[5], countness_all[5], 'skyblue', title, xLabel, yLabel, xlimit=timelimit, ylimit=1, filePath=p, filename=fileName)
			
			del timeTaken_all, avgTryCount_all, countness_all, difficulty_all, star_all
			
		## 依難度等級	
		dtimeTaken_all = []
		davgCorrect_all = []
		davgTryCount_all = []
		dcountness_all = []
		for i in range(0, len(degree)):
			dtimeTaken = []
			davgCorrect = []
			davgTryCount = []
			dcountness = []
		
			dtimeTaken_all.append([])
			davgCorrect_all.append([])
			davgTryCount_all.append([])
			dcountness_all.append([])
			for j in range(0,7):
				dtimeTaken.append([])
				davgCorrect.append([])
				davgTryCount.append([])
				dcountness.append([])
				for second in np.arange(-2.5, timelimit, 0.1):	
					second = round(second, 2)
					#print("degree:", degree[i])
					for one in ct.find({'sectionId':0, 'tickTime':0.1, 'gameStar':j, 'seconds_log':second, 'difficultyDegree':degree[i]}):
						#print(one)
						if (one['avgTryCount'] <= 100):
							dtimeTaken[j].append(one['seconds_log'])
							davgCorrect[j].append(one['avgCorrectness'])
							davgTryCount[j].append(one['avgTryCount'])
							dcountness[j].append(one['people']**size*multiple)
						if j == 5 and one['avgTryCount'] <= 100:
							dtimeTaken_all[i].append(one['seconds_log'])
							davgCorrect_all[i].append(one['avgCorrectness'])
							davgTryCount_all[i].append(one['avgTryCount'])
							dcountness_all[i].append(one['people']**size*multiple)	

			# 設定X, Y軸標籤(要在pltscatter前面設定好)
			xlabel = 'Log Accumulated Time Taken'
			ylabel = 'Average Try Times'

			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Log Accumulated Time\\%s\\difficulty' %timelimit
			title = 'Relation Between Different Stars On The Difficulty%s' %degree[i]
			fileName = '(%s)stars_difficulty%s.png' %(i+1, degree[i])
			plotMultiScatter(dtimeTaken, davgTryCount, 5, dcountness, title, xlabel, ylabel, inPath=p, filename=fileName)

			title = 'Relation Between Pass And Loss On The Difficulty%s' %degree[i]		
			fileName = '%s.pass & loss_difficulty%s.png' %(i+1, degree[i])
			plotMultiScatter(dtimeTaken, davgTryCount, 2, dcountness, title, xlabel, ylabel, inPath=p, filename=fileName)
			
			del dtimeTaken, davgCorrect, davgTryCount, dcountness 
	
		# 不分星星
		title = 'Relation Between Different Difficulty'
		#fileName = 'different difficulty_pass.png'
		#plotMultiScatter(dtimeTaken_all, davgTryCount_all, 6, dcountness_all, title, xlabel, ylabel, inPath=p, filename=fileName)
		
		fileName = 'different difficulty_pass&loss.png'	
		plotMultiScatter(dtimeTaken_all, davgTryCount_all, 6, dcountness_all, title, xlabel, ylabel, inPath=p, filename=fileName)
		
		del dtimeTaken_all, davgCorrect_all, davgTryCount_all, dcountness_all
						
		##依時間
		timeTaken = []
		avgCorrect = []
		avgTryCount = []
		difficulty = []
		countness = []
		for second in np.arange(-2.5, timelimit, 0.1):
			second = round(second, 2)
			#全部含未過關
			#for one in ct.find({'sectionId':0, 'tickTime':0.1, 'gameStar':5, 'seconds_log':second, 'difficultyDegree':'n'}):
			#只找有過關
			for one in ct.find({'sectionId':0, 'tickTime':0.1, 'gameStar':6, 'seconds_log':second, 'difficultyDegree':'n'}):			
				timeTaken.append(one['seconds_log'])
				avgCorrect.append(one['avgCorrectness'])
				avgTryCount.append(one['avgTryCount'])
				difficulty.append(one['difficulty'])
				countness.append(one['people']**size*multiple)
		# 設定各項標籤       
		xlabel = 'Log Accumulated Time Taken'
		colorbar_label = 'Difficulty'
		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Log Accumulated Time\\%s' %timelimit
		
		ylabel = 'Average Correctness Percentage'
		title = 'Relation Between Log Accumulated Time And Average Correct Percentage'
		fileName = 'Average Correct Percentage On Log Accumulated Time'
		
		if one['gameStar'] == 6: 
			title = 'Relation Between Log Accumulated Time And Average Correct Percentage(Pass)'
			fileName = 'Average Correct Percentage On Log Accumulated Time(Pass)'		
		plotScatter(timeTaken, avgCorrect, difficulty, countness, title, xlabel, ylabel, cbar_label=colorbar_label, xlimit=20, ylimit=1, filePath=p, filename=fileName)
		
		
		ylabel = 'Average Try Times'
		title = 'Relation Between Log Time And Average Try Times'
		fileName = 'Average Try Times On Log Accumulated Time'
		
		if one['gameStar'] == 6: 
			title = 'Relation Between Log AccumulatedTime And Average Try Times(Pass)'
			fileName = 'Average Try Times On  Log Accumulated Time(Pass)'
		plotScatter(timeTaken, avgTryCount, difficulty, countness, title, xlabel, ylabel, cbar_label=colorbar_label, xlimit=20, ylimit=1, filePath=p, filename=fileName)
		
		del timeTaken, avgCorrect, avgTryCount, difficulty, countness

		### 4-3 AccuTimeZ_sta
		database = 'dotCode'
		collection = 'AccuTime_sta'

		ct = clientCT(database, collection)
		
		ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
		ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
				
		timelimit = 10
		size = 0.55
		multiple = 3
		y = 0.1
		
		print('plot relation between accumulated time taken(second) and average correct percentage')        
			
		##依時間
		timeTaken = []
		avgCorrect = []
		avgTryCount = []
		difficulty = []
		countness = []
		for star in range(0, 5): 
			timeTaken.append([])
			avgCorrect.append([])
			avgTryCount.append([])
			difficulty.append([])
			countness.append([])
			for second in np.arange(-0.8, timelimit, 0.1):
			#for second in range(-1, timelimit, 1):
				second = round(second, 2)
				for one in ct.find({'sectionId':0, 'tickTime':0.1, 'gameStar':star, 'seconds_z':second}):			
					if one['avgTryCount'] <= 80:
						timeTaken[star].append(one['seconds_z'])
						avgCorrect[star].append(one['avgCorrectness'])
						avgTryCount[star].append(one['avgTryCount'])
						difficulty[star].append(one['difficulty'])
						countness[star].append(one['people']**size*multiple)
					
		# 設定各項標籤       
		xlabel = 'Standardized Accumulated Time Taken'
		colorbar_label = 'Difficulty'
		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Standardized Accumulated Time\\%s' %timelimit
		
		ylabel = 'Average Try Times'
		title = 'Relation Between Standardized Accumulated Time And Average Try Times'
		fileName = 'Average Try Times On Standardized Accumulated Time_tickTime'
		
		plotMultiScatter(timeTaken, avgTryCount, 5, countness, title, xlabel, ylabel, inPath=p, filename=fileName)
			
		del timeTaken, avgCorrect, avgTryCount, difficulty, countness
	
	
	# value = 5 FirstRecord_sta
	if(value == 5):
		print('plot relation between time taken(second) and average correct percentage')
		startTime = time.time()        
		
		database = 'dotCode'
		collection = 'FirstRecord_sta'

		ct = clientCT(database, collection)
		
		ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('difficultyDegree', 1)])
		
		timelimit = 101
		size = 0.55
		multiple = 3
		
		## 依關卡
		for section in range(1, maxSection+1):
			timeTaken = []
			avgCorrect = []
			countness = []
			difficulty = []
			star = []
			for i in range(0, 6):#星星數
				timeTaken.append([])
				avgCorrect.append([])
				countness.append([])
				difficulty.append([])
				star.append([])
				for second in range(0, timelimit):
					for one in ct.find({'sectionId':section, 'tickTime':1, 'gameStar':i, 'seconds':second}):
						timeTaken[i].append(one['seconds'])
						avgCorrect[i].append(one['avgCorrectness'])
						countness[i].append(one['people']**size*multiple)
						difficulty[i].append(one['difficulty'])
						star[i].append(one['gameStar'])
		
			# 設定X, Y軸標籤(要在pltscatter前面設定好)
			xlabel = 'Time Taken(second)'
			ylabel = 'Average Correctness Percentage'
			title = 'Relation Between Game Time And Average Correct Percentage On The First Record\n Section:%d Difficulty:%f' %(section, one['difficulty'])
			
			# 合併星星圖
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Game Time\\%s\\mixstar' %timelimit
			fileName = 'section%d.png' %section
			plotSingleScatter(timeTaken[5], avgCorrect[5], countness[5], 'skyblue', title, xlabel, ylabel, xlimit=timelimit, ylimit=1, filePath=p, filename=fileName)
			
			# 星星分開圖(正確率都是1，畫出來的圖沒有意義)
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Game Time\\%s\\allstar' %timelimit
			fileName = 'section%d.png' %section
			plotMultiScatter(timeTaken, star, 5, countness, xlabel, ylabel, inPath=p, filename=fileName)
			
			del timeTaken, avgCorrect, countness, difficulty
		
		##依難度等級	
		# 全部星星合併
		dtimeTaken = []
		davgCorrect = []
		dcountness = []
		
		for i in range(0,len(degree)):
			dtimeTaken.append([])
			davgCorrect.append([])
			dcountness.append([])
			
			# 星星分開
			dstime_taken = []
			dsavgCorrect = []
			dscountness = []
			for stars in range(0, 6):
				if(stars < 5):
					dstime_taken.append([])
					dsavgCorrect.append([])
					dscountness.append([])
				for second in range(1, timelimit):
					for one in ct.find({'sectionId':0, 'tickTime':1, 'gameStar':stars, 'seconds':second, 'difficultyDegree':degree[i-2]}):
						if (stars == 5):
							dtimeTaken[i].append(one['seconds'])
							davgCorrect[i].append(one['avgCorrectness'])
							dcountness[i].append(one['people']**size*multiple)
						elif(0 < stars <= 4):
							dstime_taken[stars].append(one['seconds'])
							dsavgCorrect[stars].append(one['avgCorrectness'])
							dscountness[stars].append(one['people']**size*multiple)
			print(len(dstime_taken))
			# 設定X, Y軸標籤(要在pltscatter前面設定好)        
			xlabel = 'Time Taken(second)'
			ylabel = 'Average Correctness Percentage'
			title = 'Relation between game time and average correct percentage on the first record'
		
			# 星星分開圖
			p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Game Time\\%s' %timelimit
			fileName = 'difficulty degree%s_%sstars.png' %(i, stars)
			plotMultiScatter(dstime_taken, dsavgCorrect, dscountness, xlabel, ylabel, inPath=p, filename=fileName)
		
			del dstime_taken, dsavgCorrect, dscountness
		
		# 設定X, Y軸標籤(要在pltscatter前面設定好)        
		xlabel = 'Time Taken(second)'
		ylabel = 'Average Correctness Percentage'
		title = 'Relation between game time and average correct percentage on the first record'
		
		# 合併星星圖
		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Game Time\\%s' %timelimit
		fileName = 'all difficulty degree'
		plotMultiScatter(dtimeTaken, davgCorrect, dcountness,  xlabel, ylabel, inPath=p, filename=fileName)
		
		del dtimeTaken, davgCorrect, dcountness
		
		## 依時間
		timeTaken = []
		avgCorrect = []
		difficulty = []
		countness = []
		for second in range(1, timelimit):
			for one in ct.find({'sectionId':0, 'tickTime':1, 'gameStar':5, 'seconds':second, 'difficultyDegree':'n'}):
				timeTaken.append(one['seconds'])
				avgCorrect.append(one['avgCorrectness'])
				difficulty.append(one['difficulty'])
				countness.append(one['people']**size*multiple)
			
		# 設定各項標籤       
		xlabel = 'Time Taken(second)'
		ylabel = 'Average Correctness Percentage'
		title = 'Relation between game time and average correct percentage on the first record'
		colorbar_label = 'Difficulty'

		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Game Time\\%s' %timelimit
		fileName = 'Average difficulty on second'
		plotScatter(timeTaken, avgCorrect, difficulty, countness, title, xlabel, ylabel, cbar_label=colorbar_label, xlimit=100, ylimit=1, filePath=p, filename=fileName)
		
		del timeTaken, avgCorrect, countness
		
		#for i, j, k in zip(timeTaken, difficulty, avgCorrect):
			#print("timeTaken:", i, "difficulty:", j, "avgCorrect:", k)

		###5-2 FirstRecordLog_sta
		print('plot relation between log time taken(second) and average correct percentage')
		startTime = time.time()        
		
		database = 'dotCode'
		collection = 'FirstRecordLog_sta'

		ct = clientCT(database, collection)
		
		ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_log', 1), ('difficultyDegree', 1)])
		
		timelimit = 20
		size = 0.55
		multiple = 3
		
		p = 'D:\\paper\\practice\\practice file\\Scatter\\Statistic\\Log Game Time\\%s' %timelimit
		
		##依關卡
		for section in range(1, maxSection+1):
			#if(section >= 50):
				#size = 1
				#multiple = 1
			timeTaken = []
			avgCorrect = []
			countness = []
			difficulty = []
			for second in np.arange(-2.4, timelimit, 0.1):
				second = round(second, 2)
				for one in ct.find({'sectionId':section, 'tickTime':0.1, 'gameStar':5, 'seconds_log':second}):
					timeTaken.append(one['seconds_log'])
					avgCorrect.append(one['avgCorrectness'])
					countness.append(one['people']**size*multiple)
					difficulty.append(one['difficulty'])
					#print(one)
					#os.system('Pause')
					#print('section:', section, timeTaken)
			
			# 設定X, Y軸標籤(要在pltscatter前面設定好)        
			xLabel = 'Time Taken(log second)'
			yLabel = 'Average Correctness Percentage'
			title = 'Relation Between Game Time And Average Correct Percentage On The First Record\n Section:%d Difficulty:%f' %(section, one['difficulty'])
			
			fileName = 'section%d.png' %section
			plotSingleScatter(timeTaken, avgCorrect, countness, 'skyblue', title, xLabel, yLabel, xlimit=timelimit, ylimit=1, filePath=p, filename=fileName)
			
			del timeTaken, avgCorrect, countness, difficulty
		
		##依難度等級
		dtimeTaken = []
		davgCorrect = []
		dcountness = []
		
		for i in range(0,len(degree)):
			dtimeTaken.append([])
			davgCorrect.append([])
			dcountness.append([])
			
			dstime_taken = []
			dsavgCorrect = []
			dscountness = []
			for stars in range(0, 6):
				if (stars < 5):
					dstime_taken.append([])
					dsavgCorrect.append([])
					dscountness.append([])
				for second in np.arange(-2.5, timelimit, 0.1):
					second = round(second, 2)
					for one in ct.find({'sectionId':0, 'tickTime':0.1, 'seconds_log':second, 'gameStar':stars, 'difficultyDegree':degree[i]}):
						if (stars == 5):
							dtimeTaken[i].append(one['seconds_log'])
							davgCorrect[i].append(one['avgCorrectness'])
							dcountness[i].append(one['people']**size*multiple)
						elif(0 <= stars <= 4):
							dstime_taken[stars].append(one['seconds_log'])
							dsavgCorrect[stars].append(one['avgCorrectness'])
							dscountness[stars].append(one['people']**size*multiple)
				
			#設定X, Y軸標籤(要在pltscatter前面設定好)        
			xlabel = 'Time Taken(second)'
			ylabel = 'Average Correctness Percentage'
			title = 'Relation between game time and average correct percentage on the first record'
		
			#星星分開圖
			fileName = 'difficulty degree%s.png' %i
			plotMultiScatter(dstime_taken, dsavgCorrect, dscountness, title, xlabel, ylabel, inPath=p, filename=fileName)
			
			del dstime_taken, dsavgCorrect, dscountness
		
		#設定X, Y軸標籤(要在pltscatter前面設定好)        
		xlabel = 'Time Taken(log second)'
		ylabel = 'Average Correctness Percentage'
		title = 'Relation between game time and average correct percentage on the first record'
		
		fileName = 'all difficulty degree.png'
		legendillus = ['-3', '-2', '-1', '0', '1', '2']
		plotMultiScatter(dtimeTaken, davgCorrect, dcountness, title, xlabel, ylabel, inPath=p, filename=fileName, legendillustration = legendillus)
		
		del dtimeTaken, davgCorrect, dcountness
		
		##依時間
		timeTaken = []
		avgCorrect = []
		difficulty = []
		countness = []
		for second in np.arange(-2.4, timelimit, 0.1):
			second = round(second, 2)
			for one in ct.find({'sectionId':0, 'tickTime':0.1, 'gameStar':5, 'seconds_log':second, 'difficultyDegree':'n'}):
				timeTaken.append(one['seconds_log'])
				avgCorrect.append(one['avgCorrectness'])
				difficulty.append(one['difficulty'])
				countness.append(one['people']**size*multiple)

		#設定各項標籤       
		xlabel = 'Time Taken(log second)'
		ylabel = 'Average Correctness Percentage'
		title = 'Relation between log game time and average correct percentage on the first record'
		colorbar_label = 'Difficulty'

		
		fileName = 'Average difficulty on log second'
		plotScatter(timeTaken, avgCorrect, difficulty, countness, title, xlabel, ylabel, cbar_label=colorbar_label, xlimit=20, ylimit=1, filePath=p, filename=fileName)
		
		del timeTaken, avgCorrect, countness,
		
	#value = 6
	##讀取CSV檔畫ELO
	if(value == 6):
		choice = int(input('(1)section elo\n(2)student elo\n:'))
		startTime = time.time() 
		k = str(0.1)
		if(choice ==1):
			path = 'D:\\paper\\practice\\practice file\\EloRating\\Duck\\%s' %k
			files = os.listdir(path)
			for file in files:
				if file.find('DuckElo') > -1:
					sectionElo = []
					fullpath = os.path.join(path, file)
					if(os.path.isfile(fullpath)):
						print(file)
						title = file[:file.find('.')]
						sectionElo = readCSV(fullpath)
						answers = []
						i = 0
						while(i < len(sectionElo)):
							answers.append(i+1)
							i += 1
						#plt.figure(figsize=(10, 6)) 
						plotLine(answers, sectionElo, title, 'eloplot', k)
		
		if(choice ==2):
			print('plot relation between second and average correct percentage')
			startTime = time.time()        
			##依序畫出各個玩家
			database = 'dotCode'
			collection = 'FirstPass'
		
			ct = clientCT(database, collection)
		
			for id in range(1, 690000):
				title = 'User%d Elo History' %id
				answers = []
				eloHist = []
				for section in range(1, 61):
					for one in ct.find({'userId':id, 'sectionId':section}):
						eloHist.append(one['elo'])
				
				if(len(eloHist) > 300):
					i = 0
					while (i < len(eloHist)):
						answers.append(i+1)
						i += 1
					plotLine(answers, eloHist, title, 'user elo')
					print(id)

	#時間的盒鬚圖
	if value == 7:
		np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
		sec_difficulty = Add_Difficulty('Duck')[0]
		sec_difficulty = bubbleSort(sec_difficulty, y = 1)
		#print(sec_difficulty)
		#os.system("pause")
		
		startTime = time.time()        
		database = 'dotCode'
		collection = 'FirstRecord'
		
		ct = clientCT(database, collection)
		ct.create_index([('sectionId', 1), ('gameStar', 1)])
		
		p = 'D:\\paper\\practice\\practice file\\box\\First Record'
		
		print('plot box of First Record')
		data = []
		i = 0
		while i < len(sec_difficulty):
			data.append([])
			#print(sec_difficulty[i][0])#關卡
			for one in ct.find({'sectionId':sec_difficulty[i][0], 'gameStar':{'$gt':0}}):
				data[i].append(one['logTime_sec'])
			i+=1
		fileName = 'all sections difficulty asc_first record'	
		plotBox(data, p, fileName)
		
		#每個關卡星星
		print('plot box of stars in First Record')
		xlabel = 'stars'
		ylabel = 'log time'
		labels = ['0star','★','★★','★★★','★★★★']
		
		for section in range(1, maxSection+1):
			title = 'section%d.png' %section
			fileName = title
			data2 = []
			for star in range(0, 5):
				data2.append([])
				for two in ct.find({'sectionId':section, 'gameStar':star}):
					data2[star].append(two['logTime_sec'])
			plotBox(data2, p, fileName, title, xlabel, ylabel, labels)
			del data2
			
		database = 'dotCode'
		collection = 'AccuTime'
		
		ct = clientCT(database, collection)
		ct.create_index([('sectionId', 1), ('gameStar', 1)])		
		
		print('plot box of Accumulated Time')
		data = []
		i = 0
		while i < len(sec_difficulty):
			data.append([])
			#print(sec_difficulty[i][0])#關卡
			for one in ct.find({'sectionId':sec_difficulty[i][0], 'gameStar':{'$gt':0}}):
				data[i].append(one['logTime_sec'])
			#print(data)
			#title = "section%d" %section
			i+=1
		fileName = 'all sections difficulty asc_accumulated time'
		plotBox(data, p, fileName)
		
	if value == 8:
		
		###人數分布圖	
		sec_difficulty = Add_Difficulty('Duck')[0]
		sec_difficulty = bubbleSort(sec_difficulty, y = 1)
		#print(sec_difficulty)
		#os.system("pause")

		startTime = time.time()        
		
		database = 'dotCode'
		collection = 'FirstRecord_sta'
		
		#儲存檔案路徑
		p1 = 'D:\\paper\\practice\\practice file\\EDA\\bar'
		#判斷路徑是否存在，不存在就創建
		if not os.path.isdir(p1):
			os.makedirs(p1)	

		p2 = 'D:\\paper\\practice\\practice file\\EDA\\distribution'
		if not os.path.isdir(p2):
			os.makedirs(p2)	
		
		p3 = 'D:\\paper\\practice\\practice file\\EDA\\Standard Deviation'
		if not os.path.isdir(p3):
			os.makedirs(p3)
			
		ct = clientCT(database, collection)
		
		for section in range(1, maxSection+1):
			for star in range(0, 5):
				data = []
				for s in range(0, 300):
					for one in ct.find({'gameCode':'Duck', 'sectionId':section, 'tickTime':1, 'gameStar':star, 'seconds':s}):
						data.append(one['people'])
		
				#人數長條圖
				bins = [i for i in range(0, 300+1, 1)]
				plt.hist(data, bins = bins)
				#plt.show()	#plt.show()會讓圖檔儲存無效
				fileName = 'Bar Plot Of Quantity Of People_section%d_star%d' %(section, star)
				filePath = os.path.join(p1, fileName)
				plt.savefig(filePath)   #儲存圖檔
				plt.close()
		
				#人數分布種類圖
				distribution = 'logistic'
				scipy.stats.probplot(data, dist=distribution, sparams=(2.5,), fit = True, plot = plt)
				#plt.show()	
				fileName = '%s Probability Plot_section%d_star%d' %(distribution, section, star)
				filePath = os.path.join(p2, fileName)
				plt.savefig(filePath)   #儲存圖檔	
				plt.close()
				
				del data
			
		#Standard Deviation Plot
		collection = 'FirstRecord'
		ct = clientCT(database, collection)
		
		ct.create_index([('gameCode', 1), ('difficultyDegree', 1)])
		data = []
		standard_error_list = []
		for degree in range(-3, 3):
			data.append([])
			for one in ct.find({'gameCode':'Duck', 'difficultyDegree':degree, 'gameTime':{'$lte':57600000}}):
				data[degree+3].append(one['gameTime']/1000)
			
			standard_error = calculate_standarderror(data[degree+3])
			standard_error_list.append(standard_error)
		
		plt.scatter([-3, -2, -1, 0, 1, 2], standard_error_list)
		plt.hist(data, [-3, -2, -1, 0, 1, 2])
		fileName = 'Standard Deviation Plot'
		filePath = os.path.join(p3, fileName)
		plt.savefig(filePath)   #儲存圖檔
		plt.close()	

		del data
		
		###各關卡星星比例圖
		#plt.style.use('dark_background')
		col = ['skyblue', 'blue', 'green', 'yellow', 'red', 'maroon', 
			   'seagreen','mediumseagreen', 'mediumvioletred', 'paleturquoise', 
			   'pink', 'salmon', 'olive', 'navy']
		
		labels = ['0star','★','★★','★★★','★★★★'] 
		
		database = 'dotCode'
		collection = 'Sec_sta'
		ct = clientCT(database, collection)
		data = []
		stars = ['zeroStar', 'oneStar', 'twoStar', 'threeStar', 'fourStar']
		total = []
		for i in range(0, len(stars)):
			data.append([])
			for section in range(1, maxSection+1):
				for one in ct.find({"gameCode":"Duck", "sectionId":section}):
					data[i].append(one[stars[i]])
			if i == 0:
				total = np.array(data[i])
			if i > 0:
				total += np.array(data[i])
		
		part = []
		for k in range(0, len(stars)): 
			part.append(np.array(data[k]) / total)
		print(part)
		
		fig, ax = plt.subplots(figsize=(13.66, 7.68))
		
		ax.bar(range(1, maxSection+1), part[0], color=col[0], label = labels[0])
		datax = np.array(part[0])
		for j in range(1, len(part)):
			ax.bar(range(1, maxSection+1), part[j], bottom=datax, color=col[j], label = labels[j])
			datax += np.array(part[j])
			#print(datax)
		
		ax.set_xlabel('section', fontsize=18)
		ax.set_ylabel('proportion', fontsize=18)
		ax.legend(loc='right')
		ax.set_title('Proportion Of Stars', fontsize=18) 
		
		fileName = '各關卡星星比例圖'
		filePath = os.path.join('D:\\paper\\practice\\practice file', fileName)	
		#plt.show()
		plt.savefig(filePath)
		#plt.close()
		
	if value == 9:
		startTime = time.time()
		database = 'dotCode'
		collection = 'AccuTime'
		ct = clientCT(database, collection)	
	
		total = 0
		i = 1
		for second in range(0, 15655251, 100):
			pipe = [{"$match":{"gameCode":'Duck', 
							   "accumulatedTime_sec":{'$gte':second, '$lt':second+100}, 
							   "gameStar":{'$gt':0}
							  }
					},
					{"$project":{"_id":0}},
					{"$group":{"_id":None,
							   "count":{"$sum":1}
							  }
					}
				   ]
			result = ct.aggregate(pipe)
			
			for people in result:
				people = dict(people)
				total += people['count']
				print("%d %d %d %.4f%s" %(i, second, second+100, total/3300644*100, "%"))
				i += 1
				#os.system("pause")	
		#print(total)		
				
	endTime = time.time()
	passTime = (endTime - startTime)
	print('執行時間', passTime, '秒')