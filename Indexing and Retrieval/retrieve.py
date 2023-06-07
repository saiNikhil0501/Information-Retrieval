# import package ...
import sys
import gzip
import json

import math

var = None
COUNT = None


def count(input):
    global COUNT
    count = 0
    with gzip.open(input, 'rt') as fle:
        lines = fle.read()
    jSON_dict = json.loads(lines)
    articles = jSON_dict["corpus"]
    for article in articles:
        art_list = article["text"].split(" ")
        new_array = [x for x in art_list if x != '']
        count += len(new_array)
    COUNT = count
    return


def length(input):
    global var
    len_list = {}
    with gzip.open(input, 'rt') as fle:
        lines = fle.read()
    jSON_dict = json.loads(lines)
    articles = jSON_dict["corpus"]
    for article in articles:
        art_list = article["text"].split(" ")
        new_array = [x for x in art_list if x != '']
        len_list[article["storyID"]] = len(new_array)
    var = len_list
    return


def buildIndex(inputFile):
    # Your function start here ...
    fle = gzip.open(inputFile, 'rt')
    data = json.load(fle)
    docs = data['corpus']
    indx = {}

    for doc in docs:
        i_d = doc['storyID']
        txt = doc['text'].split()
        txt = [element for element in txt if element != ""]
        for ind, word in enumerate(txt):
            if word not in indx:
                indx[word] = {}
            if i_d not in indx[word]:
                indx[word][i_d] = [ind + 1]
            else:
                indx[word][i_d].append(ind + 1)
    return indx


def phraseCheck(arr):
    ar = arr[0]
    for x in ar:
        successor_found = False
        for j in range(1, len(arr)):
            if x + 1 in arr[j]:
                x += 1
                successor_found = True
            else:
                successor_found = False
                break
        if successor_found is True:
            return True
    return False


def successorCount(arr):
    ar = arr[0]
    count = 0
    for x in ar:
        successor_found = False
        for j in range(1, len(arr)):
            if x + 1 in arr[j]:
                x += 1
                successor_found = True
            else:
                break
        if successor_found is True:
            count += 1
    return count


def runQueries(index, queriesFile, outputFile):
    global COUNT
    global var
    fle = open(queriesFile, 'rt')
    oFle = open(outputFile, 'w')
    for line in fle:
        line = line.rstrip('\n')
        splt = line.split('\t')
        qType = splt[0]
        q = splt[2:]
        if qType == 'and':
            arr = []
            for word in q:
                if " " in word:
                    st = set()
                    temp = word.split()
                    a = []
                    for w in temp:
                        s = set(index[w].keys())
                        a.append(s)
                    commonDocs = list(set.intersection(*a))
                    for doc in commonDocs:
                        ar = []
                        for w in temp:
                            ar.append(index[w][doc])
                        if phraseCheck(ar):
                            st.add(doc)
                    arr.append(st)
                else:
                    st = set(index[word].keys())
                    arr.append(st)
            final = list(set.intersection(*arr))
            final.sort()
            count = 1
            for doc in final:
                oFle.write(
                    splt[1] + " " + "skip" + " " + doc + " " + str(count) + " " + "1.0" + " " + "sbommisetty" + "\n")
                count += 1
        if qType == 'or':
            arr = []
            for word in q:
                if " " in word:
                    st = set()
                    temp = word.split()
                    a = []
                    for w in temp:
                        s = set(index[w].keys())
                        a.append(s)
                    commonDocs = list(set.intersection(*a))
                    for doc in commonDocs:
                        ar = []
                        for w in temp:
                            ar.append(index[w][doc])
                        if phraseCheck(ar):
                            st.add(doc)
                    arr.append(st)
                else:
                    st = set(index[word].keys())
                    arr.append(st)
            final = list(set.union(*arr))
            final.sort()
            count = 1
            for doc in final:
                oFle.write(
                    splt[1] + " " + "skip" + " " + doc + " " + str(count) + " " + "1.0" + " " + "sbommisetty" + "\n")
                count += 1
        if qType == 'ql':
            myu = 300
            ql_ = {}
            cnt = COUNT
            for doc in list(var.keys()):
                ql = 0
                dcs = var[doc]
                contains_query = False
                for word in splt[2:]:
                    if " " not in word:
                        fq = 0
                        if doc in index[word].keys():
                            fq = len(index[word][doc])
                            contains_query = True
                        cq = 0
                        for d in index[word].keys():
                            cq += len(index[word][d])
                        ql += math.log((fq + (myu * (cq / cnt))) / (dcs + myu))
                if contains_query:
                    ql_[doc] = ql
            sorted_T = sorted(ql_.items(), key=lambda item: (-item[1], item[0]))
            ql_ = {k: v for k, v in sorted_T}
            rank = 0
            for a in ql_:
                rank += 1
                oFle.write(splt[1] + " " + "skip" + " " + str(a) + " " + str(rank) + " " + "{:.4f}".format(
                    ql_[a]) + " " + "sbommisetty" + "\n")
        if qType == 'bm25':
            k1 = 1.8
            k2 = 5
            b = 0.75
            N = len(var)
            s = 0
            bm = {}
            for doc in var.keys():
                s += var[doc]
            avg_doc_len = s / len(var)

            for doc in list(var.keys()):
                lD = var[doc]
                bm25 = 0
                for word in splt[2:]:
                    qf = splt[2:].count(word)
                    if " " in word:
                        words = word.split(" ")
                        relevent = set()
                        terms_docs = []
                        for w in words:
                            x = set()
                            for d in list(index[w].keys()):
                                x.add(d)
                            terms_docs.append(x)
                        all = set.intersection(*terms_docs)

                        for document in list(all):
                            documentPosition = []
                            for w in words:
                                documentPosition.append(index[w][document])
                            if phraseCheck(documentPosition):
                                relevent.add(document)
                        y = len(relevent)
                        if doc in relevent:
                            pos = []
                            for w in words:
                                if doc in index[w].keys():
                                    pos.append(index[w][doc])
                            if len(pos) != 0 and phraseCheck(pos):
                                f = successorCount(pos)
                                K = k1 * ((1 - b) + b * lD / avg_doc_len)
                                bm25 += math.log((N - y + 0.5) / (y + 0.5)) * ((k1 + 1) * f / (K + f)) * (
                                        (k2 + 1) * qf / (k2 + qf))
                    else:
                        y = len(list(index[word].keys()))
                        if doc in index[word].keys():
                            f = len(index[word][doc])
                            K = k1 * ((1 - b) + b * lD / avg_doc_len)
                            bm25 += math.log((N - y + 0.5) / (y + 0.5)) * ((k1 + 1) * f / (K + f)) * ((k2 + 1) * qf / (k2 + qf))

                    if bm25 != 0:
                        bm[doc] = bm25

            sorted_T = sorted(bm.items(), key=lambda item: (-item[1], item[0]))
            bm = {k: v for k, v in sorted_T}

            rank = 0
            for a in bm:
                rank += 1
                oFle.write(splt[1] + " " + "skip" + " " + str(a) + " " + str(rank) + " " + "{:.4f}".format(
                    bm[a]) + " " + "sbommisetty" + "\n")
    fle.close()
    oFle.close()
    return


if __name__ == '__main__':
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "sciam.json.gz"
    queriesFile = sys.argv[2] if argv_len >= 3 else "P3train.tsv"
    outputFile = sys.argv[3] if argv_len >= 4 else "P3train.trecrun"

    index = buildIndex(inputFile)
    if queriesFile == 'showIndex':
        # Invoke your debug function here (Optional)
        f = 5
    elif queriesFile == 'showTerms':
        # Invoke your debug function here (Optional)
        d = 5
    else:
        length(inputFile)
        count(inputFile)
        runQueries(index, queriesFile, outputFile)

    # Feel free to change anything
