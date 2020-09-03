from evaluation.indexs_from_reprs.ReprWrapper import ReprWrapper
import pandas as pd

class EvalSwow():

    def __init__(self, reprtype, modelpath, pos="nouns"):
        self.reprtype=reprtype
        assert(self.reprtype in ["svd", "sgns"])
        self.modelpath=modelpath
        self.representation = self.get_representation()
        self.swow = self.load_swow(pos)

    def get_representation(self):
        return ReprWrapper(self.reprtype, self.modelpath).representation

    def load_aoa(self, aoapath):
        return pd.read_csv(aoapath, sep=";")

    def load_swow(self, pos="nouns"):
        return pd.read_csv("swow_known_{}.txt".format(pos), header=None, names=["cue", "R1", "R2", "R3"])

    def get_cues(self):
        return list(set(self.swow.cue).intersection(set(self.representation.wi.keys())))

    def get_all_associates(self, cue):

        subdata=self.swow[self.swow.cue.str.lower() == cue.lower()]
        associates = {}
        associates["all"] = []
        for col in ["R1", "R2", "R3"]:
            associates[col] = list(subdata[col].str.lower())
            associates["all"].extend(associates[col])

        return associates

    def get_precision_and_recall_from_cues(self, cues, n):

        precision, recall = {}, {}
        for cue in cues:
            #Get associates
            associates_dict=self.get_all_associates(cue)
            associates = set(associates_dict["all"])


            nrelevant = len(associates)
            if n < 0:
                ntopmost = len(associates) + 1
            else:
                ntopmost = n + 1
            neighbours = self.representation.closest(cue, ntopmost) #+1 because this includes the word itself
            neighbours = [neighbour.lower() for cosine, neighbour in neighbours]
            intersects = len(associates.intersection(neighbours))
            nretrieved = nrelevant #todo think about this one

            precision[cue] = intersects / (nretrieved*1.0)
            recall[cue] = intersects / (nrelevant*1.0)

        return precision, recall

    def get_spearmanr(self, aoapath, nneighbours):
        cuewords=self.get_cues()
        precision, recall = self.get_precision_and_recall_from_cues(cuewords, n=nneighbours)
        dfrecall=pd.DataFrame(recall.items(), columns=['cue', 'score'])
        dfrecall=dfrecall.merge(self.load_aoa(aoapath), left_on="cue", right_on="uni_lemma", how="inner")

        #By default, spearman is the correlation between ranks of the two variables, computed with method="average"
        corr = dfrecall.score.corr(dfrecall.aoa, method="spearman")
        return corr
    
if __name__ == "__main__":
    #Example
    aoaf_nouns="/home/rgalhama/Research/WordRep/WordRep_alhama/03-data/AoA/wordbank/data_cogsci/aoa_wordbank_eng_produces_prop0.5_nouns_clean_means.csv"
    repr="sgns"
    models_path="/home/rgalhama/Data_Research/results_wordrep//eng_0_60"
    repr_path=models_path +"/sgns_thr_10_win_1_negative_15_pow_1_size_100/"

    eval=EvalSwow(repr, repr_path, pos="nouns")
    corr = eval.get_spearmanr(aoaf_nouns, 50)
    print(corr)
