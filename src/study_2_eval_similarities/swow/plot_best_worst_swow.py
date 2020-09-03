import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    bdf=pd.read_csv("best_model_study1/best_model_spearman_corrs.csv")
    wdf=pd.read_csv("worst_model_study1/worst_model_spearman_corrs.csv")
    plt.plot(bdf.retrieved_neighbours, bdf.spearman, label="Best model (ND)", lw=3, color="black")
    plt.plot(wdf.retrieved_neighbours, wdf.spearman, label="Worst model (ND)", lw=3, ls="--", color="black")
    plt.legend(fontsize=14)
    plt.xlabel("Number of neighbours retrieved", fontsize=14)
    plt.ylabel("Rank correlation", fontsize=14)
    plt.savefig("spearman_comparison_models.png")


