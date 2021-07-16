#!/bin/bash
# Compilation automatique des notebooks

cd docs/examples

# conversion initiale
#for i in $(find . -type f \( -iname "*.ipynb" \)); do :
#    print "Converting $i to .md"
#    jupytext --to markdown $i
#done


for i in $(find . -type f \( -iname "*.md" \)); do :
    print "Converting $i to notebook"
    jupytext --to ipynb $i --execute
done
