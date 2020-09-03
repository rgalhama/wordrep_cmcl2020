import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

def plot_with_category(df, title):

    fig, ax = plt.subplots()
    sns.scatterplot(x="logfreq", y="aoa", hue="lexical_class", data=df, s=200)
    ax.set_title(title)
    plt.savefig("%s_freq_aoa_category.png"%(title))

def plot_category_aoa(df, title):

    fig, ax = plt.subplots()
    sns.violinplot(x="lexical_class", y="aoa", data=df)
    ax.set_title(title)
    plt.savefig("%s_aoa_category.png"%(title))

def main(aoa_path, freq_file, plot):

    dffreq = pd.read_csv(freq_file, sep=" ", names=["freq", "word"])

    print("Correlation frequency - AoA (person r):\n")
    for measure in ["understands", "produces"]:
        df=None
        print(measure.upper())
        for category in ["nouns", "verbs"]:#, "adjectives"]:
            df_cat=pd.read_csv(aoa_path%(measure, category), sep=";")
            df_cat = pd.merge(df_cat, dffreq, left_on="uni_lemma", right_on="word", how="left")
            df_cat["logfreq"] = np.log(df_cat.freq)
            print("\n"+category)
            print(df_cat.corr())
            print(" ")
            print("p-values")
            print(df_cat.corr(method=lambda x, y: pearsonr(x, y)[1])- np.eye(3))
            print(" ")
            if df is None:
                df = df_cat
            else:
                df=df.append(df_cat)
        print("all")
        print(df.corr())
        print("\n\n")

        if plot:
            plot_with_category(df, measure)
            plot_category_aoa(df, measure)

if __name__ == "__main__":

    #Frequency file
    freq_file = "../../../../03-data/CHILDES_CDS/childes_db_extraction/eng_0_60_cds_wordcounts_stem.txt"
    #AoA file
    aoa_path = "../../../../03-data/AoA/wordbank/data_for_study_2/it1/aoa_wordbank_eng_%s_prop0.5_%s_clean_means.csv"

    plot=True
    main(aoa_path, freq_file, plot)