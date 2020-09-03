from os.path import join
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 15
import seaborn as sns
import pandas as pd

def load_all_data(resultspath):
    fname="correlations_%s_%s_%s.csv"
    models=["sgns", "svd"]
    measures=["produces"] #, "understands"
    categories=["nouns", "verbs"]

    dfs=[]

    for model in models:
        for measure in measures:
            for category in categories:
                fn=fname%(model, measure, category)
                df=pd.read_csv(join(resultspath, fn), sep=";")
                dfs.append(df.copy())
                df=None
    return tuple(dfs)

def best_model(df):
    # idxmax=df.loc[df['pearsonr'].idxmax()]
    df['absr']=df['pearsonr'].abs()
    return df[df['absr']==df['absr'].max()]

def worse_model(df):
    # idxmax=df.loc[df['pearsonr'].idxmax()]
    df['absr']=df['pearsonr'].abs()
    return df[df['absr']==df['absr'].min()]

def plot_correlations(df1, df2, labeldf1, labeldf2, title=""):
    bins=20
    plt.axvline(x=0, color="grey", alpha=0.3,  zorder=-9, ls='--')
    ax=sns.distplot( df1["pearsonr"], label=labeldf1, color="blue", bins=bins)
    for i, bar in enumerate(ax.patches):
        bar.set_hatch(".")
    ax=sns.distplot( df2["pearsonr"], label=labeldf2, color="orange", bins=bins)
    plt.legend()
    plt.xlim(-.6,.6)
    # plt.title(title)
    plt.ylabel("Number of models")
    plt.xlabel("Correlation") #$r$
    plt.savefig(title+"_correlationshist"+".png")
    plt.clf()


def plot_winsize_r(dfnouns, dfverbs, title="pearson's r, sgns"):
    bins=25
    #sns.distplot( dfverbs.groupby(["pearsonr"], label="verbs", color="#ff796c", bins=bins)
    # sns.violinplot(x="win",y="pearsonr",data=dfnouns,palette='Set1', label="nouns")
    plt.clf()
    sns.stripplot(x="win",y="pearsonr",data=dfnouns,palette='Set1')
    plt.title(title+" Nouns")
    plt.savefig("sgns_nouns_win.png")
    plt.clf()
    # sns.violinplot(x="win",y="pearsonr",data=dfverbs,palette='Set1', label="verbs")
    sns.stripplot(x="win",y="pearsonr",data=dfverbs,palette='Set1')
    plt.title(title+" Verbs")
    plt.savefig("sgns_verbs_win.png")
    plt.clf()
    sns.regplot(x="win", y="pearsonr", data=dfverbs, color="#ff796c")
    plt.title("SGNS, Verbs")
    plt.savefig("sgns_decreasing_win_verbs.png")
    plt.clf()
    sns.regplot(x="win", y="pearsonr", data=dfnouns, color="#ff796c")
    plt.xlim(0.5,10.5)
    plt.xlabel("window size")
    plt.ylabel("correlation")
    plt.title("SGNS, Nouns")
    plt.savefig("sgns_decreasing_win_nouns.png")
    plt.clf()


def main (resultspath):

    #1. Load data
    names = ["sgns_produces_nouns", "sgns_produces_verbs", "svd_produces_nouns", "svd_produces_verbs"]
    alldfs = load_all_data(resultspath)

    #Remove NaNs (they result from zero variance datasets).
    alldata={}
    for i,df in enumerate(alldfs):
        newdf=df.dropna()
        alldata[names[i]]=newdf

    #2. Find best model params
    for name,df in alldata.items():
        bdf=best_model(df)
        bdf.to_csv(join(resultspath, "best_model_%s.csv"%name), sep=";")
        # Best model for SGNS: same parameters for nouns and verbs
        #Positive correlation.
        # SVD: different parameters for nouns and verbs, and they do not even overlap. Both are negative.


    #3. Histograms to see trends in sign of correlations
    plt.axvline(x=0, color="grey", alpha=0.3,  zorder=-9, ls='--')
    plt.legend()
    #SGNS
    plot_correlations(alldata["sgns_produces_nouns"], alldata["sgns_produces_verbs"], "nouns", "verbs", title="Context-predicting")
    #SVD
    plot_correlations(alldata["svd_produces_nouns"], alldata["svd_produces_verbs"], "nouns", "verbs", title="Context-counting")
    #Verbs have more negatives be more negative
    #Nouns (SGNS vs SVD)
    plot_correlations(alldata["sgns_produces_nouns"], alldata["svd_produces_nouns"],"SGNS", "SVD", title="Nouns")

    #4. SGNS -- window size (to see if sign depends on it)
    #there are probably stats to compute this (e.g. correlation between pearson's r and window size?)
    sgns_nouns=alldata["sgns_produces_nouns"]
    sgns_verbs=alldata["sgns_produces_verbs"]
    plot_winsize_r(sgns_nouns, sgns_verbs, title="SGNS")
    #both plots decrease with window size, but it may not be a tendency to be negative but just to be less correlated

    #5. SGNS -- window size when fixing params
    for pos in ("nouns", "verbs"):
        df=alldata["sgns_produces_{}".format(pos)]
        bdf=best_model(df)
        groupedcols="model;del;dyn;pos;sub;thr;alpha;iters;negative;pow;size;eig;neg;w+c;similarity_threshold".split(";")
        selected=df.merge(bdf, on=groupedcols, how="inner")
        selected=selected[selected["dyn"]==False]
        # grouped=sgns_nouns.groupby(groupedcols)
        fig= plt.figure(figsize=(4.50,2.50))
        sns.barplot(x="win_x",y="pearsonr_x",data=selected, color="grey")#  color="#ff796c")
        plt.xlabel("Window size")
        plt.ylabel("Correlation")
        #plt.title("SGNS, fixed parameters (best model)")
        plt.tight_layout()
        plt.savefig("sgns_{}_win_best_only.png".format(pos))
        plt.clf()


if __name__ == "__main__":

    resultspath="../results/"
    main(resultspath)
