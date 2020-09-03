import sys
import pandas as pd
from scipy import stats
from numpy import log
import matplotlib.pyplot as plt
import numpy as np
from os.path import join

def significance_stars(data):
    stars=[""]*len(data)
    alphas=[0.05, 0.01, 0.001]
    for i,datum in enumerate(data):
        for alpha in alphas:
            if datum < alpha:
                stars[i]+="*"
    return stars

#Correlate with replication of Hills et al. 2010
def main(model_f, cdiv_file):
    #Read in data with AoA and computed index
    model = pd.read_csv(model_f, sep=";", names=["uni_lemma","idx"])
    cdiv = pd.read_csv(cdiv_file, sep=";", names=["cont_div","word"])

    m_df = pd.merge(model, cdiv, how="inner", right_on="word", left_on="uni_lemma")

    X=m_df['idx']
    Y=m_df['cont_div']
    Y=log(Y)

    #Compute stats
    pearsonr, pearson_pval = stats.pearsonr(X, Y)

    print("Correlation: r=%.3f, p=%.3f"%(pearsonr,pearson_pval))

    return pearsonr, pearson_pval

def plot_corrs_models_ctxdiv(svd_r,sgns_r, svd_p, sgns_p, output_dir=""):


    fig,ax=plt.subplots()
    c={"sgns":"#761D76",  "svd":"#F3601A"}
    labels=["nouns", "verbs"]
    x=np.arange(len(labels))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13)
    width=0.3
    plt.ylabel("Correlation with contextual diversity", fontsize=16)
    plt.ylim(-1.,1.0)
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
    fig.tight_layout()

    #show bars
    rects1 = ax.bar(x - width/2, svd_r, width, label='svd', edgecolor="black", color=c["svd"], hatch="|")
    rects2 = ax.bar(x + width/2, sgns_r, width, label='skipgram', edgecolor="black", color=c["sgns"])

    #add significance stars

    stars=significance_stars(svd_p)
    for j, corr in enumerate(svd_r):
        yy=corr if corr>0 else corr - 0.09
        ax.text(j-width/2-0.04, yy, str(stars[j]), fontsize=10, color='dimgrey')

    stars=significance_stars(sgns_p)
    for j, corr in enumerate(sgns_r):
        yy=corr if corr>0 else corr - 0.09
        ax.text(j+width/2-0.04, yy, str(stars[j]), fontsize=10, color='dimgrey')

    plt.legend()
    plt.savefig(join(output_dir, "corr_index_ctxtdiv.png"))

if __name__ == "__main__":

    args=sys.argv[1:]
    # if len(args) != 3:
    #     print("Usage: corr_cont_div_aoa.py <aoa_file> <cont_div_file>")
    #     exit(-1)
    # compute_similarity_trajectory(*args)

    #Contextual Diversity
    win=1
    cdf="/home/rgalhama/Data_Research/results_wordrep/eng_0_60/contextual_diversity_win{}.txt".format(win)

    #Compare to best model:
    #sgns_thr_10_win_1_negative_1_pow_1_size_500/post_eig_1_neg_1/evaluation_aoa_cdi_0.5_produces_nouns
    modelsdir="/home/rgalhama/Data_Research/results_wordrep/eng_0_60/"
    model="sgns_thr_10_win_1_negative_1_pow_1_size_500/post_eig_1_neg_1/evaluation_aoa_cdi_0.5_%s_%s/indegree_train_th0.70.csv"
    for measure in ["produces","understands"]:
        for category in ["verbs", "nouns"]:#,"verbs"]:
            print("Correlation for %s %s"%(measure,category))
            modelf=modelsdir+model%(measure, category)
            main(modelf, cdf)