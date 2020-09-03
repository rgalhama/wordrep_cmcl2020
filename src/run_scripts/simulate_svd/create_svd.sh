#!/usr/bin/env bash

if [[ "$source_dir" == "" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    source ${DIR}/../../globals.sh
fi

usageline="Usage: ./create_svd.sh config_file corpus_file output_dir"
if [ "$#" -ne 3 ]; then
    echo $usageline
    exit
fi

if [[ "$CONDA_PREFIX" != *"/wordrep"  ]]; then
    source activate wordrep
fi


#Parse params
config_file=$1
CORPUS=$2
output_dir=$3

POST_OPTS=`eval "echo $(python $configs_dir/config_loader.py ${config_file} 'svd' 'CMDOPTS')"`


#Create SVD from pmi
echo "Computing SVD ..."
python $hyperwords_dir/hyperwords/pmi2svd.py $POST_OPTS $output_dir/pmi $output_dir/svd
echo "pmi2svd.py $POST_OPTS $output_dir/pmi $output_dir/svd"
cp $output_dir/pmi.words.vocab $output_dir/svd.words
cp $output_dir/pmi.contexts.vocab $output_dir/svd.contexts
python $hyperwords_dir/hyperwords/text2numpy.py $output_dir/svd.words
python $hyperwords_dir/hyperwords/text2numpy.py $output_dir/svd.contexts
echo "Done. Find the SVD results at $output_dir"



# Save the embeddings in the textual format
#    Usage:
#        svd2text.py [options] <svd_path> <output_path>
#
#    Options:
#        --w+c        Use ensemble of word and context vectors
#        --eig NUM    Weighted exponent of the eigenvalue matrix [default: 0.5]
#python hyperwords/svd2text.py $SVD2TEXT_OPTS $OUTPUT_DIR/svd $OUTPUT_DIR/vectors.txt


source deactivate