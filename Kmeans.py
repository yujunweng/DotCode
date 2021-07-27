from sklearn import cluster, datasets, preprocessing, metrics
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from scipy.spatial.distance import cdist 
import scipy
from scipy.spatial.distance import euclidean
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import traceback
import os
import gc
import time
import PaperCommon as pc

 
dst = euclidean
 
k_means_args_dict = {
	'n_clusters': 0,
	# drastically saves convergence time
	'init': 'k-means++',
	'max_iter': 100,
	'n_init': 1,
	'verbose': False,
	# 'n_jobs':8
}
 
 
def gap(data, refs=None, nrefs=20, ks=range(1, 11)):
	"""
	I: NumPy array, reference matrix, number of reference boxes, number of clusters to test
	O: Gaps NumPy array, Ks input list
	
	Give the list of k-values for which you want to compute the statistic in ks. By Gap Statistic
	from Tibshirani, Walther.
	"""
	print("gap method")
	shape = data.shape
 
	if not refs:
		tops = data.max(axis=0)
		bottoms = data.min(axis=0)
		dists = scipy.matrix(np.diag(tops - bottoms))
		rands = scipy.random.random_sample(size=(shape[0], shape[1], nrefs))
		for i in range(nrefs):
			rands[:, :, i] = rands[:, :, i] * dists + bottoms
	else:
		rands = refs
	
	gaps = np.zeros((len(ks),))
	
	for (i, k) in enumerate(ks):
		print("k={}".format(k))
		k_means_args_dict['n_clusters'] = k
		kmeans = KMeans(**k_means_args_dict)
		kmeans.fit(data)
		(cluster_centers, point_labels) = kmeans.cluster_centers_, kmeans.labels_
	
		disp = sum(
			[dst(data[current_row_index, :], cluster_centers[point_labels[current_row_index], :]) for current_row_index
			in range(shape[0])])
	
		refdisps = np.zeros((rands.shape[2],))
	
		for j in range(rands.shape[2]):
			kmeans = KMeans(**k_means_args_dict)
			kmeans.fit(rands[:, :, j])
			(cluster_centers, point_labels) = kmeans.cluster_centers_, kmeans.labels_
			refdisps[j] = sum(
				[dst(rands[current_row_index, :, j], cluster_centers[point_labels[current_row_index], :]) for
				current_row_index in range(shape[0])])
	
		# let k be the index of the array 'gaps'
		gaps[i] = np.mean(np.lib.scimath.log(refdisps)) - np.lib.scimath.log(disp)
	
	return ks, gaps


def elbow(array, maxK, message):
	print("elbow method")
	# k means determine k
	distortions = []
	for k in range(1, maxK):
		print("k={}".format(k))
		kmeanModel = KMeans(n_clusters=k).fit(array)
		kmeanModel.fit(array)
		#print("中心點:\n%s" %kmeanModel.cluster_centers_)
		#print("X矩陣各點與中心點的距離:\n%s" %cdist(array, kmeanModel.cluster_centers_, 'euclidean'))
		#print("距離最小值:%s" %np.min(cdist(array, kmeanModel.cluster_centers_, 'euclidean')))
		#print("距離取小加總/維度:\n%s" %(sum(np.min(cdist(array, kmeanModel.cluster_centers_, 'euclidean'), axis = 1))/ array.shape[0]))
		#array.shape[0]就是X[0]這個陣列的維度
		if message is not None:
			print(message)
		#計算每一個K-Means與X陣列中每一個值的距離
		distortions.append(sum(np.min(cdist(array, kmeanModel.cluster_centers_, 'euclidean'), axis = 1)) / array.shape[0])
		#print(distortions)
	return distortions


def plot_elbow(rangeK, distortions, filePath, fileName, title):
	'''Plot the elbow'''
	plt.plot(rangeK, distortions, 'yo-')
	plt.xlim(1, max(rangeK))
	plt.xlabel('Number of Clusters')
	plt.ylabel('Total Within Sum of Square')
	plt.title(title)
	#plt.show()	
	pc.create_path(filePath)
	plt.savefig(os.path.join(filePath, fileName))  
	plt.close()


def distinguish_multi_label(collection, clusters, array, _id, clusterKey, updateKey, updateQueryKey='_id'):
	'''	clusters is an integer, array and _id are list'''	
	
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)	
	
	# 分群
	kmeans_fit = cluster.KMeans(n_clusters=clusters).fit(array)
	array_labels = kmeans_fit.labels_
	'''
	for label in array_labels:
		print(label, end =" ")
	print("\n")
	'''	
	# 設定變數
	for _ in range(clusters):
		locals()['cluster%s' %_] = []
		locals()['cluster%s_id' %_] = []
	# 將資料依 label 分組
	for mongoId, st, label in zip(_id, array, array_labels):
		locals()['cluster%s' %label].append(st)
		locals()['cluster%s_id' %label].append(mongoId)
	
	# 找出各組的最大與最小值
	minArray = []
	maxArray = []
	for _ in range(clusters):
		minArray.append((_, np.amin(locals()['cluster%s' %_])))
		maxArray.append((_, np.amax(locals()['cluster%s' %_])))
	
	for _ in range(clusters):
		print("回寫前cluster{} min:{}, max:{}".format(_, np.amin(locals()['cluster%s' %_]), np.amax(locals()['cluster%s' %_])))
	print("\n")
	
	# 由小到大排序
	minArray = pc.bubbleSort_twoLayer(minArray, y=1)
	#print(minArray)
	seq = []
	for data in minArray:
		seq.append(data[0])
	maxArray = pc.follow_sort(maxArray, seq)
	#print(maxArray)
	
	i = 0
	while i < len(minArray): 
		if i < len(minArray)-1:
			if (maxArray[i][1] > minArray[i+1][1]) :
				print(i)
				print("有問題")
				os.system("pause")
				break
		
		#locals()['newCluster%s' %i] = locals()['cluster%s' %minArray[i][0]]
		#print(locals()['newCluster%s' %i])
		locals()['newCluster%s_id' %i] = locals()['cluster%s_id' %minArray[i][0]]
		#print(locals()['newCluster%s_id' %i])
		i += 1
	
	
	# 回寫
	for num in range(clusters):
		for id in locals()['newCluster%s_id' %num]:
			updateQuery = {updateQueryKey:id}
			updateDict = {updateKey:num}			
			ct.update_one(updateQuery, {'$set':updateDict}, upsert=True)


def inspect(collection, query, clusters, updateKey, clusterKey):			
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)		
	
	#檢查回寫結果是否正確
	print("開始檢查回寫結果")
	for _ in range(clusters):
		locals()['inspectCluster%s' %_] = []
	
	for two in ct.find(query):
		locals()['inspectCluster%s' %two[updateKey]].append(two[clusterKey])

	for num in range(clusters):
		print("回寫後檢查cluster{}, min:{}, max:{}".format(num, np.amin(locals()['inspectCluster%s' %num]), np.amax(locals()['inspectCluster%s' %num])))
	print("\n"*2)
	

def distinguish_label(collection, clusters, array, updateQueryKey, updateQueryValues, updateKey):
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection)
	
	# 分群
	print("開始計算 Kmeans")    
	kmeans_fit = cluster.KMeans(n_clusters = clusters).fit(array)
	array_labels = kmeans_fit.labels_
	'''
	for i,label in zip(range(0, len(array)), array_labels):
		print(label, end =" ")
	print("\n")
	'''
	# 找群組的最大最小值
	cluster0 = []
	cluster1 = []
	cluster0_id = []
	cluster1_id = []	
	for mongoId, elo, label in zip(updateQueryValues, array, array_labels):
		if label == 0:
			cluster0.append(elo)
			cluster0_id.append(mongoId)
		else:
			cluster1.append(elo)
			cluster1_id.append(mongoId)
	
	minElo0 = np.amin(cluster0)
	maxElo0 = np.amax(cluster0)
	minElo1 = np.amin(cluster1) 
	maxElo1 = np.amax(cluster1)
	print("回寫前cluster0 min:{}, max:{}".format(np.amin(cluster0), np.amax(cluster0)))
	print("回寫前cluster1 min:{}, max:{}".format(np.amin(cluster1), np.amax(cluster1)))
	
	#重分配label 數字小的在0組 數字大的在1組		
	if maxElo0 < minElo1:
		smallerCluster = cluster0
		biggerCluster = cluster1
		smallerCluster_id = cluster0_id
		biggerCluster_id = cluster1_id
	elif maxElo1 < minElo0:
		smallerCluster = cluster1
		biggerCluster = cluster0
		smallerCluster_id = cluster1_id
		biggerCluster_id = cluster0_id			
	else:
		print("有問題")
		os.system("pause")

	#回寫分群結果
	print("開始回寫分群結果")
	i = 0
	while i < len(biggerCluster):
		updateQuery = {updateQueryKey:biggerCluster_id[i]}
		updateDict = {updateKey:1}
		ct.update_one(updateQuery, {'$set':updateDict}, upsert = True)
		i += 1		

	j = 0
	while j < len(smallerCluster):
		updateQuery = {updateQueryKey:smallerCluster_id[j]}
		updateDict = {updateKey:0}
		ct.update_one(updateQuery, {'$set':updateDict}, upsert = True)
		j += 1
	
	#檢查回寫結果
	print("開始檢查回寫結果")
	#1.檢查有無漏寫
	isnull = ct.find_one({updateKey:None})
	print(isnull)
	#2.檢查回寫結果是否正確
	inspectCluster0 = []
	inspectCluster1 = []
	for two in ct.find():
		if two[updateKey] == 0:
			inspectCluster0.append(two['elo_difficulty'])
		else:	
			inspectCluster1.append(two['elo_difficulty'])

	print("回寫後檢查cluster0 min:{}, max:{}".format(np.amin(inspectCluster0), np.amax(inspectCluster0)))
	print("回寫後檢查cluster1 min:{}, max:{}".format(np.amin(inspectCluster1), np.amax(inspectCluster1)))
	print("\n"*2)	

def isnull(collection, query):
	db = pc.clientDB(database)
	ct = pc.clientCT(database, collection) 
	isnull = ct.find_one(query)
	if isnull is not None:
		print(isnull)

	
if __name__ == '__main__':	
	startTime = time.time()
	database = 'dotCode'
	game = 'Duck'
	maxSection = pc.find_maxSection(game)
	deterK = True
	
	Sec_staMK = True
	firstRecordMK = False
	accuTimeMK = False
	accuTimeZMK = False
	EloMK = False
	
	bestClusters = 5
	
	# 對關卡找最佳分群
	if Sec_staMK:
		print("start kmeans of section difficulty") 
		collection = 'Sec_sta'
		db = pc.clientDB(database)
		ct = pc.clientCT(database, collection)  
		filePath = r'D:\paper\practice\practice file\kmeans\Sec_sta'
		sections, item_difficulty, difficulty_degree = pc.add_difficulty(game, 1)
		item_difficulty = np.array(item_difficulty)
		item_difficulty = item_difficulty.reshape(-1, 1)
		
		# 找最佳群數,要回寫資料集的時候,把deterK設定成False
		if deterK:
			distortions = elbow(item_difficulty, 11, None)
	
			elbowTitle = 'The Elbow Method Showing the Optimal Clusters' 
			gapTitle = 'The Gap Statistic Method Showing the Optimal Clusters' 
			plot_elbow(range(1, 11), distortions, filePath, 'elbow', elbowTitle)
			ks, gaps = gap(item_difficulty, refs=None, nrefs=10, ks=range(1, 11))
			plot_elbow(ks, gaps, filePath, 'gaps', gapTitle)
		
		# 回寫資料集並檢查回寫區間是否正確,以及是否有資料未回寫	
		else:
			distinguish_label(collection, 3, item_difficulty, 'sectionId', sections, 'difficultyDegree_kmeans')
			distinguish_multi_label(collection, 5, item_difficulty, sections, 'elo_difficulty', 'difficultyDegree_kmeans'
									, updateQueryKey='sectionId')
			isnull(collection, {'difficultyDegree_kmeans':None})
			inspect(collection, {}, 5, 'difficultyDegree_kmeans', 'elo_difficulty')						
		
	
	# 對FirstRecord的玩家找最佳分群
	if firstRecordMK:
		print("start kmeans of FirstRecord of player's elo") 
		collection = 'FirstRecord'
		db = pc.clientDB(database)
		ct = pc.clientCT(database, collection)  
		filePath = r'D:\paper\practice\practice file\kmeans\FirstRecord\players'	
		for section in range(1, maxSection+1):
			print("start kmeans of FirstRecord of player's elo in section%d" %section) 
			playerElo = []
			_id = []
			for one in ct.find({"sectionId":section}):
				playerElo.append(one['elo_001'])
				_id.append(one['_id'])
			playerElo = np.array(playerElo)
			playerElo = playerElo.reshape(-1, 1)
			
			# 找最佳群數,要回寫資料集的時候,把deterK設定成False
			if deterK:
				distortions = elbow(playerElo, range(1, 6), None)
				elbowFileName = 'elbow_section%d' %section
				gapFileName = 'gaps_section%d' %section
				elbowTitle = 'The Elbow Method showing the optimal K of section%d' %section
				gapTitle = 'The Gap Method showing the optimal K of section%d' %section		
				plot_elbow(range(1, 5), distortions, filePath, elbowFileName, elbowTitle)
				ks, gaps = gap(playerElo, refs=None, nrefs=5, ks=range(1, 6))
				plot_elbow(ks, gaps, filePath, gapFileName, gapTitle)
			
			# 回寫資料集並檢查回寫區間是否正確,以及是否有資料未回寫			
			else:
				distinguish_multi_label(collection, 2, playerElo, _id, 'elo_001', 'playerDegree_kmeans'
										, updateQueryKey='_id')
				nullQuery = {'sectionId':section, 'playerDegree_kmeans':None}
				isnull(collection, nullQuery)
				inspect(collection, {'sectionId':section}, 2, 'playerDegree_kmeans', 'elo_001')
			
			del	playerElo, _id
	
	
	# 對AccuTime的玩家以欄位elo_001對每一個關卡找最佳分群, 每個關卡分群數不同
	if accuTimeMK:
		print("start kmeans of AccuTime of player's elo_001") 
		collection = 'AccuTime'
		db = pc.clientDB(database)
		ct = pc.clientCT(database, collection)  
		filePath = r'D:\paper\practice\practice file\kmeans\AccuTime\players'	
	
		clusters = [ 5, 3, 4, 4, 6, 4, 5, 3, 3, 3,
					3, 4, 4, 4, 4, 3, 4, 4, 5, 5,
					3, 4, 5, 6, 3, 5, 5, 4, 4, 5,
					4, 5, 4, 4, 4, 6, 3, 4, 6, 4,
					4, 5, 6, 5, 7, 7, 7, 6, 3, 5,
					4, 4, 4, 5, 5, 4, 5, 4, 5, 4
					]
		
		for section in range(1, maxSection+1):
			print("section%d" %section) 
			playerElo = []
			_id = []
			for one in ct.find({"sectionId":section}):
				playerElo.append(one['elo_001'])
				_id.append(one['_id'])
			playerElo = np.array(playerElo)
			playerElo = playerElo.reshape(-1, 1)
			
			# 找最佳群數,要回寫資料集的時候,把deterK設定成False
			if deterK:		
				distortions = elbow(playerElo, 9, None)
				elbowFileName = 'kmeans_section%d' %section
				gapFileName = 'gaps_section%d' %section
				elbowTitle = 'The Elbow Method showing the optimal K of section%d' %section
				gapTitle = 'The Gap Method showing the optimal K of section%d' %section
				plot_elbow(range(8), distortions, filePath, elbowFileName, elbowTitle)
				ks, gaps = gap(playerElo, refs=None, nrefs=5, ks=range(1, 9))
				plot_elbow(ks, gaps, filePath, gapFileName, gapTitle)
			
			# 回寫資料集並檢查回寫區間是否正確,以及是否有資料未回寫	
			else:
				distinguish_multi_label(collection, clusters[section-1], playerElo, _id, 'elo_001', 'playerDegree_kmeans'
										, updateQueryKey='_id')
				nullQuery = {'sectionId':section, 'playerDegree_kmeans':None}
				isnull(collection, nullQuery)
				inspect(collection, {'sectionId':section}, clusters[section-1], 'playerDegree_kmeans', 'elo_001')
			
			del	playerElo, _id	
	
	
	# 對AccuTime的玩家以欄位Zelo_001找最佳分群, 不分關卡一起分群
	if accuTimeZMK:
		print("start kmeans of AccuTime of player's Zelo_001") 
		collection = 'AccuTime'
		db = pc.clientDB(database)
		ct = pc.clientCT(database, collection)  
		filePath = r'D:\paper\practice\practice file\kmeans\AccuTime\players_all'	
	
		playerElo = []
		_id = []
		for one in ct.find({}):
			playerElo.append(one['Zelo_001'])
			_id.append(one['_id'])
		playerElo = np.array(playerElo)
		playerElo = playerElo.reshape(-1, 1)
	
		# 找最佳群數,要回寫資料集的時候,把deterK設定成False
		if deterK:		
			elbowFileName = 'elbow'
			gapFileName = 'gaps'
			elbowTitle = 'The Elbow Method showing the optimal Clusters'
			gapTitle = 'The Gap Statistic Method showing the optimal Clusters'
			distortions = elbow(playerElo, range(1, 11), None)
			plot_elbow(range(1,11), distortions, filePath, elbowFileName, elbowTitle)
			ks, gaps = gap(playerElo, refs=None, nrefs=11, ks=range(1, 11))
			plot_elbow(ks, gaps, filePath, gapFileName, gapTitle)
		
		else:
			distinguish_multi_label(collection, clusters, playerElo, _id, 'Zelo_001', 'ZplayerDegree_kmeans'
									, updateQueryKey='_id')
			nullQuery = {'ZplayerDegree_kmeans':None}
			isnull(collection, nullQuery)
			inspect(collection, {}, clusters, 'ZplayerDegree_kmeans', 'Zelo_001')
		
		del	playerElo, _id	
	
	
	# 對資料集Elo的玩家以欄位averageElo找最佳分群
	if EloMK:
		print("start kmeans of player's average elo in collection Elo") 
		collection = 'Elo'
		db = pc.clientDB(database)
		ct = pc.clientCT(database, collection)  
		filePath = r'D:\paper\practice\practice file\kmeans\%s\players' %collection
		for id in range(1, maxId): 
			playerElo = []
			_id = []
			for one in ct.find({"userId":id}):
				playerElo.append(one['averageElo'])
				_id.append(one['_id'])
			playerElo = np.array(playerElo)
			playerElo = playerElo.reshape(-1, 1)
		
		# 找最佳群數,要回寫資料集的時候,把deterK設定成False
		if deterK:
			distortions = elbow(playerElo, 6, None)
			elbowFileName = 'elbow_section%d' %section
			gapFileName = 'gaps_section%d' %section
			elbowTitle = 'The Elbow Method showing the optimal K of section%d' %section
			gapTitle = 'The Gap Method showing the optimal K of section%d' %section		
			plot_elbow(range(6), distortions, filePath, elbowFileName, elbowTitle)
			ks, gaps = gap(playerElo, refs=None, nrefs=5, ks=range(1, 6))
			plot_elbow(ks, gaps, filePath, gapFileName, gapTitle)
		
		# 回寫資料集並檢查回寫區間是否正確,以及是否有資料未回寫		
		else:
			distinguish_multi_label(collection, 2, playerElo, _id, 'elo_001', 'playerDegree_kmeans'
									, updateQueryKey='_id')
			nullQuery = {'sectionId':section, 'playerDegree_kmeans':None}
			isnull(collection, nullQuery)
			inspect(collection, {'sectionId':section}, 2, 'playerDegree_kmeans', 'elo_001')
		
		del	playerElo, _id
	
	pc.pass_time(startTime, time.time())