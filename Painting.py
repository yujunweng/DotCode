'''
Created on 2019年10月6日
20191006 增加畫圖
20191207 增加畫折線圖
20200329 完成難度、學生程度與累積時間關係的散布圖
20200908 plotMultiScatter加1個參數，控制要畫幾個子圖，可以傳一個多子陣列的X,Y，但不用全畫
@author: Y.J.Weng
'''
import matplotlib.pyplot as plt
import os 
import gc
import csv
import time
import numpy as np
import PaperPainting as pp
import PaperCommon	as pc
import scipy


if __name__ == '__main__': 
	database = 'dotCode'
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	sectionId, itemDifficulty, difficultyDegree = pc.add_difficulty(game, '1')
	sectionsDegrees = pc.sections_degrees()
	playersDegrees =  pc.players_degrees()
	clusters = [5, 3, 4, 4, 6, 4, 5, 3, 3, 3,
				 3, 4, 4, 4, 4, 3, 4, 4, 5, 5,
				 3, 4, 5, 6, 3, 5, 5, 4, 4, 5,
				 4, 5, 4, 4, 4, 6, 3, 4, 6, 4,
				 4, 5, 6, 5, 7, 7, 7, 6, 3, 5,
				 4, 4, 4, 5, 5, 4, 5, 4, 5, 4		 
				]
	
	starLegends = ['0star', '★', '★★', '★★★', '★★★★']			
				
	timeLimit = 3600
	
	minLogTime = pc.get_min_value('FirstRecordLog_sta', 'seconds_log')
	maxLogTime = pc.get_max_value('FirstRecordLog_sta', 'seconds_log')

	minZ = pc.get_min_value('FirstRecordZ_sta', 'seconds_z')
	maxZ = pc.get_max_value('FirstRecordZ_sta', 'seconds_z')
	
	intervalLogTime = 0.1
	intervalZ = 0.01	
	
	eloChoice = 1#input("請選擇elo分級欄位\n(1)elo1:0.01\n(2)elo2:0.01-0.002n\n(3)elo3：0.02\n：")
	sections, itemDifficulty, difficulty_degree = pc.add_difficulty(game, eloChoice)
	if eloChoice == '2':
		eloDifficulty = 'difficulty2' 
		degreeKey = 'difficultyDegree2'
	elif eloChoice == '3':
		eloDifficulty = 'difficulty3' 
		degreeKey = 'difficultyDegree3'
	else:
		eloDifficulty = 'difficulty'
		degreeKey = 'difficultyDegree_kmeans'
	
	practiceFilePath = r'D:\paper\practice\practice file'
	scatterPath = os.path.join(practiceFilePath, 'scatter')
	
	while 1:
		value = int(input('''(1)scatter figure, per data per point 
(2)scatter figure, per data per point with color 
(4)Relation between time taken(every y seconds) and average correct percentage(AccuTime_sta)
(5)Relation between time taken(per second) and average correct percentage(FirstRecord_sta)
(7)Section and User's Elo
(8)時間的盒鬚圖\n:'''))
		startTime = pc.to_vids_time(time.time())

		if value == 1:
			''' 
			relation between correctness and time
			重疊散佈點圖，每筆資料1個點, 每種星星一個圖
			'''			
			collection = pc.choose_collection(database)
			filePath = os.path.join(scatterPath, collection)
			
			figureLegends = pc.stars_legends()
			ylabel = 'Correct Percentage'			
			
			if collection == 'FirstRecord':
				label = 'Time'
				collectionTitle = 'Time Of The FirstRecord,'
				keys = ['gameTime_sec', 'logGameTime_sec', 'gameStar']
			elif collection == 'AccuTime':
				label = 'Accumulated Time'
				collectionTitle = 'Accumulated Time, limit:%d seconds,' %timeLimit
				keys = ['accuTime_sec', 'logAccuTime_sec', 'correctPercentage']	
			else:
				print("目前只有AccuTime和FirstRecord")
				os._exit(0)
			for section in range(1, maxSection+1):
				file = 'section%d.png' %section
				timeTaken = pc.create_lists(0, 5, x=[])
				logtimeTaken = pc.create_lists(0, 5, x=[])
				avgCorrectness = pc.create_lists(0, 5, x=[])
				for star in range(0,5):
					if collection == 'FirstRecord':
						query = {'sectionId':section, 'gameStar':star}
					elif collection == 'AccuTime':
						query = {'sectionId':section, 'accuTime_sec':{'$lt':timeLimit}, 
								'tryCount':{'$lt':300}, 'gameStar':star}
					timeTaken[star], logtimeTaken[star], avgCorrectness[star] = pc.collect_data(collection, query, keys)
					if collection == 'FirstRecord':
						avgCorrectness[star] = [1 if int(i) > 0 else 0 for i in avgCorrectness[star]]
					
				title = collectionTitle + file
				## plot time
				xlabel = label
				savePath = os.path.join(filePath, 'time')
				plot_multi_scatter(timeTaken, avgCorrectness, title, xlabel, ylabel, savePath, file, legendIllustration=figureLegends)
				
				## Plot log time
				xlabel = 'Log' + label
				savePath = os.path.join(filePath, 'logtime')
				plot_multi_scatter(logtimeTaken, avgCorrectness, title, xlabel, ylabel, savePath, file, legendIllustration=figureLegends)


		elif value == 2:
			'''relation between correct percentage, time and elo
			散佈點圖，每筆資料1個點, 有顏色
			'''
			colors = ['w', 'b', 'g', 'y', 'r']
			figureLegends = pc.stars_legends()
			ylabel = 'Average Correct Percentage'
			title = 'Relation between game time and item difficulty on the first record'

			label = 'Accumulated Time'
			collectionTitle = 'Accumulated Time, limit:%d seconds,' %timeLimit				
			keys = ['accuTime_sec', 'logAccuTime_sec', 'correctPercentage', 'elo_001']			
			
			for section in range(1, maxSection+1):
				file = 'section%d.png' %section
				timeTaken, logtimeTaken, correctness, stuElo = [], [], [], []
				query = {'sectionId':section, 'accuTime_sec':{'$lt':timeLimit}}
				timeTaken, logtimeTaken, correctness, stuElo = pc.collect_data('AccuTime', query, keys)
	
				title = collectionTitle + file
				fileName = 'PlayersElo'
				## plot time
				xlabel = label
				savePath = os.path.join(scatterPath, 'time')
				plot_single_scatter(timeTaken, correctness, 10, stuElo, title, xlabel, ylabel, savePath, fileName, xLimit=timeLimit)

				## plot log time
				xlabel = 'Log' + label
				savePath = os.path.join(scatterPath, 'logtime')
				plot_single_scatter(logtimeTaken, correctness, 10, stuElo, title, xlabel, ylabel, savePath, fileName, xLimit=logTimeLimit)

		###統計
		elif value == 4:
			'''relation between accumulated time taken(second) and average correct percentage'''
			# 4-1 AccuTime_sta
			ct = pc.clientCT(database, 'AccuTime_sta')
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('eloDegree', 1)])
			ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('eloDegree', 1)])

			timelimit = 55000
			size = 0.55
			multiple = 3
			y = 10
				  
			## 依關卡
			for section in range(1, maxSection+1):
				timeTaken_all = pc.create_lists(0, 7, x=[])
				avgTryCount_all = pc.create_lists(0, 7, x=[])
				avgCorrect_all = pc.create_lists(0, 7, x=[])
				countness_all = pc.create_lists(0, 7, x=[])
				difficulty_all = pc.create_lists(0, 7, x=[])
				star_all = pc.create_lists(0, 7, x=[])
				for i in range(0, 7):	# 星星數 5是全部 6是有過關
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
				title = 'Relation Between Accumulated Time And Average Try Times \n Section:%d Difficulty:%f' %(section, itemDifficulty[section-1])
				# 檔名
				fileName = 'section%d.png' %section
				path = r'D:\paper\practice\practice file\Scatter\Statistic\Accumulated Time\%s\section' %timelimit
				
				# 合併星星
				plot_single_scatter(timeTaken_all[5], avgTryCount_all[5], countness_all[5], 'skyblue', title, xlabel, ylabel, xlimit=timelimit, ylimit=1, filePath=os.path.join(path, 'mixstar'), filename=fileName)
				# 分開星星
				plotMultiScatter(timeTaken_all, avgTryCount_all, 5, countness_all, title, xlabel, ylabel, inPath=os.path.join(path, 'allstar'), filename=fileName)
				# 有過關和沒過關section
				plotMultiScatter(timeTaken_all, avgTryCount_all, 2, countness_all, title, xlabel, ylabel, inPath=os.path.join(path, '過關和沒過關') , filename=fileName)
				
				del timeTaken_all, avgTryCount_all, avgCorrect_all, countness_all, difficulty_all
				
			## 依難度等級	
			dtimeTaken_all = pc.create_lists(0, len(degree), x=[])
			davgCorrect_all = pc.create_lists(0, len(degree), x=[])
			davgTryCount_all = pc.create_lists(0, len(degree), x=[])
			dcountness_all = pc.create_lists(0, len(degree), x=[])
			for i in range(0, len(degree)):
				dtimeTaken = pc.create_lists(0, 7, x=[])
				davgCorrect = pc.create_lists(0, 7, x=[])
				davgTryCount = pc.create_lists(0, 7, x=[])
				dcountness = pc.create_lists(0, 7, x=[])	
				for j in range(0,7):
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
				path = r'D:\paper\practice\practice file\Scatter\Statistic\Accumulated Time\%s\difficulty' %timelimit
				title = 'Relation Between Different Stars on the Difficulty%s' %degree[i]
				fileName = '(%s)stars_difficulty%s.png' %(j, degree[i])
				plotMultiScatter(dtimeTaken, davgTryCount, 5, dcountness, title, xlabel, ylabel, inPath=path, filename=fileName)
				
				# 同一難度有過關和沒過關的比較
				title = 'Relation Between Pass And Loss On the Difficulty%s' %degree[i]
				fileName = '%s.pass & loss_difficulty%s.png' %(i+1, degree[i])
				plotMultiScatter(dtimeTaken, davgTryCount, 2, dcountness, title, xlabel, ylabel, inPath=p, filename=fileName)
				
				del dtimeTaken, davgCorrect, davgTryCount, dcountness
			
			# 不分星星
			p = r'D:\paper\practice\practice file\Scatter\Statistic\Accumulated Time\%s\difficulty' %timelimit
			fileName = '不分星平均.png'
			title = 'Relation Between Different Difficulty'
			plotMultiScatter(dtimeTaken_all, davgTryCount_all, 6, dcountness_all, title, xlabel, ylabel, inPath=p, filename=fileName)
				
			del dtimeTaken_all, davgCorrect_all, davgTryCount_all, dcountness_all
			
			## 依時間
			timeTaken, avgCorrect, avgTryCount, difficulty, countness = [], [], [], [], []
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
			p = r'D:\paper\practice\practice file\Scatter\Statistic\Accumulated Time\%s' %timelimit
			fileName = 'Average Difficulty On Second'
			if one['gameStar'] == 6:
				title = 'Relation Between Accumulated Time And Average Try Times(Pass)'
				fileName = 'Average Difficulty On Second(Pass)'
			colorbar_label = 'Difficulty'

			plotScatter(timeTaken, avgTryCount, difficulty, countness, title, xlabel, ylabel, cbar_label=colorbar_label, xlimit=100, ylimit=1, filePath=p, filename=fileName)
			
			#for i, j, k in zip(timeTaken, difficulty, avgCorrect):
				#print("timeTaken:", i, "difficulty:", j, "avgCorrect:", k)
			
			# 4-2 AccuTimeLog_sta
			ct = pc.clientCT(database, 'AccuTimeLog_sta')
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
				timeTaken_all = pc.create_lists(0, 7, x=[])
				avgTryCount_all = pc.create_lists(0, 7, x=[])
				avgCorrect_all = pc.create_lists(0, 7, x=[])
				countness_all = pc.create_lists(0, 7, x=[])
				difficulty_all = pc.create_lists(0, 7, x=[])
				star_all = pc.create_lists(0, 7, x=[])
				for i in range(0, 7):	# 星星數 5是全部 6是有過關
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
				title = 'Relation Between Log Accumulated Time Taken And Average Try Times \n Section:%d Difficulty:%f' %(section, itemDifficulty[section-1])
				# 檔名
				fileName = 'section%d.png' %section
				p = r'D:\paper\practice\practice file\Scatter\Statistic\Log Accumulated Time\%s\section' %timelimit
				
				# 合併星星
				plotSingleScatter(timeTaken_all[5], avgTryCount_all[5], countness_all[5], 'skyblue', title, xLabel, yLabel, xlimit=timelimit, ylimit=1, filePath=p, filename=fileName)
				
				del timeTaken_all, avgTryCount_all, countness_all, difficulty_all, star_all
				
			## 依難度等級	
			dtimeTaken_all = pc.create_lists(0, len(sectionsDegrees), x=[])
			davgCorrect_all = pc.create_lists(0, len(sectionsDegrees), x=[])
			davgTryCount_all = pc.create_lists(0, len(sectionsDegrees), x=[])
			dcountness_all = pc.create_lists(0, len(sectionsDegrees), x=[])
			for i in range(0, len(sectionsDegrees)):
				dtimeTaken = pc.create_lists(0, 7, x=[])
				davgCorrect = pc.create_lists(0, 7, x=[])
				davgTryCount = pc.create_lists(0, 7, x=[])
				dcountness = pc.create_lists(0, 7, x=[])
				for j in range(0,7):
					for second in np.arange(-2.5, timelimit, 0.1):	
						second = round(second, 2)
						#print("degree:", degree[i])
						for one in ct.find({'sectionId':0, 'tickTime':0.1, 'gameStar':j, 'seconds_log':second, 'difficultyDegree':degree[i]}):
							#print(one)
							dtimeTaken[j].append(one['seconds_log'])
							davgCorrect[j].append(one['avgCorrectness'])
							davgTryCount[j].append(one['avgTryCount'])
							dcountness[j].append(one['people']**size*multiple)
							if j == 5 :
								dtimeTaken_all[i].append(one['seconds_log'])
								davgCorrect_all[i].append(one['avgCorrectness'])
								davgTryCount_all[i].append(one['avgTryCount'])
								dcountness_all[i].append(one['people']**size*multiple)	

				# 設定X, Y軸標籤(要在pltscatter前面設定好)
				xlabel = 'Log Accumulated Time Taken'
				ylabel = 'Average Try Times'

				p = os.path.join(scatterPath, r'logtime\%s\difficulty') %timelimit
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
			timeTaken, avgCorrect, avgTryCount, difficulty, countness = [], [], [], [], []
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
			p = r'D:\paper\practice\practice file\Scatter\Statistic\Log Accumulated Time\%s' %timelimit
			
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

			### 4-3 AccuTime_sta
			collection = 'AccuTime_sta'
			ct = pc.clientCT(database, collection)
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
			ct.create_index([('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
					
			timelimit = 10
			size = 0.55
			multiple = 3
			y = 0.1
			
			print('plot relation between accumulated time taken(second) and average correct percentage')        
				
			##依時間
			timeTaken = pc.create_lists(0, 5, x=[])
			avgCorrect = pc.create_lists(0, 5, x=[])
			avgTryCount = pc.create_lists(0, 5, x=[])
			difficulty = pc.create_lists(0, 5, x=[])
			countness = pc.create_lists(0, 5, x=[])
			for star in range(0, 5): 
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
			p = r'D:\paper\practice\practice file\Scatter\Statistic\Standardized Accumulated Time\%s' %timelimit
			
			ylabel = 'Average Try Times'
			title = 'Relation Between Standardized Accumulated Time And Average Try Times'
			fileName = 'Average Try Times On Standardized Accumulated Time_tickTime'
			
			plotMultiScatter(timeTaken, avgTryCount, 5, countness, title, xlabel, ylabel, inPath=p, filename=fileName)
				
			del timeTaken, avgCorrect, avgTryCount, difficulty, countness


		### FirstRecord_sta
		elif value == 5:
			'''
			5-1 relation between time taken(second) and average correct percentage on FirstRecord_sta
			5-2 relation between log time taken and average correct percentage on FirstRecordLog_sta
			'''
			pointSize = 0.55
			pointMultiply = 3

			###5-1 time
			ct = pc.clientCT(database, 'FirstRecord_sta')
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('difficultyDegree', 1)])
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('difficultyDegree2', 1)])
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds', 1), ('difficultyDegree3', 1)])			
			
			timelimit = 250
			ticktime = 1			
			savePath = os.path.join(scatterPath, r'statistic\gametime\%s\%s' %(ticktime, timelimit))			
						
			'''
			##5-1-1 依關卡
			for section in range(1, maxSection+1):
				timeTaken = pc.create_lists(0, 6, x=[])
				avgCorrect = pc.create_lists(0, 6, x=[])
				people = pc.create_lists(0, 6, x=[])
				
				for star in range(0, 6):	# 星星數
					for second in range(0, timelimit):
						for one in ct.find({'gameCode':game, 'sectionId':section, 'tickTime':ticktime, 'gameStar':star, 'seconds':second}):
							timeTaken[star].append(one['seconds'])
							avgCorrect[star].append(one['avgCorrectness'])
							people[star].append(one['people']**pointSize*pointMultiply)
							
				# 設定X, Y軸標籤(要在pltscatter前面設定好)
				xlabel = 'Time Taken(Second)'
				ylabel = 'Average FPEP'
				title = 'Relation Between Time and Average FPEP\n Section:%d' %section
				
				# 合併星星圖
				fileName = 'section%d.png' %section
				pp.plot_single_scatter(timeTaken[5], avgCorrect[5], people[5], title, xlabel, ylabel, savePath, fileName, xLimit=timelimit)
				
				del timeTaken, avgCorrect, people
			
			##5-1-2 依難度等級	
			# 全部星星合併, 不用畫星星分開, 得分都是1, 沒有漸進效果
			timeTaken = pc.create_lists(0, len(sectionsDegrees), x=[])
			avgCorrect = pc.create_lists(0, len(sectionsDegrees), x=[])
			people = pc.create_lists(0, len(sectionsDegrees), x=[])
			for degree in range(0, len(sectionsDegrees)):
				for second in range(0, timelimit):
					query = {'gameCode':game, 'sectionId':0, 'tickTime':ticktime, 'gameStar':5, 'seconds':second, degreeKey:degree}
					for one in ct.find(query):	
						#print(one)
						timeTaken[degree].append(one['seconds'])
						avgCorrect[degree].append(one['avgCorrectness'])
						people[degree].append(one['people']**pointSize*pointMultiply)

			# 設定X, Y軸標籤(要在pltscatter前面設定好)        
			xlabel = 'Time Taken(Second)'
			ylabel = 'Average FPEP'
			title = 'Relation Between Time and Average FPEP'
			legendIllustration = pc.sections_degrees()
			fileName = 'all %s degrees' %eloDifficulty
			pp.plot_multi_scatter(timeTaken, avgCorrect, people, title, xlabel, ylabel, savePath, fileName, legendIllustration)
			
			del timeTaken, avgCorrect, people
			
			##5-1-3 依時間
			timeTaken, avgCorrect, difficulty, people = [], [], [], []
			for second in range(0, timelimit):
				query = {'gameCode':game, 'sectionId':0, 'tickTime':ticktime, 'gameStar':5, 'seconds':second, degreeKey:'n'}
				for one in ct.find(query):
					timeTaken.append(one['seconds'])
					avgCorrect.append(one['avgCorrectness'])
					difficulty.append(one[eloDifficulty])
					people.append(one['people']**pointSize*pointMultiply)
				
			# 設定各項標籤       
			xlabel = 'Time Taken'
			ylabel = 'Average FPEP'
			title = 'Relation Between Time and Average FPEP'
			colorbar_label = 'Difficulty'

			timeSavePath = os.path.join(savePath, 'time')
			fileName = 'average difficulty'
			pp.plot_scatter(timeTaken, avgCorrect, difficulty, people, title, xlabel, ylabel, savePath, fileName, cbar_label=colorbar_label, xLimit=timelimit)
			
			del timeTaken, avgCorrect, difficulty, people
			
			#for i, j, k in zip(timeTaken, difficulty, avgCorrect):
				#print("timeTaken:", i, "difficulty:", j, "avgCorrect:", k)
			

			###5-2 log time
			ct = pc.clientCT(database, 'FirstRecordLog_sta')
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_log', 1), ('difficultyDegree', 1)])
			ct.create_index([('gameCode', 1), ('sectionId', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_log', 1), ('difficultyDegree2', 1)])
			
			savePath = r'D:\paper\practice\practice file\scatter\statistic\logtime\%s' %timelimit

			##5-2-1依關卡
			for section in range(1, maxSection+1):
				#if(section >= 50):
					#pointSize = 1
					#pointMultiply = 1
				timeTaken, avgCorrect, people = [], [], []
				for second in np.arange(minLogTime, maxLogTime+intervalLogTime, intervalLogTime):
					second = round(second, 2)
					query = {'gameCode':game, 'sectionId':section, 'tickTime':intervalLogTime, 'gameStar':5, 'seconds_log':second}
					for one in ct.find(query):
						timeTaken.append(one['seconds_log'])
						avgCorrect.append(one['avgCorrectness'])
						people.append(one['people']**pointSize*pointMultiply)
				
				# 設定X, Y軸標籤(要在pltscatter前面設定好)        
				xLabel = 'Time Taken(Ln second)'
				yLabel = 'Average FPEP'
				title = 'Relation Between Ln Time and Average FPEP\n Section:%d' %section
				legendIllustration = pc.sections_degrees()
				
				fileName = 'section%d.png' %section
				pp.plot_single_scatter(timeTaken, avgCorrect, people, title, xLabel, yLabel, savePath, fileName)
				
				del timeTaken, avgCorrect, people
			
			## 5-2-2依難度等級
			timeTaken = pc.create_lists(0, len(sectionsDegrees), x=[])
			avgCorrect = pc.create_lists(0, len(sectionsDegrees), x=[])
			people = pc.create_lists(0, len(sectionsDegrees), x=[])
			for degree in range(0, len(sectionsDegrees)):	
				for second in np.arange(minLogTime, maxLogTime+intervalLogTime, intervalLogTime):
					second = round(second, 2)
					query = {'gameCode':game, 'sectionId':0, 'tickTime':intervalLogTime, 'seconds_log':second, 'gameStar':5, degreeKey:degree}
					for one in ct.find(query):
						timeTaken[degree].append(one['seconds_log'])
						avgCorrect[degree].append(one['avgCorrectness'])
						people[degree].append(one['people']**pointSize*pointMultiply)

			#設定X, Y軸標籤(要在pltscatter前面設定好)        
			xlabel = 'Time Taken(Ln second)'
			ylabel = 'Average FPEP'
			title = 'Relation Between Ln Time and Average FPEP among Different Different difficulties'
			legendIllustration = pc.sections_degrees()
			
			fileName = 'all %s degrees.png' %eloDifficulty
			pp.plot_multi_scatter(timeTaken, avgCorrect, people, title, xlabel, ylabel, savePath, fileName, legendIllustration)
			
			del timeTaken, avgCorrect, people
			
			## 5-2-3依時間
			timeTaken, avgCorrect, difficulty, people = [], [], [], []
			for second in np.arange(minLogTime, maxLogTime+intervalLogTime, intervalLogTime):
				second = round(second, 2)
				query = {'sectionId':0, 'tickTime':intervalLogTime, 'gameStar':5, 'seconds_log':second, degreeKey:'n'}
				for one in ct.find(query):
					timeTaken.append(one['seconds_log'])
					avgCorrect.append(one['avgCorrectness'])
					difficulty.append(one[eloDifficulty])
					people.append(one['people']**pointSize*pointMultiply)

			#設定各項標籤       
			xlabel = 'Time Taken(Ln second)'
			ylabel = 'Average FPEP'
			title = 'Relation Between Ln Time and Average FPEP'
			colorbar_label = 'Difficulty'
			
			fileName = 'average difficulty on Ln second'
			pp.plot_scatter(timeTaken, avgCorrect, difficulty, people, title, xlabel, ylabel, savePath, fileName, cbar_label=colorbar_label, xLimit=20)
			del timeTaken, avgCorrect, people, difficulty
			
			'''
			###5-3 Z time
			## 5-3-1 依玩家等級
			ct = pc.clientCT(database, 'FirstRecordZ_sta')
			ct.create_index([('gameCode', 1), ('playerDegree', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
			ct.create_index([('gameCode', 1), ('playerDegree_kmeans', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
			
			savePath = os.path.join(scatterPath, r'statistic\ztime\%s' %int(maxZ))
			
			timeTaken = pc.create_lists(0, len(playersDegrees), x=[]) 
			avgCorrect = pc.create_lists(0, len(playersDegrees), x=[])
			avgStars = pc.create_lists(0, len(playersDegrees), x=[])
			people = pc.create_lists(0, len(playersDegrees), x=[])			
			for degree in range(0, len(playersDegrees)):
				for second in np.arange(minZ, 3, intervalZ):
					second = round(second, 2)
					query = {'gameCode':game, 'playerDegree_kmeans':degree ,'tickTime':intervalZ, 'gameStar':5, 'seconds_z':second}
					for one in ct.find(query):
						timeTaken[degree].append(one['seconds_z'])
						avgCorrect[degree].append(one['avgCorrectness'])
						avgStars[degree].append(one['avgStar']) 
						people[degree].append(one['people']**pointSize*pointMultiply)
					#	people[degree].append(20)	
			
			# 設定X, Y軸標籤(要在pltscatter前面設定好)
			xlabel = 'Z of Time Taken'
			ylabel = 'Average FPEP'
			title = 'Realation Between Z-value of Time and Average FPEP among Different Player Degrees'
			fileName = 'player degree FPEP.png'
			legendIllustration = pc.players_degrees()
			pp.plot_multi_scatter(timeTaken, avgCorrect, people, title, xlabel, ylabel, savePath, fileName, legendIllustration)

			## 5-3-2 依難度等級
			ct = pc.clientCT(database, 'FirstRecordZ_sta')
			ct.create_index([('gameCode', 1), ('difficultyDegree_kmeans', 1), ('tickTime', 1), ('gameStar', 1), ('seconds_z', 1)])
			
			savePath = os.path.join(scatterPath, r'statistic\ztime\%s' %int(maxZ))
			xlabel = 'Z of Time Taken'
			ylabel = 'Average FPEP'
			title = 'Realation Between Z-value of Time and Average FPEP among Different Different difficulties'
			
			timeTaken = pc.create_lists(0, len(sectionsDegrees), x=[]) 
			avgCorrect = pc.create_lists(0, len(sectionsDegrees), x=[])
			avgStars = pc.create_lists(0, len(sectionsDegrees), x=[])
			people = pc.create_lists(0, len(sectionsDegrees), x=[])			
			for degree in range(0, len(sectionsDegrees)):
				for second in np.arange(minZ, 3, intervalZ):
					second = round(second, 2)
					for one in ct.find({'gameCode':game, 'difficultyDegree_kmeans':degree ,'tickTime':intervalZ, 'gameStar':5, 'seconds_z':second}):
						timeTaken[degree].append(one['seconds_z'])
						avgCorrect[degree].append(one['avgCorrectness'])
						avgStars[degree].append(one['avgStar']) 
						people[degree].append(one['people']**pointSize*pointMultiply)
					#	people[degree].append(20)	
				fileName = 'difficulty degree%s_correctness.png' %degree
				color = pc.color_degrees()
				pp.plot_single_scatter(timeTaken[degree], avgCorrect[degree], people[degree], title, xlabel, ylabel, savePath, fileName, color[degree], xLimit=100, yLimit=1)
			
			# 設定X, Y軸標籤(要在pltscatter前面設定好)
			xlabel = 'Z of Time Taken'
			ylabel = 'Average FPEP'
			title = 'Realation Between Z-value of Time and Average FPEP among Different Difficulty Degrees'
			fileName = 'difficulty degree FPEP.png'
			legendIllustration = pc.sections_degrees()
			pp.plot_multi_scatter(timeTaken, avgCorrect, people, title, xlabel, ylabel, savePath, fileName, legendIllustration)

			ylabel = 'Average Stars'
			title = 'Realation Between Z-value of Time and Average stars among Different Difficulty Degrees'
			fileName = 'difficulty degree stars.png'
			pp.plot_multi_scatter(timeTaken, avgStars, people, title, xlabel, ylabel, savePath, fileName, legendIllustration)
					

		elif value == 6:
			# 雙Y軸折線圖
			message = '請依序選擇X軸, 左Y軸, 右Y軸資料 右Y軸資料2,'
			keys = pc.list_columns('dotCode', 'Sec_sta', message)
			xlabel, ylabel1, ylabel2, ylabel3 = keys
			xaxis, yaxisP1, yaxisP2, yaxisP3 = pc.collect_data('Sec_sta', {}, keys, database='dotCode')
			seq = pc.sort_seq(yaxisP1)
			xaxis = pc.follow_sort(xaxis, seq)
			yaxisP1 = pc.follow_sort(yaxisP1, seq)
			yaxisP2 = pc.follow_sort(yaxisP2, seq)
			yaxisP3 = pc.follow_sort(yaxisP3, seq)
			xaxis = pc.int_to_str(xaxis)
			yaxis = [yaxisP1, yaxisP2, yaxisP3]
			ylabels = [ylabel1, ylabel2, ylabel3] 
			pp.plot_multi_yaxis(xaxis, yaxis, xlabel, ylabels)


		elif value == 7:
			'''讀取CSV檔畫Elo'''
			choice = int(input('(1)section elo\n(2)student elo\n:'))
			if choice == 1:
				k = '001'
				readPath = r'D:\paper\practice\practice file\EloRating\Duck\%s' %k
				savePath = os.path.join(readPath, 'section')
				#filePath = r'D:\paper\practice\practice file\EloRating\Duck\to_compare'
				files = pc.qualify_files(readPath, 'csv')
				sectionsElo = []
				for file in files:
					print(file)
					if file.find('DuckElo') > -1:
						stage = file.split('_')[1].split('.')[0]
						title = "The Variation of Elo Points"
						fileName = stage+'.png'
						sectionElo = pc.read_csv(readPath, file, 'sectionElo')
						sectionElo = [float(num) for num in sectionElo]
						pp.plot_line(sectionElo, title, savePath, fileName)
						#sectionsElo.append(sectionElo)
							
				variables = {"title":'compare different K',
							 "kvalue":'different K',
							 "category":'section'
							}
				fileName = 'CompareDifferentK.jpg'		
				#pp.plot_multi_subplots(sectionsElo, 'line', filePath, fileName, subs=(3,2), **variables)
			
			if choice == 2:
				'''畫玩家的Elo'''
				ct = pc.clientCT(database, 'FirstPass')
				ct.create_index([('userId', 1), ('sectionId', 1)])
				eloColumn = 'elo_001'
				k = eloColumn.split('_')[1]
				filePath = r'D:\paper\practice\practice file\EloRating\Duck\%s' %k
				for id in range(1, 2000):
					title = 'user%d' %id
					eloHist = []
					for section in range(1, maxSection+1):
						for one in ct.find({'userId':id, 'sectionId':section}):
							eloHist.append(one[eloColumn])
					eloHist = np.array(eloHist)		
					if len(eloHist) > 0:
						pp.plot_line(eloHist, title, filePath, title)
						print("user：{}".format(id))


		if value == 8:
			choice = int(input("(1)people distribution\n(2)theta distribution\n:"))
			if choice == 1:
				'''人數分布圖'''
				ct = pc.clientCT('dotCode', 'FirstRecord_sta')
				
				p1 = r'D:\paper\practice\practice file\EDA\bar'
				pc.create_path(p1)
				
				p2 = r'D:\paper\practice\practice file\EDA\distribution'
				pc.create_path(p2)
	
				for section in range(1, maxSection+1):
					for star in range(0, 5):
						peo = []
						for s in range(0, 300):
							for one in ct.find({'gameCode':'Duck', 'sectionId':section, 'tickTime':1, 'gameStar':star, 'seconds':s}):
								peo.append(one['people'])

						#fileName = 'Bar Plot Of Quantity Of People_section%d_star%d' %(section, star)						
						#plot_hist(peo, p1, fileName)
						#人數統計分布
						fileName = '%s Probability Plot_section%d_star%d' %('logistic', section, star)
						pp.plot_distribution(peo, 'logistic', p2, fileName)
						del peo
						
			elif choice == 2:
				'''時間的盒鬚圖'''
				# FirstRecord
				ct = pc.clientCT(database, 'FirstRecord')
				ct.create_index([('sectionId', 1), ('gameStar', 1)])
				filePath = r'D:\paper\practice\practice file\box\FirstRecord'
				pc.create_path(filePath)				
				print('plot box of time on FirstRecord')
				
				np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
				sec_difficulty, difficulty_degree = pc.add_difficulty('Duck', 2)
				sec_difficulty = pc.bubbleSort_twoLayer(sec_difficulty, y=1)

				data = []
				i = 0
				while i < len(sec_difficulty):
					data.append([])
					#print(sec_difficulty[i][0])#關卡
					for one in ct.find({'sectionId':sec_difficulty[i][0], 'gameStar':{'$gt':0}}):
						data[i].append(one['logTime_sec'])
					i+=1
				fileName = 'Sections Difficulty of FirstRecord'	
				plotBox(data, filePath, fileName)
				
				#每個關卡星星
				print('plot box of stars on FirstRecord')
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
					
					# AccuTime
					ct = pc.clientCT(database, 'AccuTime')
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
			
			
			elif choice == 4:		
				'''
				#Standard Deviation Plot
				ct = pc.clientCT(database, 'FirstRecord')
				ct.create_index([('gameCode', 1), ('difficultyDegree', 1)])
				p3 = 'D:\\paper\\practice\\practice file\\EDA\\Standard Deviation'
				pc.create_path(p3)				
				data = []
				standard_error_list = []
				for degree in range(-2, 3):
					data.append([])
					for one in ct.find({'gameCode':'Duck', 'difficultyDegree':degree, 'gameTime':{'$lte':57600000}}):
						data[degree+2].append(one['gameTime']/1000)
					
					standard_error = np.std(data[degree+2], ddof=1)
					standard_error_list.append(standard_error)
				
				plt.scatter(degrees, standard_error_list)
				plt.hist(data, degrees)
				fileName = 'Standard Deviation Plot'
				filePath = os.path.join(p3, fileName)
				plt.savefig(filePath)
				plt.show()
				plt.close()	
				del data
				'''
				#各關卡星星比例, 百分比累計圖
				ct = pc.clientCT(database, 'Sec_sta')
				#plt.style.use('dark_background')
				col = ['skyblue', 'blue', 'green', 'yellow', 'red', 'maroon', 'seagreen','mediumseagreen'
					   , 'mediumvioletred', 'paleturquoise', 'pink', 'salmon', 'olive', 'navy']
				labels = ['0star','★','★★','★★★','★★★★'] 
			
				data = []
				stars = ['zeroStarPercentage', 'oneStarPercentage', 'twoStarPercentage', 'threeStarPercentage', 'fourStarPercentage']
				total = []
				for i in range(0, len(stars)):
					data.append([])
					for section in range(1, maxSection+1):
						for one in ct.find({"gameCode":"Duck", "sectionId":section}):
							data[i].append(one[stars[i]])
					total = np.array(data[i]) if i == 0 else total+np.array(data[i])
						
				part = []
				for k in range(0, len(stars)): 
					part.append(np.array(data[k]) / total * 100)
				print(part)
				
				fig, ax = plt.subplots(figsize=(13.66, 7.68))
				
				ax.bar(range(1, maxSection+1), part[0], color=col[0], label = labels[0])
				datax = np.array(part[0])
				for j in range(1, len(part)):
					ax.bar(range(1, maxSection+1), part[j], bottom=datax, color=col[j], label = labels[j])
					datax += np.array(part[j])
					#print(datax)
				
				ax.set_title('Ratio of Stars Players Obtained', fontsize=18) 
				ax.set_xlabel('stage', fontsize=18)
				ax.set_ylabel('Cumulated Ratio %', fontsize=18)
				ax.legend(loc='right')
				
				my_y_ticks = np.arange(0, 1*100+1, (1/10)*100)
				plt.yticks(my_y_ticks)
				
				fileName = '各關卡星星比例圖'
				filePath = os.path.join(r'D:\paper\practice\practice file', fileName)	
				#plt.show()
				plt.savefig(filePath)
				#plt.close()
			
		if value == 9:
			ct = pc.clientCT(database, 'AccuTime')	
		
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
	print("\n")				
	pc.pass_time(startTime, time.time())
