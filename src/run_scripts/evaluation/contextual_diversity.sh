#!/usr/bin/env bash

#Get contextual diversity (as in Hills et al. 2010): number of types a word co-occurs with (indegree)
#Trick: use the co-occurrences gathered with sgns/svd (before algorithsm are applied)


data_dir=`echo ~/Data_Research/results_wordrep/eng_0_60/`
thr=10

wins=(1 2 5)

#Compute contextual diversity
for win in "${wins[@]}"; do
    cd ${data_dir}/sgns_thr_${thr}_win_${win}_negative_1_pow_1_size_500/
    cat counts | sed "s/^[ \t]*//" | cut -f2 -d" " | sort | uniq -c | sed "s/^[ \t]*//;s/ /;/g" > contextual_diversity_win${win}.txt
    mv contextual_diversity_win${win}.txt ${data_dir}
done

#Correlate with AoA