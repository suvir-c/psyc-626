import pandas as pd
import numpy as np


# load the emotion analysis results
# comb_df_fname = './data/to_trump_chunk_small_res/re-reservoir_sampling_hydrated_100K_ekman_comb.csv'
comb_df_fname = './data/to_trump_chunk_small_res/re-reservoir_sampling_hydrated_100K_plutchik_comb.csv'

comb_df = pd.read_csv(comb_df_fname,index_col=0,lineterminator='\n')

# group the processed text into each day in dictionary 
dates = list(comb_df.groupby(['month/day']).groups.keys())
print('Total number of dates: ', len(dates))

dates_pre_text = [[comb_df['pre_text'][row] for row in comb_df.groupby(['month/day']).groups[date]] for date in dates]
dates_dic = dict(zip(dates, dates_pre_text))

# check tweet list in one day
print(dates_dic['2017-05-07'])

# save the dictionary as csv file
dates_df = pd.DataFrame.from_dict(dates_dic, orient='index')
export_csv = dates_df.to_csv('dates_dic.csv')