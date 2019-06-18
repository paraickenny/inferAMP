# inferAMP
Genome scale copy number inference from discrete reports of gene-level amplifications on somatic cancer NGS testing reports

A working version of the web implementation is at http://inferamp.org

Note: The code was initially named inferCNV but changed name to inferAMP on 6/10/2019 when we determined that the other name was alread in prior use.

Two directories are provided:

web-implementation:

python script with flask and associated web page into which queried genes can be entered. 

The main script is in main.py.

main.py returns responses via html output into the browser.

Additional files are provided for use with the google app engine including app.yaml, requirements.txt.


Command line implementation:

inferAMPv2.py

Both directories contain the necessary input files:

coordinates.txt hg38 coordinates of genes from human genome

COSMIC.txt list of genes recurrently altered in cancer from COSMIC database

foundationone.txt list of genes reported on Foundation One genomic assay (note this project is not affiliated with Foundation Medicine in any way).


