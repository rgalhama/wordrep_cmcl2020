Model selection.

Parameters to explore (also in )

## Common in SVD and SGNS:
win: 1,2,3,5,10
thr: 10, 50, 100
dyn: off/on
size: 100
Note: I tried size 500 for many models, but the output is always the same number of neighbours for every single word (in most cases, all words are neigbhours to each other, so the vectors become too similar.). I think it's better to add a footnote about this in the paper and remove from simulations, since it takes time and the output is completely uninteresting. 

## SVD
eig: 1 (traditional)

#Similarity threshold:
 0.6, 0.7, 0.8, 0.9



