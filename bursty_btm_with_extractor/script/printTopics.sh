set -e

type='n'  #'n' is normal, 's' is simplified BurstyBTM
K=500   # number of topics

alpha=`echo "scale=3;50/$K"|bc`
beta=0.01
n_day=714
n_iter=1


input_dir=../sample-data/
#input_dir=extracted/
input_dir=../2m_stopRemoved/
output_dir=../output/
dwid_dir=${output_dir}doc_wids/
bdf_pt=${output_dir}biterm_dayfreq.txt
eta_dir=${output_dir}eta/
model_dir=${output_dir}model/

voca_pt=${output_dir}voca.txt


echo "================ Topic Display ============="
for day in `seq 1 $[$n_day-1]`; do
	echo "---------- day $day --------------"
	res_dir=${model_dir}k$K.day$day.type-$type
	python topicDisplay.py $voca_pt $res_dir 
done