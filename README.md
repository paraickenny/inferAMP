# inferCNV
Genome scale copy number inference from discrete reports of gene-level amplifications on somatic cancer NGS testing reports

A working version of the web implementation is at http://infercnv.org

Two directories are provided:

web-implementation:
python script with flask providing for a web based query page, and python. 
The main script is in main.py.
Additional files are provided for use with the google app engine including app.yaml, requirements.txt.


Command line implementation:
inferCNVv2.py

Both directories contain the necessary input files:
coordinates.txt hg38 coordinates of genes from human genome
COSMIC.txt list of genes recurrently altered in cancer from COSMIC database
foundationone.txt list of genes reported on Foundation One genomic assay (note this project is not affiliated with Foundation Medicine in any way).


