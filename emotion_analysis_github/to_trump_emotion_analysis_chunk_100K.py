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
import jsonlines
import re
import argparse

import pandas as pd
import numpy as np
import multiprocessing
import preprocessor as p

from emotion_predictor import EmotionPredictor

def emotion_analysis(tweets):

    model = EmotionPredictor(classification='ekman', setting='mc')

    tweets_text_list = tweets.re_text.tolist()

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

cpuNum = 4
chunk_num = 4

# load data A: from jsonlines
reader = jsonlines.open('./data/re-reservoir_sampling_hydrated_100K.jsonl')
to_trump_df = pd.DataFrame([obj for obj in reader])#[:10000]
to_trump_df = to_trump_df[['created_at','full_text','entities','extended_entities']]

# load data B: from csv, !! csv have some problems
# csv_fname = './data/to_trump_tweets_chunk_1.csv'
# to_trump_df = pd.read_csv(csv_fname,lineterminator='\n') # ,lineterminator='\n' is necessary 

# text preprocessing
to_trump_df['re_text'] = to_trump_df.full_text.apply(preprocess_tweet)
# to_trump_df['re_text'] = to_trump_df.full_text.apply(tokenize_tweet)

# check if nan
if np.sum(pd.isna(to_trump_df['re_text'])):
    print('Nan in re_text')
    
if np.sum(pd.isna(to_trump_df['full_text'])):
    print('Nan in full_text')


to_trump_tweet_list = np.array_split(to_trump_df, chunk_num)

# # debug
# print('Chunk size: ', len(to_trump_tweet_list))
# print('Total tweets in chunk: ', np.sum([len(chunk) for chunk in to_trump_tweet_list]))
# print('Total tweets in original: ', len(to_trump_df))


pool = multiprocessing.Pool(processes=cpuNum) 
tweets_emotion_list = pool.map(emotion_analysis, (to_trump_tweet for to_trump_tweet in to_trump_tweet_list))

tweets_emotion_list_label, tweets_emotion_list_prob = map(list,zip(*tweets_emotion_list))

tweets_emotion_label = pd.concat(tweets_emotion_list_label,ignore_index=True)
tweets_emotion_prob = pd.concat(tweets_emotion_list_prob,ignore_index=True)

tweets_emotion_label.to_csv('./res/re-reservoir_sampling_hydrated_100K_emo_label_p.csv')
tweets_emotion_prob.to_csv('./res/re-reservoir_sampling_hydrated_100K_emo_prob_p.csv')
to_trump_df.to_csv('./res/re-reservoir_sampling_hydrated_100K_p.csv')