#!/bin/bash
# run an toy example for BTM
set -e

type='n'  #'n' is normal, 's' is simplified BurstyBTM
K=500   # number of topics

alpha=`echo "scale=3;50/$K"|bc`
beta=0.01
n_day=2
n_iter=1
ix_b='n'	# 'n' is not fix, 'y' is fix

rm -rf ../output/
mkdir -p ../output/eta ../output/doc_wids ../output/model
input_dir=../sample-data/
#input_dir=extracted/
input_dir=../2m_stopRemoved2/
output_dir=../output/
dwid_dir=${output_dir}doc_wids/
bdf_pt=${output_dir}biterm_dayfreq.txt
eta_dir=${output_dir}eta/
model_dir=${output_dir}model/

voca_pt=${output_dir}voca.txt

echo "================== Index Docs =================="
python indexDocs.py $input_dir $dwid_dir $voca_pt

echo "======= Statistic Biterm Daily Frequency ======="
python bitermDayFreq.py $dwid_dir $bdf_pt

echo "======= Compute eta for Biterms == ======="
python eta.py $n_day $bdf_pt $eta_dir

echo "###CLEAN###"
cwd=$(pwd)
###cd $dwid_dir; find . -name "*.txt" -exec sed -i 's/1/2/g' "{}" \;
cd $dwid_dir; find . -type f -name "*.txt" -print0 | xargs -0 sed -i '/^[[:space:]]*$/d'
cd $cwd
###sed -i '/^[[:space:]]*$/d' 1.txt
echo "###END-CLEAN###"

## learning parameters p(z) and p(z|w)
echo "=============== Topic Learning ============="
W=`wc -l < $voca_pt`
rm -f ../src/*.o ## remove old build and rebuild code
make -C ../src
for day in `seq 1 $[$n_day-1]`; do
	echo "---------- day $day --------------"
	dwid_pt=$dwid_dir$day.txt
	eta_pt=$eta_dir$day.txt
	echo $eta_pt
	res_dir=${model_dir}k$K.day$day.type-$type
	../src/bbtm $type $K $W $alpha $beta $n_iter $eta_pt $dwid_pt $res_dir $fix_b
done

# ## output top words of each topic
echo "================ Topic Display ============="
for day in `seq 1 $[$n_day-1]`; do
	echo "---------- day $day --------------"
	res_dir=${model_dir}k$K.day$day.type-$type
	python topicDisplay.py $voca_pt $res_dir 
done
