# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 16:54:48 2018

@author: NAYAKPR
"""
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Importing Dependencies
try:
    import sqlite3
    import re
    import string
    import gensim
    import pickle
    import csv
    from gensim.corpora import Dictionary
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
except ImportError:
    print ("Error: can't import certain dependencies")               
       

# Connecting Database
try:
    conn = sqlite3.connect('C:\\xampp\\htdocs\\ChatBot_v4\\chat_system.db')
    c = conn.cursor()
except IOError:
    print ("Error: can't connect to database")              


# Getting the User query
c.execute("SELECT message FROM chats ORDER BY id DESC LIMIT 1")
query = c.fetchone()
str_query = str(query)
query_doc = [w.lower() for w in word_tokenize(str_query)]


# Finding keywords
new_query_doc = re.sub('[^ a-zA-Z0-9]', '', str_query)
word_list = []
word_list = new_query_doc.split()

# For one word queries
single = str(word_list)
single = re.sub('[^ a-zA-Z0-9]', '', single)

# Removing Stopwords 
stop = stopwords.words('english') + list(string.punctuation)
lemmatizer = WordNetLemmatizer()
query_doc =[lemmatizer.lemmatize(i) for i in word_tokenize(str_query.lower()) if i not in stop]

dictionary = Dictionary.load_from_text("C:\\xampp\\htdocs\\ChatBot_v4\\Models\\sentence_similarity_dictionary.sav")
query_doc_bow = dictionary.doc2bow(query_doc)

tf_idf = pickle.load(open('C:\\xampp\\htdocs\\ChatBot_v4\\Models\\sentence_similarity_TfIdf_model.sav', 'rb'))
query_doc_tf_idf = tf_idf[query_doc_bow]

sims = pickle.load(open('C:\\xampp\\htdocs\\ChatBot_v4\\Models\\sentence_similarity_model.sav', 'rb'))
sims[query_doc_tf_idf]

# Opening solution csv
try:
    with open('C:\\xampp\\htdocs\\ChatBot_v4\\All_Issues_Solutions_File.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        train_texts = []
        for row in reader:
            train_texts.append(row['Issues'])
except IOError:
    print ("Error: can't open file All_Issues_Solutions")  

try:
    with open ('C:\\xampp\\htdocs\\ChatBot_v4\\All_Docs_Urls.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        train_texts1 = {}
        for row in reader:
            train_texts1[row['Docs']] = row['Urls']
except IOError:
    print ("Error: can't open file All_Docs_Urls")  

try:
    with open ('C:\\xampp\\htdocs\\ChatBot_v4\\Single_Topics.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        train_texts2 = {}
        for row in reader:
            train_texts2[row['Topics']] = row['Meaning']
except IOError:
    print ("Error: can't open file Single topics")  



# Most Important loop starts
max_index = -1
suggestion = "NA"
finalVariable = "NA"

# To check if query is single word
if len(single.split()) > 1:
    max_val = max(sims[query_doc_tf_idf])
else:
    max_val = -2 


if max_val!=0:
    max_index = sims[query_doc_tf_idf].argmax()
else:
    max_index = -1
print("Maximum value is:", max_val ,"and is at the index:",max_index)

if max_val != 0:
    if max_val == -2:
        for ite in train_texts2:
            if ite != single:
                finalVariable = "Unknown issue"+"\n"
                for itr in train_texts1:
                    if itr != single:
                        if single in train_texts1:
                            suggestion = train_texts1[single]
                        else:
                            suggestion = "none"+"\n";
                        break
                    else:
                        suggestion = "none"+"\n"; 
    else:
        finalVariable = train_texts[max_index]
        suggestion = "none"+"\n";  
elif max_val == 0:
    for elem in word_list:
        if elem not in train_texts1:
            finalVariable = "Unknown issue"+"\n"
            suggestion = "none"+"\n";
            continue
        else:
            print("Matched element: ",elem)
            print("Suggestion is: ", suggestion)
            finalVariable = "Other issue"+"\n"
            suggestion = elem
            break
        
print("The matching query for:", single, "is: ", finalVariable)
print("Suggestion is:", suggestion)

try:
    c1 = c.execute('SELECT max(id) FROM chats')
    maxid = c1.fetchone()[0]
    maxIntid = int(maxid)
    c.execute("UPDATE chats SET similar_message=(?),suggestion=(?) WHERE id =(?)",[finalVariable,suggestion,maxIntid])
    conn.commit()
    c.close()
    conn.close()
except IOError:
    print ("Error: can't write to database") 