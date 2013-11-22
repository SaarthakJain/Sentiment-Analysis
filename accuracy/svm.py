from sklearn import svm
import nltk
import yaml
import re
import sys
import os
from pprint import pprint
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from sklearn.svm import SVC
import pickle

sortedFeatures = []
def processTweet(tweet):
    # process the tweets
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"?,.')
    #remove ...
    tweet = re.sub('[.]+','.',tweet)
    return tweet
#end

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end

def getinput(tweet):   
        global sortedFeatures
        map={}
        #print sortedFeatures
        for w in sortedFeatures:
            map[w] = 0
        tweet_words=tweet.split(' ')
        if '' in tweet_words:
             tweet_words.remove('')
        #print tweet_words
        for word in tweet_words:
            #process the word (remove repetitions and punctuations)
            word = replaceTwoOrMore(word) 
            #set map[word] to 1 if word exists
            if word in map:
                map[word] = 1
        return map.values()


#start getfeatureVector
def getFeatureVector(tweet):
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        if(w in stopwords.words('english') or val is None):
            continue
        else:
            featureVector.append(w.lower())

    #print ("this is feature vector",featureVector)
    return featureVector

def getSVMFeatureVectorAndLabels():
    featureList = []
    global sortedFeatures
    feature_vector=[]
    labels = []
    sentiment=[]
    tweet=[]
    
    fp=open('reviews.yml','r')
    line = fp.readline()
    tweets = []
    while line:
        if ('| ' in line):
            line2=line.split('| ')
            line2[1] = line2[1][:-1]
        else:
            newstr=''
            c=1
            while(c!=0):
                st1=line.split('\n')
                newstr = newstr + '. ' +st1[0]
                line=fp.readline()
                if('| ' in line):
                    st1=line.split('| ')
                    newstr = newstr + '. ' +st1[0]
                    line2 = []
                    line2.insert(0,newstr)
                    line2.insert(1,st1[1][:-1])
                    c=0
        sentiment.append(line2[1])
        tweet.append(line2[0])
        
        #print tweet, sentiment
        processedTweet = processTweet(line2[0])
        featureVector = getFeatureVector(processedTweet)
        #tweets.append((featureVector,line2[1]))
        #print (featureVector)
        for word in featureVector:
            featureList.append(word)
        line=fp.readline()
    #print featureList #9800
    sortedFeatures = sorted(featureList)
    for line in tweet:
        values=getinput(line)
        feature_vector.append(values)

    
    for s in sentiment:
        if(s == 'positive'):
            label = 0
        elif(s == 'negative'):
            label = 1
        elif(s == 'neutral'):
            label = 2
        labels.append(label)            
    #return the list of feature_vector and labels
    return {'feature_vector' : feature_vector, 'labels': labels}
        

    fp.close()
         

if __name__ == "__main__":
    result = getSVMFeatureVectorAndLabels()
    #print result
    clf = SVC(kernel='linear')
    #print result
    clf.fit(result['feature_vector'],result['labels'])
    f = open('SVM_classifier.pickle', 'wb')
    pickle.dump(clf, f)
    f.close()
    sent = []
    c3 = 0
    SVMCount = []
    total_reviews = 0
    fp=open('test.yml','r')
    line = fp.readline()
    while line:
        if ('| ' in line):
            line2=line.split('| ')
            line2[1] = line2[1][:-1]
        else:
            newstr=''
            c=1
            while(c!=0):
                st1=line.split('\n')
                newstr = newstr + '. ' +st1[0]
                #line2[0]=line2[0].append(line.split('\n'))
                line=fp.readline()
                if('| ' in line):
                    st1=line.split('| ')
                        #print st1[1][:-1]
                    newstr = newstr + '. ' +st1[0]
                        #print (type(newstr))
                        #print st1[1]
                    line2 = []
                    line2.insert(0,newstr)
                    line2.insert(1,st1[1][:-1])
                    c=0
        sent = line2[1]
        testreview1 = line2[0]
        total_reviews = total_reviews + 1
        #SVM Accuracy
        inputList=getinput(processTweet(testreview1))
        outputValue = clf.predict(inputList)
        if outputValue[0] == 0:
            res = "positive"
        elif outputValue[0] == 1:
            res =  "negative"
        elif outputValue[0] == 2:
            res = "neutral"
        if res==sent:
            SVMCount.append(1)
            c3 +=1
        else:
            SVMCount.append(0)
        line=fp.readline()
    fp.close()
    print "Accuracy of SVM = ",
    print c3/total_reviews
    fp = open('accuracy.yml','a')
    for item in SVMCount:
        fp.write(str(item))
    fp.write("\n")
    fp.close()
