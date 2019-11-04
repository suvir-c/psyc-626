'''
USC CSCI 626 Course Project
Sentiment analysis of ‘to trump tweets’ within 100K-tweet dataset.
Date: Oct, 19, 2019
The method used for sentiment analysis is based on [1].
[1] Colneriĉ, Niko, and Janez Demsar. "Emotion recognition on twitter: Comparative study and training a unison model." IEEE Transactions on Affective Computing (2018).
Basic preprocessing using tweet-preprocessor(https://pypi.org/project/tweet-preprocessor/) is applied. Each tweet is labeled or vectorized with Ekman's six basic emotions. 
Notes:
The tweet’s texts only containing #mention, #URL, and emoji are removed is discarded. The emotion analysis model labels them (the empty string ‘’ ) as Joy.
'''



import io
import re
import string
import jsonlines

import pandas as pd
import numpy as np
import multiprocessing

# for date regroup
import locale
import arrow
from locale import atof
from dateutil import parser
from datetime import datetime
from datesupport import *

# for emotion analysis
from emotion_predictor import EmotionPredictor

# for preprocessing
import preprocessor as p

# for sentiment analysis
import nltk

def emotion_analysis(tweets_text_list):
    '''
    Input: 1D tweet text list -- tweets_text_list
    '''

    emotion_label = model.predict_classes(tweets_text_list)
    emotion_prob = model.predict_probabilities(tweets_text_list)

    return emotion_label, emotion_prob

def clean_tweet(tweet):
    '''
    Input: Tweet text -- tweet
    '''
    
    # remove punctuation
    exclude = set(string.punctuation)
    c_tweet = ''.join(ch for ch in tweet if ch not in exclude)
    
    # remove RT and :
    c_tweet = ' '.join(re.sub("RT"," ", c_tweet).split())
    
    return c_tweet

def preprocess_tweet(tweet):
    
    tweet = p.clean(tweet)
    
    return clean_tweet(tweet).lower()

def tokenize_tweet(tweet):
    
    tweet = p.tokenize(tweet)
    
    return clean_tweet(tweet).lower()


# load data
jsonl_fname = './data/re-reservoir_sampling_hydrated_100K.jsonl'
reader = jsonlines.open(jsonl_fname)

df = pd.DataFrame([obj for obj in reader])
df = df[['created_at','full_text','entities','extended_entities','lang']]
print('There are {} tweets in original dataset.'.format(str(len(df))))

# implement preprocessing
df['pre_text'] = df['full_text'].apply(preprocess_tweet)
df['token_text'] = df['full_text'].apply(tokenize_tweet)

# remove empty pre_text
df = df[df.pre_text != '']
print('There are {} tweets in dataset (after language filtering).'.format(str(len(df))))

# rearrange the tweets into date
df['created_date'] = pd.to_datetime(df['created_at'])
df['month/day'] = df['created_date'].apply(convertUTCtoMonthDay)

# method 2 more hardcode
df = df[df.lang == 'en']
print('There are {} tweets in dataset (after language filtering).'.format(str(len(df))))

# emotion analysis
# set emotion model
# emotion_model = 'ekman'
emotion_model = 'plutchik'

model = EmotionPredictor(classification=emotion_model, setting='mc')

tweets_text_list = df.pre_text.tolist()
tweets_emotion_label, tweets_emotion_prob = emotion_analysis(tweets_text_list)

# save results
csv_fname = jsonl_fname.replace('.jsonl','.csv')
csv_fname = csv_fname.replace('./data','./data/to_trump_chunk_small_res')
tweets_emotion_label.to_csv(csv_fname.replace('.csv','_{}_label.csv'.format(emotion_model)))
tweets_emotion_prob.to_csv(csv_fname.replace('.csv','_{}_prob.csv'.format(emotion_model)))


tweets_emotion_prob = tweets_emotion_prob.drop(columns=['Tweet'])
con_df = pd.concat([df, tweets_emotion_label, tweets_emotion_prob], axis=1)

con_df.to_csv(csv_fname.replace('.csv','_{}_comb.csv'.format(emotion_model)))