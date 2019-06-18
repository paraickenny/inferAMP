

filename1 = "coordinates.txt"
filename2 = "foundationone.txt"
filename3 = "cosmic.txt"
foundationlist = []
genelist = []
genome = []
counter = 0
cosmiclist = []

with open(filename2) as fh:             # imports the list of genes on Foundation One test
    while True:
        line2 = fh.readline().rstrip()  # read the first line
        line2 = line2.upper()
        if not line2: break
        foundationlist.append(line2)

with open(filename3) as fh:             # imports the list of genes recurrently altered in cancer from COSMIC
    while True:
        line3 = fh.readline().rstrip()  # read the first line
        line3 = line3.upper()
        if not line3: break
        cosmiclist.append(line3)

with open(filename1) as fh:
    while True:
        line1 = fh.readline().rstrip()  # read the first line
        line1 = line1.upper()           # changes all text to upper case
        counter += 1
        if not line1: break
        if "Chromosome" not in line1:
            chr, start, end, karyotype, gene = line1.split("\t")    # splits each line by tabs

            genelist.append(gene)
            coordinates = chr, start, end, karyotype, gene
            coordinates = list(coordinates)
            coordinateswithcounter = chr, start, end, karyotype, gene, counter
            coordinateswithcounter = list(coordinateswithcounter)
            genome.append(coordinateswithcounter)


entry_error1 = "This gene name entered is not a standard gene name. If it is one of the following, please correct to the standard name:"
entry_error2 = "C11ORF30 = EMSY \t C17ORF39 = GID4\t FAM123B = AMER1\n GPR124 = ADGRA2\t MLL = KMT2A\t MLL2 = KMT2D \n MLL3 = KMT2C\t MRE11A = MRE11 \t MYCL1 = MYCL \n MYST3 = KAT6A \t PARK2 = PRKN \t TERC = \n"


print
print "Enter names of reported amplified genes below, pressing enter after each one. Enter XX as the last gene when finished."
print "To evaluate a test set, simply enter 1 or 2 or 3."
print "1: CCND1, FGF19,RET, ERBB2, GRB7"
print "2: ERBB2, MYC, CCND3, KRAS, IL7R, FGFR1"
print "3: KRAS, EGFR, CDKN1B, BCL2"

candidates = []
answer = ""

while answer != "XX":
    answer = raw_input("Enter gene name or XX if finished:")
    answer = answer.rstrip()
    if answer == "1":
        candidates = ["CCND1", "FGF19", "RET", "ERBB2", "GRB7"]
    elif answer == "2":
        candidates = ["ERBB2", "MYC", "CCND3", "KRAS", "IL7R", "FGFR1"]
    elif answer == "3":
        candidates = ["KRAS", "EGFR", "CDKN1B", "BCL2"]
    elif answer in genelist:
        candidates.append(answer)
    elif answer not in genelist and answer != "XX":
        print entry_error1
        print entry_error2
for a in candidates:
    if a not in genelist:
        print "I didn't find the following gene. Are you sure of correct name: ", a


print "\n \nYou entered the following amplified genes:", candidates

nonamplifiedgenes = list(set(foundationlist) - set(candidates))         # assumes genes not flagged as amplified by Foundation are not amplified. Told this is true by Tech Support


for g in genome:                              # tag genes with status for FoundationOne reported genes
    if g[4] in candidates:
        g.append("reported-up")
    elif g[4] in nonamplifiedgenes:
        g.append("reported-notup")
    elif g not in candidates and g not in nonamplifiedgenes:
        g.append("not reported")


currentstatus = "Pending"
lastchr = "0"
firsthit = 0
laststatus = ""
lasthit = 0
increment_startpending = 1

for g in genome:                 # populates g[6] with "Pending"
    g.append("unassigned")

for g in genome:
    currentchr = g[0]
    currentposition = int(g[5])

    if g[6] == "reported-up" and firsthit == 0:
        currentstatus = "inferAMP"
        g[7] = currentstatus
        firsthit = 1                               # flags the first gene on the chr with a Foundation One report. 1 is for amplified, 2 is for same
        increment_firstfound = int(g[5])
        increment_lastfound = int(g[5])
        lasthit = 1
    if g[6] == "reported-notup" and firsthit == 0:
        currentstatus = "inferSAME"
        g[7] = currentstatus
        firsthit = 2                               # flags the first gene on the chr with a Foundation One report. 1 is for amplified, 2 is for same
        increment_firstfound = int(g[5])
        increment_lastfound = int(g[5])
        lasthit = 2
    if g[6] == "reported-up" and firsthit > 0:         # found amplified gene in an amplicon already containing an amplified gene
        currentstatus = "inferAMP"
        g[7] = currentstatus
        if lasthit == 2:
            for a in genome[increment_lastfound:currentposition-1]:
                a[7] = "possibleAMP"
        if lasthit == 1:
            for a in genome[increment_lastfound:currentposition-1]:
                a[7] = "inferAMP"
        increment_lastfound = int(g[5])
        lasthit = 1

    if g[6] == "reported-notup" and firsthit > 0:
        currentstatus = "inferSAME"
        g[7] = currentstatus
        increment_lastfound = int(g[5])
        lasthit = 2
    if g[6] == "not reported" and currentchr == lastchr:
        if laststatus == "inferAMP":
            g[7] = "possibleAMP"
        elif laststatus != "inferAMP":
            g[7] = laststatus
    if currentchr != lastchr:       # need to close out variables and fill in information between chr ends and first Foundation One assessment
        currentposition = int(g[5])
        if firsthit == 1:           # fills in fields from start of chr to first reported marker
            for a in genome[increment_startpending-1:increment_firstfound-1]:
                a[7] = "possibleAMP"

        if firsthit == 2:
            for a in genome[increment_startpending-1:increment_firstfound-1]:
                a[7] = "possibleSAME"

        if lasthit == 1:
            for a in genome[increment_lastfound:currentposition-1]:
                a[7] = "possibleAMP"
        if lasthit == 2:
            for a in genome[increment_lastfound:currentposition-1]:
                a[7] = "possibleSAME"
        lasthit = 0
        firsthit = 0
        increment_startpending = int(g[5])
    lastchr = currentchr
    laststatus = currentstatus

for q in genome:                # converts chromosomal p q arms to lower case
    q[3] = str(q[3]).lower()


regions = []
amplicon = []
foundamplicon = 0
for q in genome:
    if "AMP" in q[7]:
        foundamplicon = 1
        amplicon.append(q)
    if "AMP" not in q[7] and foundamplicon == 1:
        foundamplicon = 0
        regions.append(amplicon)
        amplicon = []

print "%s amplicons found. " % len(regions)

for a in regions:
    print "-------------------------------------------------------"
    cosmicinamp = []
    startgene = a[0]            # picks the start and end chromosomal ideogram loci for reporting
    endgene = a[len(a)-1]
    startlocus = startgene[0] + startgene[3]
    endlocus = endgene[0] + endgene[3]
    for g in a:

            if g[4] in cosmiclist:
                cosmicinamp.append(g[4])
            if g[6] == "reported-up":
                print "Reported amplified: ", g[4], "(Chr", g[0], g[3], ")"

    print "This region includes a total of %s POTENTIALLY co-amplified genes" % len(a), "between Chr ", startlocus, "and ", endlocus, "."
    print "This includes the following %s gene(s) annotated as recurrently altered in cancer by COSMIC:" % len(cosmicinamp)
    print "%s" % ", ".join(map(str, cosmicinamp))  # generates a nicely formatted list without square brackets & quotes

f = open("inferCNV_output.txt", "w")

for a in genome:

    line = str(a[0]) + "\t" + str(a[1]) + "\t" + str(a[2]) + "\t" + str(a[3]) + "\t" + str(a[4]) + "\t" + str(a[5]) + "\t" + str(a[6]) + "\t" + str(a[7]) + "\n"
    f.write(line)

f.close





