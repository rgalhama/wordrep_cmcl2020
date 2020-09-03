import sys, os
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
from configs.config_loader import load_config, opts2record



data_fname="merged_indegree_train_th%.2faoa_wordbank_eng_understands_prop0.5_nouns_clean_means.csv"

header_svd="win;thr;"
header_sgns="dyn;thr"

def write_output(model_type, config, datafile, similarity_threshold, pearsonr, pearson_pval, outputpath):

    params_model=load_config(config)
    header, record=opts2record(params_model["counts"],params_model[model_type], params_model["post"])

    header="model;"+header
    record=model_type+";"+record

    header+="similarity_threshold;"
    record+=similarity_threshold+";"

    header+="pearsonr;pearson_pval"
    record+="{0:.4f};".format(pearsonr)
    record+="{0:.4f}".format(pearson_pval)


    outfile=os.path.join(outputpath, "params_corr_"+os.path.basename(datafile))
    with open(outfile, "w") as fh:
        fh.write(header+"\n")
        fh.write(record+"\n")

    print("Correlation saved at:\n %s\n"%outfile)


def main(model_type, config, similarity_th, datafile, outputpath):
    #Read in data with AoA and computed index
    df = pd.read_csv(datafile, sep=";")
    X=df["index"]
    Y=df["aoa"]

    #Read in frequency data and merge
    df["logfreq"] = np.log(df.freq)

    #Compute stats
    pearsonr, pearson_pval = stats.pearsonr(X, Y)

    #Write output
    write_output(model_type, config, datafile, similarity_th, pearsonr, pearson_pval, outputpath)

if __name__ == "__main__":
    args=sys.argv[1:]
    if len(args) != 5:
        print("Usage: corr_index.py <model_type> <config> <similarity_th> <datafile> <output_path>")
        exit(-1)
    main(*args)

#svd
#/home/rgalhama/Data_Research/results_wordrep/eng_0_60/svd_thr_100_win_5_dim_500_neg_1/post_eig_0_neg_1/
#0.7
#/home/rgalhama/Data_Research/results_wordrep/eng_0_60/svd_thr_100_win_5_dim_500_neg_1/post_eig_0_neg_1/evaluation_aoa_cdi_0.5_understands_nouns