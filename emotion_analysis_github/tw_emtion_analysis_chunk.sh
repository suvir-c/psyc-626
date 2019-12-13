#!/bin/bash

for str_fname in ./data/to_trump_chunk/tweets_chunk_*.csv; do

	echo $str_fname


    qsub tw_emtion_analysis_chunk.pbs ${str_fname}
done


