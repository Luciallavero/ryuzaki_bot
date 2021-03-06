# coding: utf-8

import constants
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Resource, Api
import nltk
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
import sys
import warnings

def get_formalities_reply(formality) :
    if any(remove_punctuation_marks(formality).lower() in remove_punctuation_marks(greet).lower() for greet in constants.GREETING_INPUTS) :
        return random.choice(constants.GREETING_REPLIES)
    elif any(remove_punctuation_marks(formality).lower() in remove_punctuation_marks(thanks).lower() for thanks in constants.THANKS_INPUTS) :
        return random.choice(constants.THANKS_REPLIES)

def get_lemmatized_tokens(text):
    normalized_tokens = nltk.word_tokenize(remove_punctuation_marks(text.lower()))
    return [nltk.stem.WordNetLemmatizer().lemmatize(normalized_token) for normalized_token in normalized_tokens]

corpus = open('corpus.txt', 'r' , errors = 'ignore').read().lower()
documents = nltk.sent_tokenize(corpus)

def get_query_reply(query) :    
    documents.append(query)
    tfidf_results = TfidfVectorizer(tokenizer = get_lemmatized_tokens, stop_words = 'english').fit_transform(documents)
    cosine_similarity_results = cosine_similarity(tfidf_results[-1], tfidf_results).flatten()
    # The last will be 1.0 because it is the Cosine Similarity between the first document and itself
    best_index = cosine_similarity_results.argsort()[-2]
    documents.remove(query)
    if cosine_similarity_results[best_index] == 0 :
        return "I am sorry! I don't understand you..."
    else :
        return documents[best_index]

def remove_punctuation_marks(text) :
    punctuation_marks = dict((ord(punctuation_mark), None) for punctuation_mark in string.punctuation)
    return text.translate(punctuation_marks)

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

class Reply(Resource) :
    def get(self) :
        if request.args.get('q') :
            formality_reply = get_formalities_reply(request.args.get('q'))
            if  formality_reply :
                return jsonify({'reply': formality_reply + ' ' + random.choice(constants.SWEETS)})
            else :
                return jsonify({'reply': get_query_reply(request.args.get('q'))})
        else :
            return jsonify({'error': 'query is empty'})

api.add_resource(Reply, '/reply.json')

if __name__ == "__main__" :

    app.run()
