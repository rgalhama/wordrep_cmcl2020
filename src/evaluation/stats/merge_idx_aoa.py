import sys, os
import pandas as pd

"""
    Merge index file with aoa file.
"""

def get_fname(idx_file, aoa_file):
    idx=os.path.basename(idx_file)
    aoa=os.path.basename(aoa_file)
    #get rid of extension (csv)
    idx =  ".".join(idx.split(".")[:-1])
    aoa =  ".".join(aoa.split(".")[:-1])
    #join into new filename
    fname = "merged_" + idx + aoa + ".csv"
    return fname

def main(idx_file, aoa_file, freq_file, output_path):

    idx_df = pd.read_csv(idx_file, sep=";", names=["word","index"])
    aoa_df = pd.read_csv(aoa_file, sep=";")
    wf_df = pd.read_csv(freq_file, sep=" ", names=["freq","word"])
    aoa_df.rename(columns={"uni_lemma":"word"}, inplace=True)
    aoa_df = aoa_df.loc[:,['word', 'aoa']]
    m_df = pd.merge(idx_df, aoa_df, how="inner", on="word")
    m_df = pd.merge(m_df, wf_df, how="left", on="word")
    m_df.to_csv(os.path.join(output_path, get_fname(idx_file, aoa_file)), sep=";")

if __name__ == "__main__":
    args=sys.argv[1:]
    if len(args) != 4:
        print("Usage: merge_idx_aoa.py <idx_file> <aoa_file> <frequency_file> <output_path>")
    else:
        idx_file, aoa_file, freq_file, output_path = args[0], args[1], args[2], args[3]
        print("Starting merge of AoA and index\n")
        print("args: \n")
        print("idx_file: %s \n"%idx_file)
        print("aoa_file: %s \n"%aoa_file)
        print("frequency_file: %s \n"%freq_file)
        print("output_path: %s \n"%output_path)
    main(*args)
