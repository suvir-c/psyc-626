def do_something_with(line):
	items = line.split(",")
	itemCount = 0;
	for item in items:
		if(itemCount >=1):
			if(item != ""):
				with open('extracted/'+str(datefile)+'.txt', 'a+') as the_file:
					the_file.write(item+'\n')
		itemCount = itemCount + 1;



datefile = 0;
with open("source.csv") as infile:
	for line in infile:
		do_something_with(line)
		datefile = datefile + 1 
		print(str(datefile));