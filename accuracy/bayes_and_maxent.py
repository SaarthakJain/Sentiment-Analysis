import nltk
import yaml
import re
import sys
import os
from pprint import pprint
from nltk.corpus import stopwords
import easygui as eg
import pickle


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
    tweet = tweet.strip('\'"')
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
#end

#start extract_features
def extract_features(tweet):
    tweet_words = set(tweet)
    #print tweet_words
    features = {}
    for word in featureList:
        """if word == (word in tweet_words):
            print "yes"""
        #print (tweet_words^set(featureList))
        features['contains(%s)' % word] = (word in tweet_words)
    return features
#end


if __name__ == "__main__":
    featureList = []
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
                    #print line2
        #pprint (line2[0])
        #print c
        #print line2
        sentiment = line2[1]
        tweet = line2[0]
        #print tweet, sentiment
        processedTweet = processTweet(tweet)
        #print processedTweet
        featureVector = getFeatureVector(processedTweet)
        tweets.append((featureVector,sentiment))
        #print (featureVector)
        for word in featureVector:
            featureList.append(word)
        line=fp.readline()
    #print(featureList)
    fp.close()
    
    c1 = 0
    c2 = 0
    tot = 0
    NBCount = []
    MaxEntCount=[]
    sent = []
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
        processedTestreview = processTweet(testreview1)
        extracted_feature_set = extract_features(getFeatureVector(processedTestreview))
        tot=tot+1
    #1. Using Naive Bayes Classifier
        """training_set = nltk.classify.util.apply_features(extract_features, reviews)
        NBClassifier = nltk.NaiveBayesClassifier.train(training_set)
        """
        f= open('NB_classifier.pickle')
        NBClassifier = pickle.load(f)
        f.close()
        result_Bayes = NBClassifier.classify(extracted_feature_set)
        if result_Bayes.lower()==sent:
            NBCount.append(1)
            c1 +=1
        else:
            NBCount.append(0)


    #2. Using Maximum Exntropy Classifier
        """MaxEntClassifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'GIS', trace=3, \
        encoding=None, labels=None, sparse=True, gaussian_prior_sigma=0, max_iter = 5)
        """
        f= open('Maxent_classifier.pickle')
        MaxEntClassifier = pickle.load(f)
        f.close()
        result_MaxEntropy = MaxEntClassifier.classify(extracted_feature_set)
        if result_MaxEntropy.lower()==sent:
            MaxEntCount.append(1)
            c2 +=1
        else:
            MaxEntCount.append(0)
        line=fp.readline()

    fp.close()
    fp = open('accuracy.yml','w')
    print "Bayes = ",
    print c1/tot
    print "\nMax Ent = ",
    print c2/tot
    for item in NBCount:
        fp.write(str(item))
    fp.write("\n")
    for item in MaxEntCount:
        fp.write(str(item))
    fp.write("\n")
    fp.close()
