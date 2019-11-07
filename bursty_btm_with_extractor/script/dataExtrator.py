def do_something_with(line):
	items = line.split(",")
	itemCount = 0;
	for item in items:
		if(itemCount >=1):
			if(item != ""):
				with open('../2m_data/'+str(datefile)+'.txt', 'a+') as the_file:
					the_file.write(item+'\n')
		itemCount = itemCount + 1;



datefile = 0;
with open("../2m_data/re-reservoir_sampling_hydrated_2M_group_by_date_tweet_dic.csv") as infile:
	for line in infile:
		do_something_with(line)
		datefile = datefile + 1 
		print(str(datefile));