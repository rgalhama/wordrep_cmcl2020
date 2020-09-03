import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

def load_data_freq(freq_file):
    return pd.read_csv(freq_file, sep=" ", names=["freq", "word"])

def significance_stars(data):
    stars=[""]*len(data)
    alphas=[0.05, 0.01, 0.001]
    for i,datum in enumerate(data):
        for alpha in alphas:
            if datum < alpha:
                stars[i]+="*"
    return stars


def plot_with_category(df, title):

    fig, ax = plt.subplots()
    sns.scatterplot(x="logfreq", y="index", hue="lexical_class", data=df, s=200)
    ax.set_title(title)
    plt.show()
    #plt.savefig("%s_freq_index_category.png"%(title))

def plot_category_index(df, title):

    fig, ax = plt.subplots()
    sns.violinplot(x="lexical_class", y="index", data=df)
    ax.set_title(title)
    plt.show()
#    plt.savefig("%s_index_category.png"%(title))




def compute_corr(index_path, freq_file, split):

    dffreq = load_data_freq(freq_file)

    print("Correlation frequency - index (pearson r):\n")
    for measure in ["understands", "produces"]: #Actually they are the same, this is just a sanity check
        df=None
        print(measure.upper())
        for category in ["nouns", "verbs" ]:#,  "adjectives"]:
            df_cat=pd.read_csv(index_path % (measure, category), sep=";", names=["word", "index"])
            df_cat = pd.merge(df_cat, dffreq, on="word", how="left")
            df_cat["logfreq"] = np.log(df_cat.freq)
            print("\n"+category)
            if split:
                split_freq(df_cat)
            else:
                print(df_cat.corr())
                print(" ")
                print("p-values")
                print(df_cat.corr(method=lambda x, y: pearsonr(x, y)[1])- np.eye(len(df_cat.columns)-1))

            print(" ")


            #Keep to check correlation of them all
            if df is None:
                df = df_cat
            else:
                df=df.append(df_cat)
        print("all")
        print(df.corr())
        print("\n\n")


def plot_corr_two_models_freq(index_path_svd, index_path_sgns, freq_file, split):

    measure="produces" #for this computation, measure is not relevant, but it is encoded in the path
    dffreq=load_data_freq(freq_file)
    corrs={"svd":[], "sgns":[]}
    pvals={"svd":[], "sgns":[]}
    stars={"svd":[], "sgns":[]}

    #Compute necessary corrs
    for model in ["svd","sgns"]:
        index_path=[index_path_svd, index_path_sgns][model=='sgns']
        for category in ["nouns","verbs"]:
            df_cat=pd.read_csv(index_path % (measure, category), sep=";", names=["word", "index"])
            df_cat = pd.merge(df_cat, dffreq, on="word", how="left")
            df_cat["logfreq"] = np.log(df_cat.freq)
            allcorrs=df_cat.corr()
            corrs[model].append(allcorrs.iloc[0][2])
            allpvals=df_cat.corr(method=lambda x, y: pearsonr(x, y)[1])- np.eye(len(df_cat.columns)-1)
            pvals[model].append(allpvals.iloc[0][2])
        stars[model]=significance_stars(pvals[model])

    #Plot
    fig,ax=plt.subplots()
    c={"sgns":"#761D76",  "svd":"#F3601A"}
    labels=["nouns", "verbs"]
    x=np.arange(len(labels))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13)
    width=0.3
    plt.ylabel("Correlation with log-frequency", fontsize=16)
    plt.ylim(-1.,1.0)
    plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
    fig.tight_layout()


    #show bars
    rects1 = ax.bar(x - width/2, corrs["svd"], width, label='svd', edgecolor="black", color=c["svd"], hatch="|")
    rects2 = ax.bar(x + width/2, corrs["sgns"], width, label='skipgram', edgecolor="black", color=c["sgns"])

    #add significance stars
    for j, corr in enumerate(corrs['svd']):
        yy=corr if corr>0 else corr - 0.09
        ax.text(j-width/2-0.04, yy, str(stars['svd'][j]), fontsize=10, color='dimgrey')

    for j, corr in enumerate(corrs['sgns']):
        yy=corr if corr>0 else corr - 0.09
        ax.text(j+width/2-0.04, yy, str(stars['sgns'][j]), fontsize=10, color='dimgrey')

    plt.legend()
    plt.savefig("corr_index_freq.png")

def split_freq(df):
    """ Computes correlation for high and low frequency (half split) """

    df=df.sort_values("logfreq", ascending=False)
    nrows=df.shape[0]
    middle=nrows/2
    df=df.reset_index(drop=True)
    df1=df[df.index <= middle]
    df2=df[df.index > middle]
    print("Higher freq:")
    print(df1.corr())
    print("Lower freq:")
    print(df2.corr())
    print("\n\n")

if __name__ == "__main__":

    freq_file = "../../../../03-data/CHILDES_CDS/childes_db_extraction/eng_0_60_cds_wordcounts_stem.txt"
    index_path_svd = "/home/rgalhama/Data_Research/results_wordrep/eng_0_60/svd_thr_100_win_5_dim_100_neg_1/post_eig_1_neg_1/evaluation_aoa_cdi_0.5_%s_%s/indegree_train_th0.70.csv"
    index_path_sgns = "/home/rgalhama/Data_Research/results_wordrep/eng_0_60/sgns_thr_10_win_1_negative_0_pow_1_size_100/post_eig_1_neg_1/evaluation_aoa_cdi_0.5_%s_%s/indegree_train_th0.70.csv"
    split=False
    print("SVD\n")
    compute_corr(index_path_svd, freq_file, split)
    print("SGNS\n")
    compute_corr(index_path_sgns, freq_file, split)

    #Plot
    plot_corr_two_models_freq(index_path_svd, index_path_sgns, freq_file, split)
