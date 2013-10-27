levels = range(10)
counter = 0

for i in levels:
	for j in levels:
		if j > i:
			print i, j, counter
		counter = counter + 1
	
	