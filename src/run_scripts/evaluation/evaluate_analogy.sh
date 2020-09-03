#!/usr/bin/env bash


if [[ "$source_dir" == "" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    source ${DIR}/../../globals.sh
fi


if [[ "$CONDA_PREFIX" != *"/hyperwords"  ]]; then
    source activate hyperwords
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


echo "Evaluating on Analogy..."
model=`echo $MODEL |  tr '[:upper:]' '[:lower:]'`
eval_command="python $hyperwords_dir/hyperwords/analogy_eval.py  $POST_OPTS $model $model_dir/$repr "
for test_set in $hyperwords_dir/testsets/analogy/*.txt; do
    outcome=`$eval_command $test_set`
    only_value=`echo $outcome | awk '{print $NF}'`
    model_id=`eval "echo $(python ${configs_dir}/config_loader.py ${config_file} $model "STRID")"`
    test=`echo $test_set |  sed -n 's/.*testsets\/\(.*\.txt\)/\1/p' `
    echo $model_id";"$test";"$only_value
    echo ""
done

