#!/bin/bash
export PATH="/home/risham-raj-byahut/texlive/2026/bin/x86_64-linux:$PATH"
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cp main.pdf manuscript.pdf
echo "Done: manuscript.pdf updated"
