import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Importing Dependencies
try:
    import sqlite3
    import gensim
    import pickle
    from nltk.tokenize import word_tokenize
    import os , sys , glob , docx2txt
    from gensim.corpora import Dictionary
except ImportError:
    print ("Error: can't import certain dependencies")     


# Connecting Database
try:
    conn = sqlite3.connect('C:\\xampp\\htdocs\\ChatBot_v4\\chat_system.db')
    c = conn.cursor()
except IOError:
    print ("Error: can't connect to database")


# Getting the User query
c.execute("SELECT document FROM docs ORDER BY id DESC LIMIT 1")
query = c.fetchone()
str_query = str(query)
query_doc = [w.lower() for w in word_tokenize(str_query)]

dictionary = Dictionary.load_from_text("C:\\xampp\\htdocs\\ChatBot_v4\\Models\\document_finder_dictionary.sav")
query_doc_bow = dictionary.doc2bow(query_doc)

tf_idf = pickle.load(open('C:\\xampp\\htdocs\\ChatBot_v4\\Models\\document_finder_TfIdf_model.sav', 'rb'))
query_doc_tf_idf = tf_idf[query_doc_bow]

dsims = pickle.load(open('C:\\xampp\\htdocs\\ChatBot_v4\\Models\\document_finder_model.sav', 'rb'))
dsims[query_doc_tf_idf]

# Reading all the files
try:
    path = 'C:\\xampp\\htdocs\\ChatBot_v4\\Documents'
    dirs = os.listdir( path )
    processed_texts = []
    all_documents = {}
    i=0
    for filename in dirs:
        all_documents[i] = filename
        i+=1
except IOError:
    print ("Error: can't open files")  
    

try:
    max_val = max(dsims[query_doc_tf_idf])
    max_index = dsims[query_doc_tf_idf].argmax()
    finalVariable = all_documents[max_index]
except OverflowError:
    print ("Error: Index out of bounds") 


try:
    c1 = c.execute('SELECT max(id) FROM docs')
    maxid = c1.fetchone()[0]
    maxIntid = int(maxid)
    c.execute("UPDATE docs SET reference=(?) WHERE id =(?)",[finalVariable,maxIntid])
    conn.commit()
    c.close()
    conn.close()
except IOError:
    print ("Error: can't write to database") 
