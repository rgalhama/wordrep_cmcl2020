import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from evaluation.indexs_from_reprs.ReprWrapper import ReprWrapper



def get_all_associates(cue, data):
    subdata=data[data.cue.str.lower() == cue.lower()]
    associates = {}
    associates["R1"] = list(subdata.R1.str.lower())
    associates["R2"] = list(subdata.R2.str.lower())
    associates["R3"] = list(subdata.R3.str.lower())
    associates["all"] = []
    associates["all"].extend(associates["R1"])
    associates["all"].extend(associates["R2"])
    associates["all"].extend(associates["R3"])

    return associates

def precision_and_recall(cuewords):
    # #For each different cue, get the topmost neighbours
    topmostdict={}
    print("Computing neighbours...")
    for cue in cuewords:
        neighbours = representation.closest(cue, n+1) #+1 because this includes the word itself
        topmostdict[cue] = neighbours
    print("Computing neighbours completed.")
    precision, recall = 0, 0
    for i, cue in enumerate(cuewords):
        associates_dict = get_all_associates(cue, swow)
        associates = set(associates_dict["all"])

        #Intersection between neighbours and associates
        nrelevant = len(associates)
        neighbours = [neighbour.lower() for cosine, neighbour in topmostdict[cue]]
        intersects = len(associates.intersection(neighbours))
        nretrieved = n #I'm not sure if this should be n, since n is fixed! Maybe it should be the rank of the furthest neighbour

        precision_cue = intersects / (nretrieved*1.0)
        recall_cue = intersects / (nrelevant*1.0)

        #f1:
        precision += (precision_cue / len(cuewords)*1.)
        recall += (recall_cue / len(cuewords)*1.)

        if i%100 == 0:
            print("{}: Actual precision: {} Actual recall: {}".format(i, precision, recall))
    print("Mean precision over all cues: ", precision)
    print("Mean recall over all cues: ", recall)


def get_precicion_and_recall_from_cues(cues, representation, swowdata, n=-1):

    precision, recall = {}, {}
    for cue in cues:
        #Get associates
        associates_dict=get_all_associates(cue, swowdata)
        associates = set(associates_dict["all"])


        nrelevant = len(associates)
        if n < 0:
            ntopmost = len(associates) + 1
        else:
            ntopmost = n + 1
        neighbours = representation.closest(cue, ntopmost) #+1 because this includes the word itself
        neighbours = [neighbour.lower() for cosine, neighbour in neighbours]
        intersects = len(associates.intersection(neighbours))
        nretrieved = nrelevant

        precision[cue] = intersects / (nretrieved*1.0)
        recall[cue] = intersects / (nrelevant*1.0)

    return precision, recall



if __name__ == "__main__":

    whichmodel="best"
    if len(sys.argv) > 1:
        whichmodel=sys.argv[1]

    #Load Model
    models_path="/home/rgalhama/Data_Research/results_wordrep//eng_0_60"

    #Best and Worst model can be determined in study 6
    if whichmodel == "best":
       representation="sgns"
       repr_path=models_path +"/sgns_thr_10_win_1_negative_15_pow_1_size_100/"
    elif whichmodel == "worst":
        representation="svd"
        repr_path=models_path +"/svd_thr_10_win_4_dim_100_neg_15/"
    else:
        raise Exception("Unknown model %s. Use \"best\" or \"worse\""%whichmodel)

    representation = ReprWrapper(representation, repr_path).representation

    #Load Small World of Worlds data
    pos="nouns"
    swow=pd.read_csv("swow_known_{}.txt".format(pos), header=None, names=["cue", "R1", "R2", "R3"])

    #Load AoA produces, nouns and verbs
    if pos == "nouns":
        aoaf_nouns="/home/rgalhama/Research/WordRep/WordRep_alhama/03-data/AoA/wordbank/data_cogsci/aoa_wordbank_eng_produces_prop0.5_nouns_clean_means.csv"
        aoa=pd.read_csv(aoaf_nouns, sep=";")
    else:
        aoaf_verbs="/home/rgalhama/Research/WordRep/WordRep_alhama/03-data/AoA/wordbank/data_cogsci/aoa_wordbank_eng_produces_prop0.5_verbs_clean_means.csv"
        aoa=pd.read_csv(aoaf_verbs, sep=";")
#    aoaall=aoan.append(aoav)

    #Filter words in swow to make sure they have been in the training data of the model (in case frequency threshold is different for model)
    cuewords=list(set(swow.cue).intersection(set(representation.wi.keys())))
    print("Number of different cues:" ,len(cuewords))
    #


    #There are many possible ways to evaluate this!!!

    #Ev 1. Precision and Recall
    #precision_and_recall(cuewords)


    #Ev 2. Rank correlation between overlaps and AoA
    corrs, scores=[], []
    #Number of neighbours to retrieve
    xs=list(range(0,201, 10))

    for n in xs:
        precision, recall = get_precicion_and_recall_from_cues(cuewords, representation, swow, n=n)
        dfrecall=pd.DataFrame(recall.items(), columns=['cue', 'score'])
        dfrecall=dfrecall.merge(aoa, left_on="cue", right_on="uni_lemma", how="inner")
        scores.append(list(dfrecall.score))

        #By default, spearman is the correlation between ranks of the two variables, computed with method="average"
        corrs.append(dfrecall.score.corr(dfrecall.aoa, method="spearman"))
        print("n:",n,"spearman: ",corrs[-1], " mean score:",np.mean(scores[-1]))

        #Graphs using the "average" method are unintuitive though (many points collapse); "first" is more readable
        dfrecall["rank_aoa"]=dfrecall["aoa"].rank(ascending=True, method="first")
        dfrecall["rank_score"]=dfrecall["score"].rank(ascending=True, method="first")

        #x=list(range(dfrecall.rank_aoa.min(), dfrecall.rank_aoa.max()))
        #u = smoothfit.fit1d(dfrecall.rank_aoa, dfrecall.rank_score, dfrecall.rank_aoa.min(), dfrecall.rank_aoa.max(), 1000, degree=1, lmbda=1.0e-6)
        #vals = [u(xx) for xx in range(dfrecall.rank_aoa.min(), dfrecall.rank_aoa.max()+1)]


        if True:#n == 20:
            #maybe better sth equivalent to R's loess instead of regplot?
            sns.regplot(x="rank_aoa", y="rank_score", data=dfrecall, color="black")
            plt.xlabel("Ranked AoA", fontsize=14)
            plt.ylabel("Ranked score", fontsize=14)
            spearman, pval =spearmanr(dfrecall.score, dfrecall.aoa)
            title =  "Spearman correlation: %.3f"
            if pval < 0.0001:
                title += " (p-value < 0.001)"
            plt.title(title%corrs[-1])
            print("p-val:", spearman, pval)
            plt.savefig("regplot_ranks_top%i.png"%n)
            #For nouns, the correlation gets better and better: as more neighbours are considered, associates reflect better the AoA
            #For verbs, however, the neighbours don't reflect AoA that well
            plt.clf()
            #sns.distplot(dfrecall.score, kde=False)
            sns.swarmplot(dfrecall.score)
            plt.xlim(-0.1,1.1)
            plt.savefig("scores_top%i.png"%n)
            plt.clf()

    plt.clf()
    plt.plot(xs, corrs, color="black", lw="4")
    plt.xlabel("Number of retrieved neighbours", fontsize=14)
    plt.ylabel("Spearman correlation", fontsize=14)
    plt.savefig("spearmanr.png")

    #Save data
    spdf=pd.DataFrame.from_records(zip(xs,corrs), columns=["retrieved_neighbours", "spearman"])
    spdf.to_csv("%s_model_spearman_corrs.csv"%whichmodel)

    #Ev 3. Check if this gets better over development


