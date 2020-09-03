"""
    Find correlation and p-value between AoA and some index.
    Input: <csv file with columns: word, index, AoA > <model-id>
    Output: csv file with: model-id AoA-fname idx-fname corr pvalue

"""
import sys
import os, inspect
from os.path import join
import pandas as pd
import numpy as np
import re
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
#Add source folder to the path:
SCRIPT_FOLDER = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
MAIN_FOLDER = join(SCRIPT_FOLDER, os.pardir)
if MAIN_FOLDER not in sys.path:
    sys.path.insert(0, MAIN_FOLDER)
from configs.model_id_opts import strid_to_opts



def find_model_id(datafile):
    if "svd" in datafile:
        match=re.search("svd.*/.*/eval",datafile)
        strid=match.group(0)[4:-5]
    elif "sgns" in datafile:
        match=re.search("sgns.*/eval",datafile)
        strid=match.group(0)[5:-5]
    else:
        raise Exception("I don't know how to find a model strid in %s"%datafile)
    strid = re.sub("/","_",strid)

    return strid

def write_correlation(model, datafile, outputpath, pearsonr, pearson_pval, spearman_rho, spearman_pval, rsq_model, rsq_freq, rsq_m_f, rsq_f_m, rsq_m_f_int, rsq_f_m_int, corr_freq_index, corr_freq_pval ):


    #separate modelid from datafile (or load config?)
    # model_strid = find_model_id(datafile)
    # ks,vs = strid_to_opts(model_strid)

    header="model;aoa_idx_file;pearsonr;pearsonr_pval;spearmanrho;spearman_pval;rsquared_model;rsquared_freq;rsquared_model_freq;rsquared_freq_model;rsquared_model_freq_interaction;rsquared_freq_model_interaction;corr_freq_index;corr_freq_pval\n"
    line=";".join([str(x) for x in [model, os.path.basename(datafile), pearsonr, pearson_pval, spearman_rho, spearman_pval, rsq_model, rsq_freq, rsq_m_f, rsq_f_m, rsq_m_f_int, rsq_f_m_int, corr_freq_index, corr_freq_pval]])

    outfile=os.path.join(outputpath, "stats_"+os.path.basename(datafile))

    with open(outfile, "w") as fh:
        fh.write(header)
        fh.write(line+"\n")

    print("Correlations saved at:\n %s\n"%outfile)

def write_lr(datafile, outputpath, results_lr, results_lr_freq, results_f_m, results_m_f, results_f_m_int, results_m_f_int, vif):

    ## Linear regression
    outfile=os.path.join(outputpath, "lr_"+os.path.basename(datafile).replace("csv","txt"))
    with open(outfile, "w") as fh:
        fh.write("Linear Regression AoA ~ index")
        fh.write(str(results_lr.summary()))
        fh.write("\n\n")

        fh.write("\nLinear Regression AoA ~ Log(freq)")
        fh.write(str(results_lr_freq.summary()))
        fh.write("\n\n")

        fh.write("\nLinear Regression AoA ~ log(freq) + index")
        fh.write(str(results_f_m.summary()))
        fh.write("\n\n")

        fh.write("\nLinear Regression AoA ~ index + log(freq)")
        fh.write(str(results_m_f.summary()))
        fh.write("\n\n")

        fh.write("\nLinear Regression AoA ~ log(freq) + index + index*log(freq)")
        fh.write(str(results_f_m_int.summary()))
        fh.write("\n\n")

        fh.write("\nLinear Regression AoA ~ index + log(freq) + index*log(freq)")
        fh.write(str(results_m_f_int.summary()))
        fh.write("\n\n")

        fh.write("\nVariance inflation for index and log(freq)")
        fh.write("(1: not correlated; 1 to 5: moderately correlated; >5 highly correlated")
        fh.write(str(vif))
        fh.write("\n\n")

    print("Linear Regression results saved at:\n %s\n"%outfile)

def main(model_id, datafile, outputpath):

    #Read in data with AoA and computed index
    df = pd.read_csv(datafile, sep=";")
    X=df["index"]
    Y=df["aoa"]

    #Read in frequency data and merge
    df["logfreq"] = np.log(df.freq)

    #Compute stats
    pearsonr, pearson_pval = stats.pearsonr(X, Y)
    spearman_rho, spearman_pval = stats.spearmanr(X, Y)
    corr_freq_index, corr_freq_pval = stats.pearsonr(X, df["logfreq"])

    #Regress modelsonly (eq_1)
    results_lr = smf.ols('aoa ~ index', data=df).fit() #with this notation there is no need to add a constant
    rsq_model=results_lr.rsquared
    #results_lr_log = smf.ols('aoa ~ np.log(index+1)', data=df).fit()
    #rsqlog=results_lr_log.rsquared

    #Regress log frequency only (eq_3)
    results_lr_freq = smf.ols('aoa ~ np.log(freq)', data=df).fit() #with this notation there is no need to add a constant
    rsq_freq=results_lr_freq.rsquared

    #Regress model then frequency (eq_2)
    results_m_f = smf.ols('aoa ~ index + np.log(freq) ', data=df).fit()
    rsq_m_f = results_m_f.rsquared

    #Regress frequency then model (eq_4)
    results_f_m = smf.ols('aoa ~ np.log(freq) + index', data=df).fit()
    rsq_f_m = results_f_m.rsquared

    ## adding INTERACTION ##
    #Regress model then frequency (eq_2)
    results_m_f_int = smf.ols('aoa ~ index + np.log(freq) + index*np.log(freq)', data=df).fit()
    rsq_m_f_int = results_m_f_int.rsquared

    #Regress frequency then model (eq_4)
    results_f_m_int = smf.ols('aoa ~ np.log(freq) + index + index*np.log(freq)', data=df).fit()
    rsq_f_m_int = results_f_m_int.rsquared

    #Checking for multicollinearity: VARIANCE INFLATION FACTOR
    pred1=np.array(df.index)
    pred2=np.log(df.freq)
    ck = np.column_stack([pred1, pred2])
    vif = [variance_inflation_factor(ck, i) for i in range(ck.shape[1])]

    #Write output
    write_correlation(model_id, datafile, outputpath, pearsonr, pearson_pval, spearman_rho, spearman_pval, rsq_model, rsq_freq, rsq_m_f, rsq_f_m, rsq_m_f_int, rsq_f_m_int, corr_freq_index, corr_freq_pval)
    write_lr(datafile, outputpath, results_lr, results_lr_freq, results_f_m, results_m_f, results_f_m_int, results_m_f_int, vif)



if __name__ == "__main__":
    args=sys.argv[1:]
    if len(args) != 3:
        print("Usage: all_stats.py <model_id> <merged_aoa_idx_file> <output_path>")
        exit(-1)
    main(*args)

# Example
#args:
# svd /home/rgalhama/Data_Research/results_wordrep/eng_0_60/svd_thr_100_win_5_dim_500_neg_1/post_eig_0_neg_1/evaluation_aoa_cdi_0.5_understands_nouns//merged_indegree_train_th0.70aoa_wordbank_eng_understands_prop0.5_nouns_clean_means.csv /home/rgalhama/Data_Research/results_wordrep/eng_0_60/svd_thr_100_win_5_dim_500_neg_1/post_eig_0_neg_1/evaluation_aoa_cdi_0.5_understands_nouns
