'''
USC CSCI 626 Course Project
Sentiment analysis of ‘trump tweets’
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
import json

import pandas as pd
import numpy as np
import preprocessor as p

from emotion_predictor import EmotionPredictor

def emotion_analysis(tweets_text_list):

    model = EmotionPredictor(classification='ekman', setting='mc')

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

with open('./data/since-20190927-processed.json') as f:
    jsondata = json.load(f)

normalized_json = pd.io.json.json_normalize(jsondata)

to_trump_df = pd.DataFrame(normalized_json)


# text preprocessing
to_trump_df['re_text'] = to_trump_df.text.apply(preprocess_tweet)
# to_trump_df['re_text'] = to_trump_df.full_text.apply(tokenize_tweet)

# check if nan
if np.sum(pd.isna(to_trump_df['re_text'])):
    print('Nan in re_text')
    
if np.sum(pd.isna(to_trump_df['text'])):
    print('Nan in text')

tweets_text_list = to_trump_df.re_text.tolist()

tweets_emotion_label, tweets_emotion_prob = emotion_analysis(tweets_text_list)

tweets_emotion_label.to_csv('./res/trump_tweets_emo_label.csv')
tweets_emotion_prob.to_csv('./res/trump_tweets_emo_prob.csv')
to_trump_df.to_csv('./res/trump_tweets.csv')    