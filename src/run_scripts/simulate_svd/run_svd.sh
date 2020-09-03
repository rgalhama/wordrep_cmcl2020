#!/usr/bin/env bash


if [[ "$source_dir" == "" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    source ${DIR}/../../globals.sh
fi

if [[ "$CONDA_PREFIX" != *"/wordrep" ]]; then
    source activate wordrep
fi

MODEL="SVD"

############################################################################################
#
#    Create representations,  with PPMI+SVD
#        Usage: ./run_study_svd [config_file]
#    If the config_file is not provided, the default one is used.
#
############################################################################################

if [[ -z "$1" ]]
then
    config_file=$configs_dir'/config.json'
    echo "Config file not provided. "
    echo "    Usage: ./run_create_svd [config_file] "

    read -p "Do you want to continue with the default config file? <y/N> " prompt
    if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]
    then
        echo "Running default configuration... ($config_file)"
    else
        exit 0
    fi
else
    config_file="${1}"
fi

##############################################
#Initialize parameters and environment vars  #
##############################################
source $source_dir/run_scripts/__prepare_env.sh $MODEL $config_file

##################################################################
#Create model
##################################################################

# Save configuration in representation dir
cp $config_file $output_dir

# Count co-occs
${source_dir}/run_scripts/simulate_cooccurrences/create_counts.sh $config_file  $CORPUS $output_dir

#Create PPMI
${source_dir}/run_scripts/simulate_ppmi/create_ppmi.sh $config_file $CORPUS $output_dir

#Create SVD
${source_dir}/run_scripts/simulate_svd/create_svd.sh $config_file $CORPUS $output_dir
cp $output_dir/pmi.words.vocab $output_dir/svd.words.vocab
cp $output_dir/pmi.contexts.vocab $output_dir/svd.contexts.vocab

##################################################################
#Evaluate
##################################################################
#cd ..
#MODEL=`echo $MODEL |  tr '[:lower:]' '[:upper:]'`
#./evaluate.sh $MODEL $output_dir $config_file $eval_dir

#Deactivate virtual environment
source deactivate
