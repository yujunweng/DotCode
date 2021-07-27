from pymongo import MongoClient
from sklearn import cluster, datasets, preprocessing, metrics
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
import PaperCommon as pc


def plot_multi_yaxis(xaxis, yaxisList, xlabel, ylabelsList):
	fig, ax = plt.subplots(figsize=(10, 6))
	fig.subplots_adjust(right=0.75)

	twin1 = ax.twinx()
	twin2 = ax.twinx()
	#twin1 = ax.twiny()
	twin2 = twin1.twiny()
	# Offset the right spine of twin2.  The ticks and label have already been
	# placed on the right by twinx above.
	#twin2.spines['right'].set_position(("axes", 1.2))
	yaxisP1, yaxisP2, yaxisP3 = yaxisList
	ylabel1, ylabel2, ylabel3 = ylabelsList 
	p1, = ax.plot(xaxis, yaxisP1, "b-", label=ylabel1)
	p2, = twin1.plot(xaxis, yaxisP2, "r-", label=ylabel2)
	p3, = twin2.plot(xaxis, yaxisP3, "g-", label=ylabel3)

	ax.set_xlim(0, 60)
	ax.set_ylim(-1, 3)
	twin1.set_ylim(0, 2000)
	#twin2.set_ylim(1, 65)
	
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel1)
	#twin1.set_ylabel(ylabel2)
	#twin2.set_ylabel(ylabel3)

	ax.yaxis.label.set_color(p1.get_color())
	twin1.yaxis.label.set_color(p2.get_color())
	twin2.yaxis.label.set_color(p3.get_color())

	tkw = dict(size=4, width=1.5)
	ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
	twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
	#twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
	#ax.tick_params(axis='x', **tkw)

	ax.legend(handles=[p1, p2, p3])
	#ax.legend(handles=[p1, p2])
	plt.show()
	plt.close()


def plot_scatter(xList, yList, color, scale, title, xLabel, yLabel, filePath, fileName, cbar_label=None, xLimit=100, yLimit=1):
	'''分散點圖, 顏色有漸層效果, 僅1個子圖, xLabel and yLabel must be string'''
	#有cmap
	plt.style.use('dark_background')
	fig, ax = plt.subplots(figsize=(10, 6)) #plt.subplots是開出總畫布
	plt.title(title, fontsize = 14)
	#等同於 fig = plt.figure()
	#ax = plt.subplot(111)
	#ax = plt.subplots()
	
	#給子圖一個名稱後面設定給color
	sc = ax.scatter(xList, yList, c=color, s=scale, cmap='bwr', alpha=0.7) 

	#設定X軸與Y軸字體大小
	ax.set_xlabel(xLabel, fontsize = 12)
	ax.set_ylabel(yLabel, fontsize = 12)
	
	#设置坐标轴刻度
	my_x_ticks = np.arange(0, (xLimit+(xLimit/10)), (xLimit/10))
	my_y_ticks = np.arange(0, (yLimit+(yLimit/10)), (yLimit/10))
	#plt.xticks(my_x_ticks)
	plt.yticks(my_y_ticks)
	
	#设置刻度字体大小
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	
	#設置格線
	ax.grid(True)
	
	#有子圖時需將子圖設定給colorbar當對象
	cbar = plt.colorbar(sc)
	cbar.set_label(cbar_label,fontsize=12)
	
	#设置图例
	#plt.legend(loc = 'best', fontsize = 12)
	
	#圖表過度集中可以使用.tight_layout分開
	plt.tight_layout()
	
	#儲存圖檔
	pc.create_path(filePath)
	plt.savefig(os.path.join(filePath, fileName))   
	
	#显示图片
	#plt.show()
	plt.close()


def plot_single_scatter(xList, yList, scale, title, xLabel, yLabel, filePath, fileName, color='skyblue', xLimit=100, yLimit=1):
	'''畫單一顏色的分散點圖,僅1個子圖'''
	#沒有cmap
	#xLabel and yLabel must be word
	plt.style.use('dark_background')
	fig, ax = plt.subplots(figsize=(13.66, 7.68)) #plt.subplots是開出總畫布
	plt.title(title, fontsize=18)
	
	#給子圖一個名稱後面設定給color
	sc = ax.scatter(xList, yList, c=color, s=scale, alpha=0.7) 

	#設定X軸與Y軸字體大小
	ax.set_xlabel(xLabel, fontsize=18)
	ax.set_ylabel(yLabel, fontsize=18)
	
	#设置坐标轴范围
	#plt.xlim((-5, 5))     #也可写成plt.xlim(-5, 5) 
	plt.ylim((0, yLimit+yLimit/10))     #也可写成plt.ylim(-4, 4)	
	
	#设置坐标轴刻度
	my_x_ticks = np.arange(0, (xLimit+(xLimit/10)), (xLimit/10))
	my_y_ticks = np.arange(0, (yLimit+(yLimit/10)), (yLimit/10))
	#plt.xticks(my_x_ticks)
	#plt.yticks(my_y_ticks)
	
	#设置刻度字体大小
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	
	#設置格線
	ax.grid(True)
	
	#设置图例
	#plt.legend(loc='best', fontsize=12)
	
	#圖表過度集中可以使用.tight_layout分開
	plt.tight_layout()
	
	#儲存圖檔
	pc.create_path(filePath)
	plt.savefig(os.path.join(filePath, fileName))   
	
	#显示图片
	#plt.show()
	plt.close()


def plot_multi_scatter(xList, yList, scale, title, xLabel, yLabel, savePath, saveName, legendIllustration=None):
	''' 分散點圖, 依據axNum的數字決定子圖的數量, 
		圖的數量有2, 5, 6 三種, 會呈現在同一個畫布上
	'''
	# 決定子圖的數量
	axNum = len(xList)
	
	# 設置畫布背景顏色
	plt.style.use('dark_background')
	plt.figure(figsize=(13.66, 7.68)) 
	colorList = pc.color_degrees()
	
	if scale is None:
		scale = pc.create_lists(0, len(xList), [])
		for i in range(len(xList)):
			scale[i] = pc.create_lists(0, len(xList[i]), 50)
	
	if legendIllustration is None:
		legendIllustration = [num for num in range(len(xList))]
	
	axes = []
	for i in range(axNum):
		locals()['ax%s' %i] = plt.scatter(xList[i], yList[i], s=scale[i], color=colorList[i], label=legendIllustration[i], alpha=0.7)
		axes.append(locals()['ax%s' %i])
	plt.legend(axes, legendIllustration, loc='best', edgecolor='w',  prop={'size':10})
	
	#設定title, x, y軸標籤
	plt.title(title, fontsize=18)
	plt.xlabel(xLabel, fontsize=18)
	plt.ylabel(yLabel, fontsize=18)

	#设置坐标轴范围
	#plt.xlim((-5, 5))     #也可写成plt.xlim(-5, 5) 
	plt.ylim(0, 1)     #也可写成plt.ylim(-4, 4)	

	#設置格線, 格線為虛線, minor為次要格線
	plt.grid(True)
	
	pc.create_path(savePath)
	plt.savefig(os.path.join(savePath, saveName))
	#plt.show()
	plt.close()
	

def plot_line(yList, title, savePath, saveFile, xList=None):
	''' 折線圖, 僅有一個子圖'''
	pc.create_path(savePath)
	
	if xList is None:
		xList = [i+1 for i in range(len(yList))]
	#plt.style.use('dark_background')
		
	#設置畫布大小
	plt.figure(figsize=(13.66, 7.68))

	# 標示x軸(labelpad代表與圖片的距離)
	plt.xlabel('quantity of answers', fontsize=18, labelpad=10)
	# 標示y軸(labelpad代表與圖片的距離)
	plt.ylabel('elo points', fontsize=18, labelpad=10)
	# 標示title
	plt.title(title, fontsize=18)
	

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
	
	#plt.xticks(fontsize=15)
	#plt.yticks(fontsize=15)
	
	#plt.plot(xList, yList, 's-', color='g', label='Elo estimating')
	plt.plot(xList, yList, color='r', label='Elo estimating')	
	
	# 顯示出線條標記位置
	plt.legend(loc='best', fontsize=18)
	
	plt.savefig(os.path.join(savePath, saveFile))
	#plt.show()
	plt.close()


def plot_box(data, savePath, saveName, title=None, xLabel=None, yLabel=None, labels=None):
	'''盒鬚圖 僅有1個子圖'''
	plt.figure(figsize=(13.66, 7.68)) 
	pc.create_path(savePath)
	outPath = os.path.join(savePath, saveName)	
	plt.boxplot(data, labels = labels)
	plt.title(title)
	plt.xlabel(xLabel)
	plt.ylabel(yLabel)
	plt.savefig(outPath)
	#plt.show()
	plt.close()


def plot_distribution(data, distribution, savePath, saveName):
	'''用EDA檢查data的資料分布型態'''	
	pc.create_path(savePath) 
	fig = plt.figure()
	scipy.stats.probplot(data, dist=distribution, sparams=(5,), fit=True, plot=plt)
	plt.savefig(os.path.join(savePath, saveName))
	#plt.show()
	plt.close()
	#print("%s completed!" %distribution)


def plot_multi_subplots(data, plotType, savePath, saveName, subs=(3,3), **kwargs):
	'''用EDA檢查data的資料分布型態
		將多種分布呈現現在同一圖中	
	'''	
	m, n = subs[0], subs[1]
	pc.create_path(savePath) 
	fig, axes = plt.subplots(m, n)
	#plt.figure(figsize=(13.66, 7.68))
	i = 0
	for row in range(m):
		for column in range(n):
			print("第{}幅畫".format(i+1))
			#plt.text(0.5, 0.5, str(dist), fontsize=8, ha='bottom')
			if plotType == 'probplot':
				axes[row, column] = scipy.stats.probplot(data, dist=data[i], sparams=(5,), fit=True, plot=plt)
			elif plotType == 'line':
				axes[row, column] = plt.plot([(j+1) for j in range(len(data[i]))], data[i], color='r', label='Elo estimating')
			i += 1
	del data
	gc.collect()
	#fig.subplots_adjust(hspace=0.8, wspace=0.5) #設定子圖的間隔
	
	saveFile = os.path.join(savePath, saveName)
	print("繪圖中請稍候...")
	#plt.show()
	plt.savefig(saveFile)
	
	plt.close()
	print("completed!")


def plot_hist(data, savePath, saveName):			
	'''人數長條圖'''
	bins = [i for i in range(0, 300+1, 1)]
	plt.hist(data, bins = bins)
	plt.savefig(os.path.join(savePath, saveName))
	#plt.show()	#會讓圖檔儲存無效
	plt.close()
	