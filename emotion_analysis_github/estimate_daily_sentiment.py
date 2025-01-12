import pandas as pd

# for date regroup
import locale
import arrow
from locale import atof
from dateutil import parser
from datetime import datetime
from datesupport import *


def estimate_daily_sent(comb_emo_cdf,sent_list,dates,sent_Tha = 0.3):
    
    comb_emo_cdf['pos_sentiment'] = comb_emo_cdf['sentiment'] > sent_Tha
    comb_emo_cdf['neg_sentiment'] = comb_emo_cdf['sentiment'] < -sent_Tha
    comb_emo_cdf['neu_sentiment'] = abs(comb_emo_cdf['sentiment']) <= sent_Tha
    
    for date in dates:
#         print(date)
        # emotions_list = ['Anger','Disgust','Fear','Joy','Sadness','Surprise']
        date_sent_prob_df = comb_emo_cdf.iloc[comb_emo_cdf.groupby(['month/day']).groups[date]][sent_list].copy()
        yield date_sent_prob_df.mean()


senti_fnames = ['./data/to_trump_chunk_res/tweets_chunk_{}_senti.csv'.format(str(i)) for i in range(80)]

# senti_data_frame
senti_dfs = [pd.read_csv(fname, lineterminator='\n') for fname in senti_fnames]
senti_dfs = [senti_df.drop(columns=['Unnamed: 0','Unnamed: 0.1','full_text','entities','extended_entities','lang','pre_text','token_text']) for senti_df in senti_dfs]
senti_cdf = pd.concat(senti_dfs,ignore_index=False)
senti_cdf = senti_cdf.reset_index()
senti_cdf = senti_cdf.drop(columns=['index'])
# rearrange the tweets into date
senti_cdf['created_date'] = pd.to_datetime(senti_cdf['created_at'])
senti_cdf['month/day'] = senti_cdf['created_date'].apply(convertUTCtoMonthDay)


sent_list = ['pos_sentiment','neg_sentiment','neu_sentiment']
dates = list(senti_cdf.groupby(['month/day']).groups.keys())
dates_sent = [*estimate_daily_sent(senti_cdf,sent_list,dates, sent_Tha = 0.001)]

dates_sent_df = pd.concat(dates_sent,axis=1).T
dates_sent_df['month/day'] = dates
dates_sent_df = dates_sent_df.set_index('month/day')

dates_sent_df.to_csv('./data/to_trump_2M_dates_res/daily_senti.csv')