import sys
import pandas as pd
from scipy import stats
from numpy import log

#Correlate with replication of Hills et al. 2010
def main(aoa_f, cdiv_file):
    #Read in data with AoA and computed index
    aoa = pd.read_csv(aoa_f, sep=";")
    cdiv = pd.read_csv(cdiv_file, sep=";", names=["cont_div","word"])

    m_df = pd.merge(aoa, cdiv, how="inner", right_on="word", left_on="uni_lemma")

    X=m_df['aoa']
    Y=m_df['cont_div']
    Y=log(Y)

    #Compute stats
    pearsonr, pearson_pval = stats.pearsonr(X, Y)

    print("Correlation: r=%.3f pval=%.7f"%(pearsonr,pearson_pval))


if __name__ == "__main__":

    args=sys.argv[1:]
    # if len(args) != 3:
    #     print("Usage: corr_cont_div_aoa.py <aoa_file> <cont_div_file>")
    #     exit(-1)
    # compute_similarity_trajectory(*args)

#    Correlates logarithmic contextual diversity (as in Hills etal. 2010) with AoA
    win=1
    cdf="/home/rgalhama/Data_Research/results_wordrep/eng_0_60/contextual_diversity_win{}.txt".format(win)
    for measure in ["produces","understands"]:
        for category in ["nouns","verbs"]:
            print("Correlation for %s %s"%(measure,category))
            aoaf="/home/rgalhama/Research/WordRep/WordRep_alhama/03-data/AoA/wordbank/data_for_study_2/it1/aoa_wordbank_eng_{}_prop0.5_{}.csv".format(measure, category)
            main(aoaf, cdf)