import pandas as pd

# for date regroup
import locale
import arrow
from locale import atof
from dateutil import parser
from datetime import datetime
from datesupport import *

def estimate_daily_emo(comb_emo_cdf,emotions_list,dates,mode_flag = 'onehot',Tha = 0.5):
    for date in dates:
#         print(date)
        # emotions_list = ['Anger','Disgust','Fear','Joy','Sadness','Surprise']
        date_emotion_prob_df = comb_emo_cdf.iloc[comb_emo_cdf.groupby(['month/day']).groups[date]][emotions_list].copy()
        # date_emotion_df = date_emotion_df.reset_index()

        if mode_flag == 'threshold':
        # threshold mean
            for emo in emotions_list:
                date_emotion_prob_df[emo] = date_emotion_prob_df[emo] > Tha

            yield date_emotion_prob_df.sum()/date_emotion_prob_df.sum().sum()
        elif mode_flag == 'onehot':
        # one-hot mean
            max_in_row = date_emotion_prob_df.max(axis=1)
            for emo in emotions_list:
                date_emotion_prob_df[emo] = date_emotion_prob_df[emo] == max_in_row
            yield date_emotion_prob_df.sum()/date_emotion_prob_df.sum().sum()
        else:
        # if mode_flag == 'simple'
        # simple mean
            yield date_emotion_prob_df.mean()

senti_fnames = ['./data/to_trump_chunk_res/tweets_chunk_{}_senti.csv'.format(str(i)) for i in range(80)]

# senti_data_frame
senti_dfs = [pd.read_csv(fname, lineterminator='\n') for fname in senti_fnames]
senti_dfs = [senti_df.drop(columns=['Unnamed: 0','Unnamed: 0.1']) for senti_df in senti_dfs]
senti_cdf = pd.concat(senti_dfs,ignore_index=False)
senti_cdf = senti_cdf.reset_index()
senti_cdf = senti_cdf.drop(columns=['index'])
# rearrange the tweets into date
senti_cdf['created_date'] = pd.to_datetime(senti_cdf['created_at'])
senti_cdf['month/day'] = senti_cdf['created_date'].apply(convertUTCtoMonthDay)


# # ekman
# prob_emo_fnames = ['./data/to_trump_chunk_res/tweets_chunk_{}_ekman_prob.csv'.format(str(i)) for i in range(80)]
# label_emo_fnames = ['./data/to_trump_chunk_res/tweets_chunk_{}_ekman_label.csv'.format(str(i)) for i in range(80)]

# plutchik
prob_emo_fnames = ['./data/to_trump_chunk_res/tweets_chunk_{}_plutchik_prob.csv'.format(str(i)) for i in range(80)]
label_emo_fnames = ['./data/to_trump_chunk_res/tweets_chunk_{}_plutchik_label.csv'.format(str(i)) for i in range(80)]

prob_emo_dfs = [pd.read_csv(fname,lineterminator='\n') for fname in prob_emo_fnames]
label_emo_dfs = [pd.read_csv(fname,lineterminator='\n') for fname in label_emo_fnames]

label_emo_cdf = pd.concat(label_emo_dfs,ignore_index=False)
prob_emo_cdf = pd.concat(prob_emo_dfs,ignore_index=False)
prob_emo_cdf = prob_emo_cdf.reset_index()
label_emo_cdf = label_emo_cdf.reset_index()
label_emo_cdf = label_emo_cdf.drop(columns=['Unnamed: 0','index'])
prob_emo_cdf = prob_emo_cdf.drop(columns=['Unnamed: 0','index',"Tweet"])

comb_emo_cdf = pd.concat([senti_cdf, label_emo_cdf, prob_emo_cdf], axis=1)

# group the processed text into each day in dictionary 
emotions_list = ['Anger','Disgust','Fear','Joy','Sadness','Surprise','Trust','Anticipation']
dates = list(comb_emo_cdf.groupby(['month/day']).groups.keys())
dates_emotion = [*estimate_daily_emo(comb_emo_cdf,emotions_list,dates, mode_flag = 'onehot',Tha = 0.5)]
dates_emotion_df = pd.concat(dates_emotion,axis=1).T
dates_emotion_df['month/day'] = dates
dates_emotion_df = dates_emotion_df.set_index('month/day')

dates_emotion_df.to_csv('./data/to_trump_2M_dates_res/daily_plutchik_onehot.csv')