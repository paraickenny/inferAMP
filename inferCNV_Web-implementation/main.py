from flask import Flask, request
app = Flask(__name__)

@app.route("/evaluate")
def infercnv():
    filename1 = "coordinates.txt"
    filename2 = "foundationone.txt"
    filename3 = "cosmic.txt"
    foundationlist = []
    genelist = []
    genome = []
    counter = 0
    cosmiclist = []

    with open(filename2) as fh:  # imports the list of genes on Foundation One test
        while True:
            line2 = fh.readline().rstrip()  # read the first line
            line2 = line2.upper()
            if not line2: break
            foundationlist.append(line2)

    with open(filename3) as fh:  # imports the list of genes recurrently altered in cancer from COSMIC
        while True:
            line3 = fh.readline().rstrip()  # read the first line
            line3 = line3.upper()
            if not line3: break
            cosmiclist.append(line3)

    with open(filename1) as fh:
        while True:
            line1 = fh.readline().rstrip()  # read the first line
            line1 = line1.upper()  # changes all text to upper case
            counter += 1
            if not line1: break
            if "Chromosome" not in line1:
                chr, start, end, karyotype, gene = line1.split("\t")  # splits each line by tabs

                genelist.append(gene)
                coordinates = chr, start, end, karyotype, gene
                coordinates = list(coordinates)
                coordinateswithcounter = chr, start, end, karyotype, gene, counter
                coordinateswithcounter = list(coordinateswithcounter)
                genome.append(coordinateswithcounter)

    weboutput = ""              #starts assembling a string which will return the results to browser in html format
    weboutput += "<h1>InferCNV Results:</h1>"

    candidates = []

    query = request.args.get('query')          # takes the query argument passed in http query to app (gene names)
    query = query.encode('ascii','ignore')    # change imported text from unicode to ascii
    candidates = list(query.split(","))
    candidates = map(str.strip, candidates)  # removes spaces from elements in list
    candidates = map(str.upper, candidates)  # convert all elements of string to upper case

    for a in candidates:
        if a not in genelist:           # handling cases where entered gene name is not in list - either typo or using non-standard name
            weboutput += "*****************************************************************<br>"
            weboutput += str("I didn't find the following gene. Are you sure of correct name: " + a + "<br>")
            weboutput += "*****************************************************************<br>"
            weboutput += "If it is one of the following, please correct to the standard name:<br>"
            weboutput += "C11ORF30 = EMSY <br> C17ORF39 = GID4<br> FAM123B = AMER1<br> GPR124 = ADGRA2<br> MLL = KMT2A<br> MLL2 = KMT2D <br> MLL3 = KMT2C<br> MRE11A = MRE11 <br> MYCL1 = MYCL <br> MYST3 = KAT6A <br> PARK2 = PRKN <br>"
            weboutput += "*****************************************************************<br>"

    weboutput += str("<p> You entered the following amplified genes: " + "%s" % ", ".join(map(str, candidates)) + "<br>")
    nonamplifiedgenes = list(set(foundationlist) - set(candidates))  # assumes genes not flagged as amplified by Foundation are not amplified. Told this is true by Tech Support

    for g in genome:  # tag genes with status for FoundationOne reported genes
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

    for g in genome:  # populates g[6] with "Pending"
        g.append("unassigned")

    for g in genome:
        currentchr = g[0]
        currentposition = int(g[5])

        if g[6] == "reported-up" and firsthit == 0:
            currentstatus = "inferAMP"
            g[7] = currentstatus
            firsthit = 1  # flags the first gene on the chr with a Foundation One report. 1 is for amplified, 2 is for same
            increment_firstfound = int(g[5])
            increment_lastfound = int(g[5])
            lasthit = 1
        if g[6] == "reported-notup" and firsthit == 0:
            currentstatus = "inferSAME"
            g[7] = currentstatus
            firsthit = 2  # flags the first gene on the chr with a Foundation One report. 1 is for amplified, 2 is for same
            increment_firstfound = int(g[5])
            increment_lastfound = int(g[5])
            lasthit = 2
        if g[
            6] == "reported-up" and firsthit > 0:  # found amplified gene in an amplicon already containing an amplified gene
            currentstatus = "inferAMP"
            g[7] = currentstatus
            if lasthit == 2:
                for a in genome[increment_lastfound:currentposition - 1]:
                    a[7] = "possibleAMP"
            if lasthit == 1:
                for a in genome[increment_lastfound:currentposition - 1]:
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
        if currentchr != lastchr:  # need to close out variables and fill in information between chr ends and first Foundation One assessment
            currentposition = int(g[5])
            if firsthit == 1:  # fills in fields from start of chr to first reported marker
                for a in genome[increment_startpending - 1:increment_firstfound - 1]:
                    a[7] = "possibleAMP"

            if firsthit == 2:
                for a in genome[increment_startpending - 1:increment_firstfound - 1]:
                    a[7] = "possibleSAME"

            if lasthit == 1:
                for a in genome[increment_lastfound:currentposition - 1]:
                    a[7] = "possibleAMP"
            if lasthit == 2:
                for a in genome[increment_lastfound:currentposition - 1]:
                    a[7] = "possibleSAME"
            lasthit = 0
            firsthit = 0
            increment_startpending = int(g[5])
        lastchr = currentchr
        laststatus = currentstatus

    for q in genome:  # converts chromosomal p q arms to lower case
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
        weboutput += "<p>----------------------------------------------------------------------------------------------------------------------------</p>"
        cosmicinamp = []
        startgene = a[0]  # picks the start and end chromosomal ideogram loci for reporting
        endgene = a[len(a) - 1]
        startlocus = startgene[0] + startgene[3]
        endlocus = endgene[0] + endgene[3]
        for g in a:

            if g[4] in cosmiclist:
                cosmicinamp.append(g[4])
            if g[6] == "reported-up":
                weboutput += str("Reported amplified: " + "<a href=\"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln=" + g[4] + "\" target=\"_blank\">" + g[4] + "</a>" + " (Chr" + g[0] + g[3] + ")<br>")

        weboutput += str("<p>This region includes a total of %s POTENTIALLY co-amplified genes" % len(a) + " between Chr " + startlocus + " and " + endlocus + ".<br>")
        weboutput += str ("This includes the following %s gene(s) annotated as recurrently altered in cancer by COSMIC: <br>" % len(cosmicinamp))
        weboutput += "\n"

        for p in cosmicinamp:
            weboutput+= str("<a href=\"https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln=" + p  + "\" target=\"_blank\">" + p +"</a>" + "&emsp;") # generates space-delimited list of gens with links to COSMIC
        weboutput += "<br>"
    weboutput += " </p> ---------------------------------------------------------------------------------------------------------------------------- <br>"
    weboutput += "<br><br>InferCNV - a tool for inferring possible copy number changes using data from Foundation One NGS test reports. <br>"
    weboutput += "Written by Paraic Kenny, PhD <br>"
    weboutput += "Code available from: https://github.com/paraickenny/inferCNV <br>"
    weboutput += "To run another analysis, click <a href=\"http://infercnv.org\"> HERE</a> <br>"
    weboutput += "<h1> Research Use Only </h1>"

    return weboutput

if __name__ == "__main__":
    app.run()
