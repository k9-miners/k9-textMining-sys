from flask import Flask, render_template, request, redirect, url_for
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import string
from pymongo import MongoClient
import time
import spacy
import math
from operator import itemgetter


# Class to process the input and return related documents
class queryInput:
    # -------------------------------------------------------------------------
    # Database Section
    # -------------------------------------------------------------------------
    # Connect to the database client

    # connect from Local host
    uri = "mongodb://localhost:27017/"

    # Connect remotely
    # uri = "mongodb://35.247.134.85:27017/"
    # client = MongoClient(uri)

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
    en_stopwords = {'has', 'on', 'some', 'too', 'shan', "aren't", "you'll", 'further', 'most', 'shouldn', 'against', "you'd", "couldn't", 'i', 'here', 're', 'you', 'our', "don't", 'itself', 'why', "doesn't", "hadn't", "haven't", 'if', 'under', 'but', "it's", 'while', 'o', "wouldn't", 'them', 'its', 'm', 'during', "shouldn't", 'she', 'him', 'such', 'isn', "won't", 'your', 'below', 'myself', 'few', "didn't", 'again', 'before', "needn't", 'ours', 'should', 'all', 'over', "she's", 'after', 'her', "that'll", 'nor', 'where', 'is', 'have', 'each', 's', 'didn', 'now', 'will', 'this', 'above', 'wouldn', "shan't", 'mightn', 'being', 'ma', 'to', 'once', 'own', "isn't", 'aren', 'had', 'so', 'until', 'in', 'needn', 'yourselves', 'or', 'just', 'yourself', "wasn't", 'he', 'mustn', 'as', 'hasn', 'ourselves', 'there', 'not', 'don', 'be', 'we', 'down', 'doing', 'because', 'the', 'themselves', 'do', 'y', 'did', 'can', 'does', 'me', 'with', 'been', 'of', 'up', 'between', 'who', 'how', 'which', 'my', 'other', "you're", 'his', 'these', 'then', 'very', 'won', 'those', 'into', "weren't", 'for', 'both', 'ain', 'out', 'no', 'about', 'from', 'and', 'it', 'hers', 'hadn', 'am', "mustn't", "hasn't", 'off', 'through', 'was', 'doesn', 'd', 'are', 'any', 've', 'll', 'were', 'an', 'more', "should've", 'they', 'only', 'same', 'when', 'couldn', 'herself', 'by', "you've", 'than', 'having', 'whom', 'at', "mightn't", 'what', 'theirs', 'himself', 'their', 'weren', 't', 'haven', 'a', 'wasn', 'that', 'yours'}

    # Initialize spacy 'en' model, keeping only tagger component needed for lemmatization
    nlp = spacy.load('en', disable=['parser', 'ner'])

    # Function to tokenize the sentence and return the lemmatized token
    def clean_comment(self, text):
        # regex to remove all the punctuations
        regex = re.compile('[' + re.escape(string.punctuation) + '\\r\\t\\n]')
        # replace all the punctuation with space
        nopunct = regex.sub(" ", str(text))
        
        #tokenize the no punctation text
        remove_punct = self.nlp(nopunct)
        lemma = [token.lemma_ for token in remove_punct]
        lemmatized = [w for w in lemma if w not in self.en_stopwords and w != "-PRON-" and w.isspace() == False]

        return lemmatized

    # Function to get the bigram
    def get_bi_string(self, text):

        # Create list of bigram from the input
        all_bigrams = ngrams(text, 2)
        bigram_list = []
        for bigram in all_bigrams:
            # if the token in the trigram is not a stopword
            if any(token not in self.en_stopwords for token in bigram):
                # join the token to form a trigram and append it to the list
                bigram_list.append(' '.join(bigram))
        return bigram_list

    # Function to get the trigram
    def get_tri_string(self, text):
        
        # Create list of trigram from the input
        all_trigrams = ngrams(text, 3)
        trigram_list = []

        for trigram in all_trigrams:
            # if the token in the trigram is not a stopword
            if any(token not in self.en_stopwords for token in trigram):
                # join the token to form a trigram and append it to the list
                trigram_list.append(' '.join(trigram))

        return trigram_list


    # Function to get the frequencies of all the tokens
    # and compute the obtained frequencies into a matrix
    def get_frequencies(self, lemmatized, bi_string, tri_string):
        query_string = "word_frequency"
        all_related_docs = []
        total_freq = []
        total_bi_freq = []
        total_tri_freq = []
        len_of_doc = []

        # -----------------------------------------------------------
        # Section to obtain the frequencies of each token
        # -----------------------------------------------------------

        # For each of the token
        for token in lemmatized:
            total_id_freq = {}
            query_string_token = query_string + "." + token
            count = 0
            for a in self.doc_details_col.find({query_string_token:{"$exists": True}}, {"web_url": 0, "total_Word_Count": 0}):

                # If the queried document id is not in the list then append it to the list
                # This is to union all the queried documents for the tokens, bigrams and trigrams
                if(a['_id'] not in all_related_docs):
                    all_related_docs.append(a['_id'])
                
                # Create dict of id: frequency 
                # {'id-1': 5, 'id-2': 3}
                total_id_freq[a['_id']] = a['word_frequency'][token]

                # Count the amount of documents queried for a single token
                count = count + 1
            total_freq.append(total_id_freq)
            len_of_doc.append(count)

        # If the bigram is not null then query for the frequencies
        if(bi_string != []):
            for bi_token in bi_string:
                total_bi_id_freq = {}
                count = 0
                for b in self.bigram_col.find({bi_token: {"$exists": True}}):
                    if(b['_id'] not in all_related_docs):
                        all_related_docs.append(b['_id'])
                    total_bi_id_freq[b['_id']] = b[bi_token]
                    count = count + 1
                total_bi_freq.append(total_bi_id_freq)
                len_of_doc.append(count)

        # If the trigram is not null then query for the frequencies
        if(tri_string != []):
            for tri_token in tri_string:
                total_tri_id_freq = {}
                count = 0
                for t in self.trigram_col.find({tri_token: {"$exists": True}}):
                    if(t['_id'] not in all_related_docs):
                        all_related_docs.append(t['_id'])
                    print(t[tri_token])
                    total_tri_id_freq[t['_id']] = t[tri_token]
                    count = count + 1
                total_tri_freq.append(total_tri_id_freq)
                len_of_doc.append(count)

        # -----------------------------------------------------------
        # Section to obtain the matrix
        # -----------------------------------------------------------

        total_matrix = []
        
        # for freq dict in the list
        # [{'id1': 2}, {}] - Each dict representing frequencies for each token
        for freq in total_freq:
            word_freq_union = []
            
            # search for frequencies for corresponding id
            for id in all_related_docs:
                try:
                    word_freq_union.append(freq[id])
                except:
                    # if the token does not have frequency in a document
                    # set the frequency to 0
                    word_freq_union.append(0)
            total_matrix.append(word_freq_union)


        for bi_freq in total_bi_freq:
            bi_freq_union = []
            for id in all_related_docs:
                try:
                    bi_freq_union.append(bi_freq[id])
                except:
                    bi_freq_union.append(0)
            total_matrix.append(bi_freq_union)
        

        for tri_freq in total_tri_freq:
            tri_freq_union = []
            for id in all_related_docs:
                try:
                    tri_freq_union.append(tri_freq[id])
                except:
                    tri_freq_union.append(0)
            total_matrix.append(tri_freq_union)
        
        return [total_matrix, len_of_doc, all_related_docs]

    #------------------------------------------------------------------------------
    # TF-IDF
    #------------------------------------------------------------------------------

    # Get the idf for each token
    def get_idf(self, len_of_doc):
        idf = []

        # Count the total documents in the database
        doc_count = self.doc_details_col.count_documents({})

        # for amount of documents for each token
        # l = amount of docs for each of the token
        for l in len_of_doc:
            if l != 0:
                # idf = total documents / amount of docs for each token
                wtq = float(doc_count) / l
                idf.append(math.log10(wtq))
            else:
                idf.append(0)
        
        return idf

    #  Function to compute the results
    def get_result(self, matrix, idf):
        result = []
        try:
            # for each document column
            for col in range(0, len(matrix[0])):
                temp = 0
                # for each token in row format
                for row, df in zip(matrix, idf):
                    value = row[col]
                    # if value greater than 0
                    if value > 0:
                        # modify the value based on the tf-idf formula
                        # The df value
                        value = 1 + math.log10(value)
                    # Sum each idf * df together
                    temp = temp + (float(df) * float(value))
                result.append(temp)
            
            return result
        except Exception as e:
            return result
    
    def process_for_frontend(self, sorted_result, token):
        display_content = []

        # return display_content
        for t in sorted_result:
            result = list(self.json_col.find({"_id": t[0]}))
            content = result[0]['content']

            # sentencelist = nltk.sent_tokenize(content)
            sentencelist = [s.strip() for s in content.splitlines()]
            # sentencelist = content.split('.')
            
            count = 0
            concordance = ""
            for sent in sentencelist:
                if any(y in sent.lower() for y in token):
                    sent = sent.split('.')
                    for s in sent:
                        if any(y in s.lower() for y in token):
                            s = s.strip()
                            s = s.strip(string.punctuation)
                            concordance = concordance + s + '. '
                            if len(concordance) > 50:
                                break
                    break

            if concordance == "":
                sent = sentencelist[0].strip('.')
                for s in sent:
                    concordance = concordance + s.strip(string.punctuation) + '. '
                    if len(concordance) > 50:
                        break
            
            limitLength = ""
            splitConcordance = concordance.split()
            if len(splitConcordance) > 30:
                for i in range(0, 30):
                    limitLength = limitLength + ' ' + splitConcordance[i]
                limitLength = limitLength + '... '
            else:
                limitLength = concordance



            display_content.append({
                "doc_id": result[0]['_id'],
                'doc_url': result[0]['url'],
                'doc_title': result[0]['title'],
                'concordance': limitLength,
                'query_term': token,
            })
        return display_content




    # Function to call all other functions to process the input
    def mainProcess(self, input):

        # Lemmatize the input and compute the sets of bigram and trigram that
        # can be formed
        lemmatized = self.clean_comment(input)
        bi_string = self.get_bi_string(lemmatized)
        tri_string = self.get_tri_string(lemmatized)

        # Get the frequencies of the word tokens, bigrams and trigrams
        get_freq = self.get_frequencies(lemmatized, bi_string, tri_string)

        # extract each components from the get_freq function
        
        # list of all queried documents
        all_related_docs = get_freq[2]
        # list of amount of docs for each token
        len_of_doc = get_freq[1]
        # The matrix 
        total_matrix = get_freq[0]

        # Get the list of idf for each token
        idf = self.get_idf(len_of_doc)

        # Get the list of final result
        result = self.get_result(total_matrix, idf)

        # -------------------------------------------------------------
        # Sort the final result based on the computed scores
        # -------------------------------------------------------------
        sorted_result = []
        for a, r in zip(all_related_docs, result):
            sorted_result.append(tuple((a, r)))

        sorted_result = sorted(sorted_result, key=itemgetter(1), reverse=True)
        # print(sorted_result)
        # self.process_for_frontend(sorted_result, lemmatized)

        # Return the structurized data to be processed in the front-end
        return self.process_for_frontend(sorted_result, lemmatized)


queryObj = queryInput()
app = Flask(__name__)

@app.route("/dashboard")
def home():

    input = request.args['query']
    print(input)

    if input == "": 
        return render_template('Detail-none.html', page_title = "Dashboard")
    else:
        global posts
        posts = queryObj.mainProcess(input)
        if posts == []:
            # if no result return no result page
            return render_template('Detail-none.html', page_title = "Dashboard", input=input)
        else:
            # if results are available return result page
            return render_template('Detail.html', page_title = "Dashboard", posts=posts, input=input)



@app.route("/", methods = ["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form['queryText']

        return redirect(url_for('home', query=query))

    return render_template('Home.html', page_title = 'K9Miners')    

@app.route("/about")
def about():
    return render_template('About.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
