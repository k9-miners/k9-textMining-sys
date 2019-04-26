import re
import nltk
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.util import ngrams
import string
import json
from pymongo import MongoClient
import spacy
import time
import pandas as pd

uri = "mongodb://35.247.134.85:27017/"
client = MongoClient(uri)

# Get the database named "textMine"
textMineDB = client["textMine"]

# Get the collections
# Collection for document details
doc_details_col = textMineDB["doc_details"]
# Collection for bigram details
bigram_col = textMineDB["bigram_col"]
# Collection for trigram details
trigram_col = textMineDB["trigram_col"]
# Collection for json doc
json_col = textMineDB["json_col"]


# -------------------------------------------------------------------------
# Input processing Section
# -------------------------------------------------------------------------
# List of stopwords in the nltk lib
en_stopwords = set(stopwords.words('english'))

# Remove all non ascii characters
def _removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

# Initialize spacy 'en' model, keeping only tagger component needed for lemmatization
nlp = spacy.load('en', disable=['parser', 'ner'])

# Function to tokenize the sentence and return the lemmatized token
def clean_comment(text):
    # regex to remove all the punctuations
    regex = re.compile('[' + re.escape(string.punctuation) + '\\r\\t\\n]')
    # replace all the punctuation with space
    nopunct = regex.sub(" ", str(text))
    
    #tokenize the no punctation text
    remove_punct = nlp(nopunct)
    lemma = [token.lemma_ for token in remove_punct]
    lemmatized = [w for w in lemma if w not in en_stopwords and w != "-PRON-" and w.isspace() == False]
    lemmatized_nopunct = []
    for l in lemmatized:
        np = regex.sub(" ", l)
        np = np.replace(" ", "")
        lemmatized_nopunct.append(np)
        

    return lemmatized_nopunct



# Function to structured the data to be inserted into the database
def structurize_data(id, frequency, url, webpage_details):

    # Initialize the total_terms of each document to 0
    total_terms = 0

    # For loop to sum all the frequency of each word to obtain the total terms
    # in the document
    for i in frequency:
        total_terms = total_terms + i[1]
    
    # Create the dict for word frequency
    word_frequency = {}

    # For loop to structurized the frequency into the format:
    # {"new": 10, "york": 5}
    for f in frequency:
        word_frequency[f[0]] = f[1]
    
    # Append each webpage details into the main array
    webpage_details.append({
        '_id': id,
        'total_Word_Count': total_terms,
        'word_frequency': word_frequency 
    })

    return webpage_details

def bigram(text):
    all_bigrams = ngrams(text, 2)
    ngram_list = []
    for ngram in all_bigrams:
        lowered_bigram_tokens = map(lambda token: token.lower(), ngram)
        if any(token not in en_stopwords for token in lowered_bigram_tokens):
            ngram_list.append(' '.join(ngram))
    # return ngram_list 
    freqDist = FreqDist(ngram_list)
    frequency = freqDist.most_common()
    return frequency

def process_bigram(id, lemmatized, bigram_details):
    bi = bigram(lemmatized)
    bi_freq = {}
    bi_freq['_id'] = id
    for b in bi:
        bi_freq[b[0]] = b[1]
    
    bigram_details.append(bi_freq)
    return bigram_details


def trigram(text):
    all_trigrams = ngrams(text, 3)
    ngram_list = []
    for ngram in all_trigrams:
        lowered_trigram_tokens = map(lambda token: token.lower(), ngram)
        if any(token not in en_stopwords for token in lowered_trigram_tokens):
            ngram_list.append(' '.join(ngram))
    # return ngram_list 
    freqDist = FreqDist(ngram_list)
    frequency = freqDist.most_common()
    return frequency

def process_trigram(id, lemmatized, trigram_details):
    tri = trigram(lemmatized)
    tri_freq = {}
    tri_freq['_id'] = id
    for t in tri:
        tri_freq[t[0]] = t[1]
    
    trigram_details.append(tri_freq)
    return trigram_details

# Function to get the raw data and structurized the data
def process_raw_data():
    
    # The main array to store each block of structurized data
    webpage_details = []
    bigram_details = []
    trigram_details = []

    # For all the block from the raw data
    for block in json_col.find({"status": 'F'}):

        # Save each section of data to corresponding variables
        content = block["content"]
        title = block["title"]
        id = block["_id"]
        url = block["url"]

        # Stringify all the data and remove the non ascii data
        content = str(content)
        content = _removeNonAscii(content)
        title = str(title)
        title = _removeNonAscii(title)

        # Lemmatize the content data
        lemmatized = clean_comment(content)

        # Lemmatize the title data
        lemmatized_title = clean_comment(title)
        
        # For loop to append the title tokens into the lemmatized
        for t in lemmatized_title:
            lemmatized.append(t)
        
        # Get the frequency distributions of the lemmatized data
        freqDist = FreqDist(lemmatized)
        # Rearrange the frequencies in descending order
        frequency = freqDist.most_common()

        # Structured all the data to be inserted into the database
        webpage_details = structurize_data(id, frequency, url, webpage_details)
        bigram_details = process_bigram(id, lemmatized, bigram_details)
        trigram_details = process_trigram(id, lemmatized, trigram_details)
    
    update_field = {"$set": { "status": "T" } }
    json_col.update_many({}, update_field)
    
    try:
        doc_insert = doc_details_col.insert_many(webpage_details)
        print("doc_details collection modified")
    except Exception as e:
        print(e)

    try:
        bigram_insert = bigram_col.insert_many(bigram_details)
        print("bigram_col collection modified")
    except Exception as e:
        print(e)
    
    try:
        trigram_insert = trigram_col.insert_many(trigram_details)
        print("trigram_col collection modified")
    except Exception as e:
        print(e)

start = time.time()
lemmatized = process_raw_data()
print(time.time()-start)
