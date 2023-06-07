# import package ...
import math
import sys


def eval(trecrunFile, qrelsFile, outputFile):
    fleRun = open(trecrunFile, 'rt')
    fleQrels = open(qrelsFile, 'rt')
    fleOut = open(outputFile, 'w')

    trecDict = {}
    relDict = {}

    # creating the dictionary for trecrun
    for line in fleRun:
        splt = line.split()
        query = splt[0]
        docID = splt[2]
        if query not in trecDict:
            trecDict[query] = {}
        trecDict[query][docID] = []
        for val in splt[3:5]:
            trecDict[query][docID].append(val)

    # creating the dictionary for qrels
    for line in fleQrels:
        splt = line.split()
        query = splt[0]
        docID = splt[2]
        if query not in relDict:
            relDict[query] = {}
        relDict[query][docID] = splt[3]

    # calculating numRels and relFound
    numRels = {}
    relFound = {}
    for query in list(trecDict.keys()):
        if query in list(relDict.keys()):
            numRels[query] = 0
            relFound[query] = 0
            for docID in relDict[query]:
                if int(relDict[query][docID]) > 0:
                    numRels[query] = numRels[query] + 1
                    if docID in trecDict[query]:
                        relFound[query] = relFound[query] + 1

    # calculating Reciprocal Rank
    recRank = {}
    for query in trecDict:
        if query in relDict:
            docs = trecDict[query]
            flag = False
            for document in docs:
                if document in relDict[query] and int(relDict[query][document]) > 0:
                    rank = trecDict[query][document][0]
                    recRank[query] = 1 / int(rank)
                    flag = True
                    break
            if flag == False:
                recRank[query] = 0
    # calculating P@10 and R@10
    p10 = {}
    r10 = {}
    for query in trecDict:
        if query in relDict:
            docs = trecDict[query]
            count = 0
            for document in list(docs.keys())[:10]:
                if document in relDict[query] and int(relDict[query][document]) > 0:
                    count = count + 1

            p10[query] = count / 10
            nRel = numRels[query]
            if nRel == 0:
                r10[query] = 0
            else:
                r10[query] = count / nRel

    # calculating F1
    f1 = {}
    for query in trecDict:
        if p10[query] == 0 or r10[query] == 0:
            f1[query] = 0
        else:
            pQ = p10[query]
            rQ = r10[query]
            calc = 2 * ((pQ * rQ) / (pQ + rQ))
            f1[query] = calc

    # calculating p@20%
    p20 = {}
    for query in trecDict:
        docs = trecDict[query]
        prec = []
        rlCount = 0
        rec = 0
        rcount = 0
        for document in docs:
            rcount = rcount + 1
            if document in relDict[query] and int(relDict[query][document]) > 0:
                rlCount = rlCount + 1
                if numRels[query] != 0:
                    rec = rlCount / numRels[query]
                if rec >= 0.20:
                    prec.append(rlCount / rcount)
        if len(prec) != 0:
            p20[query] = max(prec)
        else:
            p20[query] = 0

    # calculating NDCG
    n_DCG = {}
    for query in trecDict:
        dcg = 0
        docs = trecDict[query]
        for document in list(docs.keys())[0:20]:
            if document in list(relDict[query].keys()):
                if int(trecDict[query][document][0]) > 1:
                    dcg = dcg + int(relDict[query][document]) / math.log2(int(trecDict[query][document][0]))

                elif int(trecDict[query][document][0]) == 1:
                    dcg = dcg + int(relDict[query][document])

            else:
                dcg = dcg + 0

        dicts = {}
        for document in list(relDict[query].keys()):
            dicts[document] = relDict[query][document]

        sortedT = sorted(dicts.items(), key=lambda item: -int(item[1]))
        sorted_T = {x: y for x, y in sortedT}
        idcg = 0
        count = 1
        for m in list(sorted_T.keys())[0:20]:
            if math.log2(count) != 0:
                idcg += int(sorted_T[m]) / math.log2(count)
            else:
                idcg += int(sorted_T[m])
            count = count + 1

        if idcg!=0:
            ndcg = dcg / idcg
        if numRels[query]!=0:
            n_DCG[query] = ndcg
        else:
            n_DCG[query] = 0



    # calculating AP
    ap = {}
    for query in trecDict:
        prec = []
        ret = 0
        rel = 0
        docs = trecDict[query]
        for document in docs:
            ret = ret + 1
            if document in relDict[query] and int(relDict[query][document]) > 0:
                rel = rel + 1
                prec.append(rel / ret)
        if numRels[query] != 0:
            ap[query] = sum(prec) / numRels[query]
        else:
            ap[query] = 0



    sRels = 0
    for query in numRels:
        sRels = sRels + numRels[query]
    sFound = 0
    for query in relFound:
        sFound = sFound + relFound[query]

    mNDCG = 0
    for query in n_DCG:
        mNDCG = mNDCG + n_DCG[query]
    mNDCG = mNDCG/len(n_DCG)


    mRR = 0
    for query in recRank:
        mRR = mRR + recRank[query]
    mRR = mRR/len(recRank)


    mP10 = 0
    for query in p10:
        mP10+=p10[query]
    mP10 = mP10/len(p10)


    mR10 = 0
    for query in r10:
        mR10+=r10[query]
    mR10 = mR10/len(r10)


    mF10 = 0
    for query in f1:
        mF10+=f1[query]
    mF10 = mF10/len(f1)


    mP20 = 0
    for query in p20:
        mP20+=p20[query]
    mP20 = mP20/len(p20)


    mAP = 0
    for query in ap:
        mAP+=ap[query]
    mAP = mAP/len(ap)



    for query in trecDict:
        fleOut.write('NDCG@20  '+ query + '  ' + str(round(n_DCG[query],4))+'\n')
        fleOut.write('numRel  ' + query + '  ' + str(round(numRels[query])) + '\n')
        fleOut.write('relFound  ' + query + '  ' + str(round(relFound[query])) + '\n')
        fleOut.write('RR  ' + query + '  ' + str(round(recRank[query],4)) + '\n')
        fleOut.write('P@10  ' + query + '  ' + str(round(p10[query],4)) + '\n')
        fleOut.write('R@10  ' + query + '  ' + str(round(r10[query],4)) + '\n')
        fleOut.write('F1@10  ' + query + '  ' + str(round(f1[query],4)) + '\n')
        fleOut.write('P@20%  ' + query + '  ' + str(round(p20[query],4)) + '\n')
        fleOut.write('AP  ' + query + '  ' + str(round(ap[query],4)) + '\n')

    fleOut.write('NDCG@20  ' + 'all' + '  ' + str(round(mNDCG,4)) + '\n')
    fleOut.write('numRel  ' + 'all' + '  ' + str(sRels) + '\n')
    fleOut.write('relFound  ' + 'all' + '  ' + str(sFound) + '\n')
    fleOut.write('MRR  ' + 'all' + '  ' + str(round(mRR,4)) + '\n')
    fleOut.write('P@10  ' + 'all' + '  ' + str(round(mP10,4)) + '\n')
    fleOut.write('R@10  ' + 'all' + '  ' + str(round(mR10,4)) + '\n')
    fleOut.write('F1@10  ' + 'all' + '  ' + str(round(mF10,4)) + '\n')
    fleOut.write('P@20%  ' + 'all' + '  ' + str(round(mP20,4)) + '\n')
    fleOut.write('MAP  ' + 'all' + '  ' + str(round(mAP,4)) + '\n')

    fleRun.close()
    fleQrels.close()
    fleOut.close()

    def p_at_r(q):
        if numRels[q] == 0:
            return {}
        else:
            p = []
            count = 0
            rel = 0
            recall_step = 1 / 50
            prev_recall = 0  # keep track of previous recall value
            for doc in list(trecDict[q].keys()):
                count += 1
                if doc in list(relDict[q].keys()) and int(relDict[q][doc]) > 0:
                    rel += 1
                    recall = rel / numRels[q]
                    if recall >= 0:
                        r = round(recall / recall_step) * recall_step
                        if r <= 1:
                            p.append((r, rel / count))
                    # check if recall remains unchanged after a point
                    if recall == prev_recall and count == numRels[q]:
                        p.append((1.0, 0.0))  # map remaining recall to 1.00 with 0 precision
                        break
                    prev_recall = recall  # update previous recall value
            if len(p) != 0:
                precision_at_recall = dict(p)
            else:
                precision_at_recall = {0: 0}

            if list(precision_at_recall.keys())[-1] < 1.00:
                initial = list(precision_at_recall.keys())[-1]
                skip = 0.02
                while initial <= 1.00:
                    precision_at_recall[initial + skip] = 0
                    initial = initial + skip
            return precision_at_recall

    print(p_at_r("330975"))

    return


if __name__ == '__main__':
    argv_len = len(sys.argv)
    runFile = sys.argv[1] if argv_len >= 2 else "msmarcofull-ql.trecrun"
    qrelsFile = sys.argv[2] if argv_len >= 3 else "msmarco.qrels"
    outputFile = sys.argv[3] if argv_len >= 4 else "ql.eval"

    eval(runFile, qrelsFile, outputFile)
