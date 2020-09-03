#!/usr/bin/env bash


if [[ "$source_dir" == "" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    source ${DIR}/../../globals.sh
fi


if [[ "$CONDA_PREFIX" != *"/hyperwords"  ]]; then
    source activate wordrep
fi

###############################################################
#Evaluation
###############################################################
#
#    Usage: ./evaluate.sh <MODEL>  <model_dir> <config_file> <output_dir>
#
#    The config file must specify the postprocessing options.
#
###############################################################


if [ "$#" -ne 4 ]; then
    echo "Usage: ./evaluate.sh <MODEL>  <model_dir>  <config_file> <output_dir> "
    echo "Available models: ppmi / SVD / SGNS / GLOVE"
    echo ""
    exit
fi

MODEL="$1"
model_dir="$2"
config_file="$3"
output_dir="$4"

echo "Starting evaluation for "$MODEL" and config "${config_file}"...."
echo ""

repr=`echo $MODEL |  tr '[:upper:]' '[:lower:]'`
if [[ $repr == "ppmi" ]]
then
    repr="pmi"
fi



#Run
POST_OPTS=`eval "echo $(python $configs_dir/config_loader.py ${config_file} "post" "CMDOPTS")"`


echo "Evaluating on Word Similarity..."
echo "python $hyperwords_dir/hyperwords/ws_eval.py  $POST_OPTS $MODEL $model_dir/$repr "
eval_command="python $hyperwords_dir/hyperwords/ws_eval.py  $POST_OPTS $MODEL $model_dir/$repr "
MODEL=`echo $MODEL |  tr '[:upper:]' '[:lower:]'`
for test_set in $hyperwords_dir/testsets/ws/*.txt; do
    test=`echo $test_set |  sed -n 's/.*testsets\/\(.*\.txt\)/\1/p' `
    outcome=`$eval_command $test_set`
    only_value=`echo $outcome | awk '{print $NF}'`
    model_id=`eval "echo $(python ${configs_dir}/config_loader.py ${config_file} $MODEL "STRID")"`
    echo $model_id";"$test";"$only_value
done

