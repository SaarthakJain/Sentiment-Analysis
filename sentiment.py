import nltk
import yaml
import re
import sys
import os
from pprint import pprint
from nltk.corpus import stopwords
import wx
from sklearn import svm
from sklearn.svm import SVC
import pickle
featureList = []

sortedFeatures = []  

class BasicUI(wx.Frame):
  
    def __init__(self, parent, title):
        super(BasicUI, self).__init__(parent, title=title,size=(500, 400))
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):
    
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#006699')

        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Stencil')

        font.SetPointSize(14)
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Lucida Handwriting')

        font1.SetPointSize(12)


        vbox = wx.BoxSizer(wx.VERTICAL)
             
    
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Enter your text here')
        st2.SetFont(font)
        hbox2.Add(st2)
        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=20)
    
        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.tc2.SetFont(font1)
       
        hbox3.Add(self.tc2, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, 
            border=10)

        vbox.Add((-1, 25))
       
        
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(panel, label='Show results....', size=(200,30))
        btn1.SetFont(font)
        hbox5.Add(btn1)
        self.Bind(wx.EVT_BUTTON, self.DisplayResults, id = btn1.GetId() )
        
        vbox.Add(hbox5, flag=wx.ALIGN_CENTER|wx.CENTER, border=10)

        vbox.Add((-1, 10))
        panel.SetSizer(vbox)

    def DisplayResults(self, event):
        testreview1 =self.tc2.GetValue()
        if testreview1 !="":
            dial = wx.MessageDialog(None,"wait while review is being processed..." ,'progress', wx.OK)        
            dial.ShowModal()
            global sortedFeatures
            global featureList
            feature_vector=[]
            labels = []
            sentiment=[]
            review=[]
            #print (featureList)
            fp=open('reviews.yml','r')
            line = fp.readline()
            reviews = []
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
                sentiment.append(line2[1])
                review.append(line2[0])
                processedreview = processreview(line2[0])
                featureVector = getFeatureVector(processedreview)
                reviews.append((featureVector,line2[1]))
                for word in featureVector:
                    featureList.append(word)
                line=fp.readline()

            fp.close()            
            sortedFeatures = sorted(featureList)
            #print sortedFeatures[-1]
            for line in review:
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
        
       
            processedTestreview = processreview(testreview1)
            extracted_feature_set = extract_features(getFeatureVector(processedTestreview))
            
            #1. Using Naive Bayes Classifier
            """training_set = nltk.classify.util.apply_features(extract_features, reviews)
            NBClassifier = nltk.NaiveBayesClassifier.train(training_set)
            """
            f= open('NB_classifier.pickle')
            NBClassifier = pickle.load(f)
            f.close()
            result_Bayes = NBClassifier.classify(extracted_feature_set)


            #2. Using Maximum Exntropy Classifier
            """MaxEntClassifier = nltk.classify.maxent.MaxentClassifier.train(training_set, 'GIS', trace=3, \
            encoding=None, labels=None, sparse=True, gaussian_prior_sigma=0, max_iter = 5)
            """
            f= open('Maxent_classifier.pickle')
            MaxEntClassifier = pickle.load(f)
            f.close()
            result_MaxEntropy = MaxEntClassifier.classify(extracted_feature_set)


            
            #3. Using Linear SVM
            clf = SVC(kernel='linear')
            clf.fit(feature_vector,labels)
            inputList=getinput(processedTestreview)
            outputValue = clf.predict(inputList)
            if outputValue[0] == 0:
               result_SVM = "Positive"
            elif outputValue[0] == 1:
               result_SVM = "Negative"
            elif outputValue[0] == 2:
               result_SVM = "Neutral"


            ans_list=[result_Bayes.lower(),result_SVM.lower(),result_MaxEntropy.lower()]
            ans="positive" if ans_list.count("positive") >=2 else "negetive"
            
            result =  "\n polarity(combined)\t :: " + ans +"\n********************************"+"\nBayes \t :: "+result_Bayes +"\nSVM \t :: "+ result_SVM.lower() +"\nMax Entropy:: "+result_MaxEntropy
            ans_list=[]
            dial = wx.MessageDialog(None,result,'sentiment polarity', wx.OK)        
            dial.Destroy()
            if dial.ShowModal() == wx.ID_OK:
                
                dial1 = wx.MessageDialog(None, 'do you wish to check for more sentences???', 'more...', 
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                dial1.Destroy()
                if dial1.ShowModal() == wx.ID_YES :        
                    BasicUI(None, title='Educational review sentiment analysis')
                else:
                     dial2=wx.MessageBox('Thank You for using this System...\n Developed by Priyanka Sodhia and Saarthak Jain', 'Info',wx.OK | wx.ICON_INFORMATION)
                     sys.exit(0)

        else :
            dial = wx.MessageDialog(None,"please enter a review!!",'sentiment polarity', wx.OK)
            dial.ShowModal()
            dial.Destroy()
                    
                
            



def processreview(review):
    # process the reviews
    
    #Convert to lower case
    review = review.lower()
    #Convert www.* or https?://* to URL
    review = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',review)
    #Convert @username to AT_USER
    review = re.sub('@[^\s]+','AT_USER',review)
    #Remove additional white spaces
    review = re.sub('[\s]+', ' ', review)
    #trim
    review = review.strip('\'"?,.')
    # remove ....
    review = re.sub('[.]+','.',review)
    return review
#end

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end


def getinput(review):   
        global sortedFeatures
        map={}
        #print sortedFeatures
        for w in sortedFeatures:
            map[w] = 0
        review_words=review.split(' ')
        if '' in review_words:
             review_words.remove('')
        #print review_words
        for word in review_words:
            #process the word (remove repetitions and punctuations)
            word = replaceTwoOrMore(word) 
            #set map[word] to 1 if word exists
            if word in map:
                map[word] = 1
        return map.values()



#start getfeatureVector
def getFeatureVector(review):
    featureVector = []
    #split review into words
    words = review.split()
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

#start extract_features
def extract_features(review):
    global featureList
    review_words = set(review)
    #print review_words
    features = {}
    for word in featureList:
        """if word == (word in review_words):
            print "yes"""
        #print (review_words^set(featureList))
        features['contains(%s)' % word] = (word in review_words)
    return features
#end

if __name__ == "__main__":
    
    app = wx.App()
    frame=BasicUI(None, title='Educational review sentiment analysis')
    frame.Show()
    app.MainLoop()
