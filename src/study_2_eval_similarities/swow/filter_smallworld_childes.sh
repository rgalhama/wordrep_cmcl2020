#!/usr/bin/env bash


smwf=`echo ~/Data_Research/SWOW-EN.R100.csv`
swowcrf=`echo ~/Data_Research/SWOW-EN.R100_cues_responses.csv`
age="0_60"


##1) Filter words in SWOW to make sure they are in CHILDES

#Get only cues and responses swow. Also remove lines with numbers in the last step (as some appear as cues or responses), and lines that have spaces (to avoid compounds)
cat $smwf | cut -d',' -f10,11,12,13 | sed "s/\"//g" | sed '/[0-9]/d;/\ /d;'> $swowcrf
#Filter also single letters and capitalized words?

#Get list of types CHILDES
chf=`echo ~/Research/WordRep/WordRep_alhama/03-data/CHILDES_CDS/childes_db_extraction/eng_${age}_cds_wordcounts_stem.txt`
#Remove rare words
thr=10
filteredf=eng${age}_wordcounts_stem_thr${thr}.txt
awk -F' ' -v thr=${thr} '$1>thr{print $0}' $chf > $filteredf
#Get the types
cat $filteredf | cut -f2 -d" " | sed '/^\s*$/d' > childes_${age}_types.txt


##Find line numbers for each column (cue, r1, r2, r3) that have a correspondance in childes
for col in `seq 1 4`; do
    cat $swowcrf | cut -f${col} -d"," | grep -w -n -f childes_${age}_types.txt | cut -f1 -d":" |sort > nl${col}.txt
done

#Get only lines with all the associates
join nl1.txt nl2.txt | join - nl3.txt | join - nl4.txt > lines_all_in_childes.txt

#Filter these lines in cue-responses file
nl $swowcrf > swow_nl.txt
grep -w -f lines_all_in_childes.txt swow_nl.txt | cut -f2 |sort > swow_in_childes.txt

#Remove intermediate files
rm nl?.txt
rm swow_nl.txt
rm lines_all_in_childes.txt


#Count the number of word types
cat swow_in_childes.txt| tr ',' '\n' | sort | uniq | wc -l
#There are 6384 types


#Filter responses using only words in AoA list.
pos="nouns"
aoafile=`echo ~/Research/WordRep/WordRep_alhama/03-data/AoA/wordbank/data_cogsci/aoa_wordbank_eng_produces_prop0.5_${pos}_clean_means.csv`
cat $aoafile | cut -f1 -d";" > known_${pos}.txt

#todo this should be factorized in one function
##Find line numbers for each column (cue, r1, r2, r3) that have a correspondance in learnt_words file
ref_file="known_${pos}.txt"
outputf="swow_known_${pos}.txt"
for col in `seq 1 4`; do
    cat $swowcrf | cut -f${col} -d"," | grep -w -n -f $ref_file | cut -f1 -d":" |sort > nl${col}.txt
done

##Get only lines with all the associates
join nl1.txt nl2.txt | join - nl3.txt | join - nl4.txt > aux

##Filter these lines in cue-responses file
nl $swowcrf > swow_nl.txt
grep -w -f aux swow_nl.txt | cut -f2 |sort > $outputf

##Remove intermediate files
rm nl?.txt
rm swow_nl.txt
rm aux

#Count
wc -l $outputf


