import io 
import os
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
#word_tokenize accepts a string as an input, not a file. 
stop_words = set(stopwords.words('english')) 


directory="small/"

for filename in os.listdir(directory):
    appendFile = open("smallout/"+filename,'a')
    if filename.endswith(".txt"):
        with open(directory+filename) as fp:
            line = fp.readline()
            while line:
                #print line
                if len(line) > 0 and line !="\n":
                    words = line.split()
                    for r in words:
                        if not r in stop_words:
                            appendFile.write(r+" ")
                    appendFile.write("\n")
                line = fp.readline()
        appendFile.close();