import nltk
import yaml
import re
import sys
import os
from pprint import pprint

fp = open('accuracy.yml','r')
line = fp.readline()
line2=[]
while line:
    line2.append(line[:-1])
    line = fp.readline()
    

length = len(line2[0])
total_count = 0
for i in range(0,length):
    count = 0
    bayes = line2[0][i]
    maxent = line2[1][i]
    svm = line2[2][i]
    if int(bayes) == 1:
        count +=1
    if int(maxent) == 1:
        count +=1
    if int(svm) == 1:
        count +=1
    if count > 1:
        total_count +=1
print "Combined",
print total_count


