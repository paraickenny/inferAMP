from flask import Flask, request
app = Flask(__name__)

@app.route("/evaluate")
def infercnv():

    assay = request.args.get('test')
    assay = assay.encode('ascii','ignore')
    if assay == "FoundationOne":
        filename2 = "foundationone.txt"
    if assay == "FoundationCdx":
        filename2 = "foundation_one_cdx.txt"
    if assay == "TempusXT":
        filename2 = "tempus-596.txt"
    if assay == "Oncomine-v3":
        filename2 = "oncomine-v3.txt"
    if assay == "Caris-MI":
        filename2 = "caris-mi-profile.txt"
    if assay == "Trusight170":
        filename2 = "trusight_170.txt"
    if assay == "Trusight500":
        filename2 = "trusight500.txt"
    if assay == "STRATA-NGS":
        filename2 = "strataNGS.txt"

    if assay == "custom":
        customlist = request.args.get('custom')
        customlist = customlist.encode('ascii', 'ignore')

    verboseoutput = ""
    verboseoutput = request.args.get('verbose')
    #verboseoutput = verboseoutput.encode('ascii', 'ignore')





    filename1 = "coordinates.txt"
    filename3 = "cosmic.txt"
    foundationlist = []
    genelist = []
    genome = []
    counter = 0
    cosmiclist = []

    if assay != "custom":
        with open(filename2) as fh:  # imports the list of genes on Foundation One test
            while True:
                line2 = fh.readline().rstrip()  # read the first line
                line2 = line2.upper()
                if not line2: break
                foundationlist.append(line2)

    if assay == "custom":
        foundationlist = customlist.split("\r\n")
        foundationlist = map(str.strip, foundationlist)  # removes spaces from elements in list
        foundationlist = map(str.upper, foundationlist)  # convert all elements of string to upper case
        foundationlist = filter(None, foundationlist)   # removes blank elements in list resulting from blank lines in form text area

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
    weboutput += "<h1>InferAMP Results:</h1>"
    #weboutput += customlist
    candidates = []

    query = request.args.get('query')          # takes the query argument passed in http query to app (gene names)
    query = query.encode('ascii','ignore')    # change imported text from unicode to ascii
    candidates = list(query.split(","))
    candidates = map(str.strip, candidates)  # removes spaces from elements in list
    candidates = map(str.upper, candidates)  # convert all elements of string to upper case



    weboutput += str("Assay selected: " + assay + " (" + str(len(foundationlist)) + " genes).<br>")
    if len(foundationlist) < 100:
        weboutput += "Note: Amplicon boundary refinement is much more accurate in assays panels with high gene numbers."
    if verboseoutput == "verbose":
        weboutput += "<p> Verbose output selected.<br>"
        weboutput += "<p> Assay gene list:<br>"
        for s in foundationlist:
            weboutput += str(s + "," + "&ensp;")
    weboutput += "<p>----------------------------------------------------------------------------------------------------------------------------</p>"

    if assay == "custom":
        custom_errors=[]
        for s in foundationlist:
            if s not in genelist:
                custom_errors.append(s)
        if custom_errors != []:
            weboutput += "<p> Custom assay gene name entry error check:<br>"
            weboutput += str("I didn't find the following gene(s). Are you sure of correct name: " + str(custom_errors) + "<br>")
            weboutput += "If it is one of the following, please correct to the standard name:<br>"
            weboutput += "C10ORF54 = VSIR <br> C11ORF30 = EMSY <br> C17ORF39 = GID4<br> FAM123B = AMER1<br> FAM175A = ABRAXAS1<br> GPR124 = ADGRA2<br> MLL = KMT2A<br> MLL2 = KMT2D <br> MLL3 = KMT2C<br> MRE11A = MRE11 <br> MYCL1 = MYCL <br> MYST3 = KAT6A <br> PAK5 = PAK7<br>  PARK2 = PRKN <br> TCEB1 = ELOC<br> WHSC1 = NSD1<br> WHSC1L1 = NSD3<br>"
            weboutput += "Otherwise, please try to find an alternate name <a href=\"https://www.ncbi.nlm.nih.gov/gene\"> HERE</a> <br>"



    for a in candidates:
        if a not in genelist:           # handling cases where entered gene name is not in list - either typo or using non-standard name
            weboutput += "*****************************************************************<br>"
            weboutput += str("I didn't find the following gene. Are you sure of correct name: " + a + "<br>")
            weboutput += "*****************************************************************<br>"
            weboutput += "If it is one of the following, please correct to the standard name:<br>"
            weboutput += "C10ORF54 = VSIR <br> C11ORF30 = EMSY <br> C17ORF39 = GID4<br> FAM123B = AMER1<br> FAM175A = ABRAXAS1<br> GPR124 = ADGRA2<br> MLL = KMT2A<br> MLL2 = KMT2D <br> MLL3 = KMT2C<br> MRE11A = MRE11 <br> MYCL1 = MYCL <br> MYST3 = KAT6A <br> PAK5 = PAK7<br>  PARK2 = PRKN <br> TCEB1 = ELOC<br> WHSC1 = NSD1<br> WHSC1L1 = NSD3<br>"
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

    boundary_gene_list = []

    for a in regions:
        weboutput += "<p>----------------------------------------------------------------------------------------------------------------------------</p>"
        cosmicinamp = []
        genesinamp = []
        startgene = a[0]  # picks the start and end chromosomal ideogram loci for reporting
        endgene = a[len(a) - 1]
        startlocus = startgene[0] + startgene[3]
        endlocus = endgene[0] + endgene[3]
        start_non_amp_index = startgene[5]-1    #gets the index of the gene preceding the first predicted amplified gene
        end_non_amp_index = endgene[5]+1        #gets the index of the gene following the last predicted amplified gene

        for w in a:
            genesinamp.append(w[4])

        for v in genome:            #determines the two non-amplified assay genes representing the boundary of the amplicon
            if v[5] == start_non_amp_index:
                start_non_amp_boundary_gene = v[4]
                if v[0] != a[0][0]:
                    start_non_amp_boundary_gene = str("Start of chromosome " + str(a[0][0]))
            if v[5] == end_non_amp_index:
                end_non_amp_boundary_gene = v[4]
                if v[0] != a[0][0]:
                    end_non_amp_boundary_gene = str("End of chromosome " + str(a[0][0]))

        boundary_gene_list.append(end_non_amp_boundary_gene)
        boundary_gene_list.append(start_non_amp_boundary_gene)

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
        if verboseoutput == "verbose":
            if "chromosome" in str(start_non_amp_boundary_gene + end_non_amp_boundary_gene):
                weboutput += str("<p> This region is between a chromosomal end and an assayed gene not reported as amplified: " + start_non_amp_boundary_gene + " and " + end_non_amp_boundary_gene)
            else:
                weboutput += str("<p> This region is defined as the genes between the following assayed genes which were NOT reported as amplified: " + start_non_amp_boundary_gene + " and " + end_non_amp_boundary_gene)
            weboutput += str("<p> All genes in this amplified region are listed here: " + "%s" % ", ".join(map(str, genesinamp)) + "<br>")

    boundary_gene_set = set(boundary_gene_list)
    for i in boundary_gene_set:
       if boundary_gene_list.count(i) > 1:
            weboutput += "<p>----------------------------------------------------------------------------------------------------------------------------</p>"
            weboutput += str("<P>NOTE: Two potential amplicons share the same reported non-amplified boundary gene: " + i)
            weboutput += str("<p> Consider the possibility that these adjacent potential amplicons actually represent a single amplicon if " + i + " may be reported incorrectly.")
            if verboseoutput != "verbose":
                weboutput += "<p>Repeat the analysis, checking the VERBOSE checkbox on the input form, for more details."




    weboutput += " </p> ---------------------------------------------------------------------------------------------------------------------------- <br>"
    weboutput += "<br><br>InferAMP - a tool for inferring possible copy number changes using data from Foundation One NGS test reports. <br>"
    weboutput += "Written by Paraic Kenny, PhD <br>"
    weboutput += "Code available from: https://github.com/paraickenny <br>"
    weboutput += "To run another analysis, click <a href=\"http://inferamp.org\"> HERE</a> <br>"
    weboutput += "<h1> Research Use Only </h1>"

    return weboutput

if __name__ == "__main__":
    app.run()
