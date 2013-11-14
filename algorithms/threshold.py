##########
#Threshold.py OTSU Thresholding Extended to three thresholds.
#Mark Lowerison 2013-11-07
##########

##########
#Get some packages
##########

import sqlite3 as sqlite
import sys
import random
from math import floor
import matplotlib.pyplot as plt
import numpy as np

##########
#Simulate some data
##########

records = range(10000)
observations = []
for i in records:
	observations.append([int(floor(random.gauss(60, 12.5)))])
	observations.append([int(floor(random.expovariate(0.05)))])
	#observations.append([int(floor(random.gauss(40, 12.5)))])


def divide(x, y):
	if y == 0:
		return float(-sys.maxint)
	else:
		return x/y
	
##########
#Throw the simulated data into a local sqlite DB
##########
con = sqlite.connect('threshold.db')
with con:
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS scores;')
    cur.execute('CREATE TABLE scores (id INT PRIMARY KEY ASC, score INT);')    
    cur.executemany('INSERT INTO scores (`id`, `score`) values (NULL, ?);', observations,)
    

##########
#Get some data from the database to feed the thresholding routines. 
##########

#Get distinct number of levels of score, max, min and range.
with con:
	cur = con.cursor()
	cur.execute("select 'scores' as var, count(distinct(score)) as observation from scores;")
	levels = cur.fetchone()
	cur.execute("select 'minScore' as var, min(score) as observation from scores;")
	minScore = cur.fetchone()
	cur.execute("select 'maxScore' as var, max(score) as observation  from scores;")
	maxScore = cur.fetchone()
	cur.execute("select 'thresholds' as var, (max(score) - min(score))-1 as observation from scores")
	thresholds = cur.fetchone()
	
	print thresholds
	cur.execute("select score from scores order by score asc;")
	scores = cur.fetchall()

#Print some status info.
print "In the submitted population there are %s distinct %s, a %s of %s, and a %s of %s." % (levels[1],levels[0], minScore[0], minScore[1], maxScore[0], maxScore[1])
print "There are %s distinct threshold values" % thresholds[1]

#Start Threshold detection loops.

#Threshold calculation.
categories = int(sys.argv[1])
hist, bin_edges = np.histogram(scores, bins=range(minScore[1],maxScore[1]+1), density=True)
hist = np.array(hist)
bin_edges = np.array(bin_edges)
product = hist * bin_edges[1:]
minint = float(-sys.maxint)
	

if categories == 2:
	
	print "You have requested splitting the population into %s categories\nBeginning Loop:" % categories
	
	for i in range(thresholds[1]):
		lowerArray = product[0:i+1]
		upperArray = product[i+1:] 		
		lowerProbSum = sum(hist[0:i+1])
		upperProbSum = sum(hist[i+1:])
		lowerMu = sum([divide(x,lowerProbSum) for x in lowerArray])
		upperMu = sum([divide(x,upperProbSum) for x in upperArray])
		lowerVar = lowerMu**2*lowerProbSum
		upperVar = upperMu**2*upperProbSum
		overallVar = lowerVar + upperVar
		if overallVar > minint:
			cutPointi = bin_edges[i]
			minint = overallVar

	plt.bar(bin_edges[:-1], hist, width = 1)
	plt.xlim(min(bin_edges), max(bin_edges))
	plt.axvline(cutPointi, color='r', linestyle='dashed', linewidth=2)
	plt.show() 


elif categories == 3:
	counter = 0
	print "You have requested splitting the population into %s categories" % categories
	for i in range(thresholds[1]):
		for j in range(thresholds[1]):
			if j > i:
				
	
				lowerArray = product[0:i+1]
				middleArray = product[i+1:j+1] 
				upperArray = product[j+1:]
				lowerProbSum = sum(hist[0:i+1])
				middleProbSum = sum(hist[i+1:j+1])
				upperProbSum = sum(hist[j+1:])
				lowerMu = sum([divide(x,lowerProbSum) for x in lowerArray])
				middleMu = sum([divide(x,middleProbSum) for x in middleArray])
				upperMu = sum([divide(x,upperProbSum) for x in upperArray])
				
				lowerVar = lowerMu**2*lowerProbSum
				middleVar = middleMu**2*middleProbSum
				upperVar = upperMu**2*upperProbSum
				overallVar = lowerVar + middleVar + upperVar
				if overallVar > minint:
					cutPointi = bin_edges[i]
					cutPointj = bin_edges[j]
					minint = overallVar
					print bin_edges[i], bin_edges[j], overallVar
				

	plt.bar(bin_edges[:-1], hist, width = 1)
	plt.xlim(min(bin_edges), max(bin_edges))
	plt.axvline(cutPointi, color='r', linestyle='dashed', linewidth=2)
	plt.axvline(cutPointj, color='r', linestyle='dashed', linewidth=2)
	plt.show() 





elif categories == 4:
	counter = 0
	print "You have requested splitting the population into %s categories" % categories
	for i in range(thresholds[1]):
		for j in range(thresholds[1]):
			for k in range(thresholds[1]):
				if k > j > i:
					
					lowerArray = product[0:i+1]
					twoArray = product[i+1:j+1] 
					threeArray = product[j+1:k+1]
					upperArray = product[k+1:]
					lowerProbSum = sum(hist[0:i+1])
					twoProbSum = sum(hist[i+1:j+1])
					threeProbSum = sum(hist[j+1:k+1])
					upperProbSum = sum(hist[k+1:])
					lowerMu = sum([divide(x,lowerProbSum) for x in lowerArray])
					twoMu = sum([divide(x,twoProbSum) for x in twoArray])
					threeMu = sum([divide(x, threeProbSum) for x in threeArray])
					upperMu = sum([divide(x,upperProbSum) for x in upperArray])
					
					lowerVar = lowerMu**2*lowerProbSum
					twoVar = twoMu**2*twoProbSum
					threeVar = threeMu**2*threeProbSum
					upperVar = upperMu**2*upperProbSum
					overallVar = lowerVar + twoVar + threeVar + upperVar
					if overallVar > minint:
						cutPointi = bin_edges[i]
						cutPointj = bin_edges[j]
						cutPointk = bin_edges[k]
						minint = overallVar
						print bin_edges[i], bin_edges[j], bin_edges[k], overallVar
					

	plt.bar(bin_edges[:-1], hist, width = 1)
	plt.xlim(min(bin_edges), max(bin_edges))
	plt.axvline(cutPointi, color='r', linestyle='dashed', linewidth=2)
	plt.axvline(cutPointj, color='r', linestyle='dashed', linewidth=2)
	plt.axvline(cutPointk, color='r', linestyle='dashed', linewidth=2)
	plt.show() 






elif categories == 5:
	counter = 0
	print "You have requested splitting the population into %s categories" % categories
	for i in range(thresholds[1]):
		for j in range(thresholds[1]):
			for k in range(thresholds[1]):
				for l in range(thresholds[1]):
					if l > k > j > i:
						print i+1, j+1, k+1, l+1,  counter
						counter += 1



else:
	print "USAGE:  python threshold.py [2 < int < 5]"








#Plot histogram of scores
