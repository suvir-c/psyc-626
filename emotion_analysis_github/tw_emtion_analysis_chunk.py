import io
import re
import json
import jsonlines
import argparse
import multiprocessing
import requests

import pandas as pd
import numpy as np
import preprocessor as p

# for date regroup
import locale
import arrow
from locale import atof
from dateutil import parser
from datetime import datetime
from datesupport import *

from emotion_predictor import EmotionPredictor

# for sentiment analysis
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

### funcitons

def vader_sentiment_analysis(text):
    '''
    tweet sentiment analysis
    Input: text 
    '''
    
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text)
    return vs['compound']

def emotion_analysis(tweets_text_list):
    '''
    tweet emotion anlaysis
    Input: 1D tweet text list -- tweets_text_list
    '''

    emotion_label = model.predict_classes(tweets_text_list)
    emotion_prob = model.predict_probabilities(tweets_text_list)

    return emotion_label, emotion_prob

def clean_tweet(tweet):
    '''
    remove RT and :
    '''
    return ' '.join(re.sub("RT|:"," ", tweet).split())

def preprocess_tweet(tweet):
    
    tweet = p.clean(tweet)
    
    return clean_tweet(tweet)

def tokenize_tweet(tweet):
    
    tweet = p.tokenize(tweet)    
    
    return clean_tweet(tweet)


def tweet_entity_linking(text,Tha = 0.1):

    # text = "I definitely like ice cream better than tomatoes."
    TAGME_URL = 'https://tagme.d4science.org/tagme/tag'

    params = {
        'text': text,
        'gcube-token': "2ed60a81-a4be-4591-b9b5-7c661e785f65-843339462",
        'lang': 'en',
        'tweet': 'true',
        'include_abstract': 'true',
        'include_categories': 'true'
    }
    json_response = requests.get(TAGME_URL, params=params).json()
    normalized_json = pd.io.json.json_normalize(json_response['annotations'])
    return pd.DataFrame(normalized_json[normalized_json["rho"] > Tha][['abstract','rho','spot']])



def tweet_enrich_entity_linking(text, Tha = 0.2):
    text_df = tweet_entity_linking(text,Tha)

    if not text_df.empty:
        entity_links = ' '
        
        for row in text_df.iterrows():
            entity_links = entity_links + row[1].abstract + ' '

        text = text + entity_links
    
    return text

def add_features(df):
    # enrich data with entity linking
    df['enriched_pre_text'] = df['pre_text'].apply(tweet_enrich_entity_linking)
    # sentiment analysis
    df['sentiment'] = df['pre_text'].apply(vader_sentiment_analysis)
    df['enriched_sentiment'] = df['enriched_pre_text'].apply(vader_sentiment_analysis)

    # rearrange the tweets into date
    df['created_date'] = pd.to_datetime(df['created_at'])
    df['month/day'] = df['created_date'].apply(convertUTCtoMonthDay)
    
    return df

def parallelize_dataframe(df, func, n_cores=4):
    df_split = np.array_split(df, n_cores)
    pool = multiprocessing.Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


# parameter settings

parser = argparse.ArgumentParser()
parser.add_argument('--csv_fname', type=str, default='./data/to_trump_chunk/tweets_chunk_0.csv', help='csv file name')
parser.add_argument('--cpuNum', type=int, default=4, help='CPU numbers')
parser.add_argument('--emotion_model', type=str, default='plutchik', help='emotion framework')

args = parser.parse_args()

print('Working on ')
print(args)

csv_fname = args.csv_fname
cpuNum = args.cpuNum
chunk_num = cpuNum
emotion_model = args.emotion_model

import time
stime = time.time()

#load the data
df = pd.read_csv(csv_fname, lineterminator='\n')
df = df[:100]

# df = add_features(df)
df = parallelize_dataframe(df, add_features)
model = EmotionPredictor(classification=emotion_model, setting='mc')

to_trump_tweet_list = np.array_split(df, chunk_num)
pool = multiprocessing.Pool(processes=cpuNum) 
tweets_emotion_list = pool.map(emotion_analysis, (to_trump_tweet.pre_text.tolist() for to_trump_tweet in to_trump_tweet_list))
tweets_emotion_list_label, tweets_emotion_list_prob = map(list,zip(*tweets_emotion_list))

tweets_emotion_label = pd.concat(tweets_emotion_list_label,ignore_index=True)
tweets_emotion_prob = pd.concat(tweets_emotion_list_prob,ignore_index=True)

csv_fname = csv_fname.replace('to_trump_chunk','to_trump_chunk_res')

tweets_emotion_prob = tweets_emotion_prob.drop(columns=['Tweet'])
tweets_emotion_label = tweets_emotion_label.drop(columns=['Tweet'])

concat_df = pd.concat([df, tweets_emotion_prob, tweets_emotion_label], axis=1)
concat_df = concat_df.drop(columns=['Unnamed: 0','entities','extended_entities','lang','token_text','created_date'])
concat_df.to_csv(csv_fname.replace('.csv','_analysis.csv'))

print(time.time() - stime)