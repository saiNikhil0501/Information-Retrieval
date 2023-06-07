import sys
import gzip
import re
import matplotlib.pyplot as plt


def remove_trailing(w):
    word = re.sub(r'[\W_]+$', "", w)
    word = re.sub(r'^[\W_]+', "", word)
    return word


def stop(l):
    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                    "was", "were", "with"]

    for line in l:
        for arr in line:
            t = arr.copy()
            for i in range(1, len(arr)):
                if t[i] in stopword_lst:
                    arr.remove(t[i])

    return l


def tokenize(w):
    l = []
    word = w
    l.append(word)
    if word.startswith('https://') or word.startswith('http://'):
        without_trailing = remove_trailing(word)
        l.append(without_trailing)

    elif re.search(re.compile(r'^[0-9.,+-]*$'), word):
        l.append(word)
    else:
        word = word.lower()
        if any(i == "'" for i in word):
            word = word.replace("'", "")
        if all(j != "-" for j in word) and any(i == "." for i in word) and not any(
                re.match(r'\d+', chars) for chars in word):
            word = word.replace(".", "")
        if any(i == '-' for i in word):
            temp = word.split('-')
            temp.append(word.replace('-', ''))
            for w in temp:
                # "english-sources)" -> ["english","sources)", "englishsources)"
                if re.search(re.compile(r'^[0-9.,+-]*$'), w):
                    l.append(w)
                elif any(i == "." for i in w):
                    w = w.replace(".", "")
                    l.append(remove_trailing(w))
                else:
                    l.append(remove_trailing(w))
            return l

        # Step 8 where punctuation is like spaces
        word = remove_trailing(word)
        word = re.sub(r'[^\w.,-]', " ", word)
        arr = word.split()
        for i in arr:
            l.append(i)
    return l


def step_1a(l):
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    temp = l
    for line in temp:
        for arr in line:
            for i in range(1, len(arr)):
                stemming = arr[i]
                if arr[i].endswith('sses'):
                    stemming = stemming[:-4] + 'ss'

                elif arr[i].endswith('ied') or arr[i].endswith('ies'):
                    if len(arr[i]) - 3 > 1:
                        stemming = stemming[:-3] + 'i'
                    else:
                        stemming = stemming[:-3] + 'ie'
                elif arr[i].endswith('s') and not arr[i].endswith('us') and not arr[i].endswith('ss') :
                    second_to_last = arr[i][-2]
                    if any(char in vowels for char in arr[i][:-2]):
                        for char in arr[i][:-2]:
                            if char in vowels and char != second_to_last:
                                stemming = stemming[:-1]
                                break
                arr[i] = stemming

    return temp


def step_1b(l):
    temp = l
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    for line in temp:
        for arr in line:
            for i in range(1, len(arr)):
                stemming = arr[i]
                if stemming.endswith('eed') or stemming.endswith('eedly'):
                    ind = 0
                    for j in range(0, len(stemming)):
                        if stemming[j] in vowels:
                            ind = j
                            if ind < (len(stemming) - 1) and stemming[ind + 1] not in vowels:
                                ind = ind + 2
                                break
                    if ind != 0 and 'eedly' in stemming[ind:]:
                        stemming = stemming[:-5] + 'ee'
                    elif ind != 0 and 'eed' in stemming[ind:]:

                        stemming = stemming[:-3] + 'ee'

                elif stemming.endswith('ingly'):
                    temp_stem = stemming
                    if any(char in vowels for char in temp_stem[:-5]):
                        temp_stem = temp_stem[:-5]
                        if temp_stem.endswith('at') or temp_stem.endswith('bl') or temp_stem.endswith('iz'):
                            temp_stem = temp_stem + 'e'
                        elif temp_stem.endswith('bb') or temp_stem.endswith('dd') or temp_stem.endswith(
                                'ff') or temp_stem.endswith('gg') or temp_stem.endswith('mm') or temp_stem.endswith(
                            'nn') or temp_stem.endswith('pp') or temp_stem.endswith('rr') or temp_stem.endswith(
                            'tt'):
                            temp_stem = temp_stem[:-1]
                        elif temp_stem[0] in vowels and temp_stem[1] not in vowels:
                            temp_stem = temp_stem + 'e'
                        elif temp_stem[0] not in vowels:
                            ind = 0
                            for j in range(1, len(temp_stem)):
                                if temp_stem[j] in vowels:
                                    ind = j
                                    break
                            if ind != 0 and ind < (len(temp_stem) - 1) and temp_stem[ind + 1] not in vowels and \
                                    temp_stem[ind + 1] != 'x' and temp_stem[ind + 1] != 'w' and ind + 1 == len(
                                temp_stem) - 1:
                                temp_stem = temp_stem + 'e'
                    stemming = temp_stem

                elif stemming.endswith('edly'):
                    temp_stem = stemming
                    if any(char in vowels for char in temp_stem[:-4]):
                        temp_stem = temp_stem[:-4]
                        if temp_stem.endswith('at') or temp_stem.endswith('bl') or temp_stem.endswith('iz'):
                            temp_stem = temp_stem + 'e'
                        elif temp_stem.endswith('bb') or temp_stem.endswith('dd') or temp_stem.endswith(
                                'ff') or temp_stem.endswith('gg') or temp_stem.endswith('mm') or temp_stem.endswith(
                            'nn') or temp_stem.endswith('pp') or temp_stem.endswith('rr') or temp_stem.endswith(
                            'tt'):
                            temp_stem = temp_stem[:-1]
                        elif temp_stem[0] in vowels and temp_stem[1] not in vowels:
                            temp_stem = temp_stem + 'e'
                        elif temp_stem[0] not in vowels:
                            ind = 0
                            for j in range(1, len(temp_stem)):
                                if temp_stem[j] in vowels:
                                    ind = j
                                    break
                            if ind != 0 and ind < (len(temp_stem) - 1) and temp_stem[ind + 1] not in vowels and \
                                    temp_stem[ind + 1] != 'x' and temp_stem[ind + 1] != 'w' and ind + 1 == len(
                                temp_stem) - 1:
                                temp_stem = temp_stem + 'e'
                    stemming = temp_stem

                elif stemming.endswith('ing'):
                    temp_stem = stemming
                    if any(char in vowels for char in temp_stem[:-3]):
                        temp_stem = temp_stem[:-3]
                        if temp_stem.endswith('at') or temp_stem.endswith('bl') or temp_stem.endswith('iz'):
                            temp_stem = temp_stem + 'e'
                        elif temp_stem.endswith('bb') or temp_stem.endswith('dd') or temp_stem.endswith(
                                'ff') or temp_stem.endswith('gg') or temp_stem.endswith('mm') or temp_stem.endswith(
                            'nn') or temp_stem.endswith('pp') or temp_stem.endswith('rr') or temp_stem.endswith(
                            'tt'):
                            temp_stem = temp_stem[:-1]
                        elif temp_stem[0] in vowels and temp_stem[1] not in vowels and len(temp_stem) == 2:
                            temp_stem = temp_stem + 'e'
                        elif temp_stem[0] not in vowels:
                            ind = 0
                            for j in range(1, len(temp_stem)):
                                if temp_stem[j] in vowels:
                                    ind = j
                                    break
                            if ind != 0 and ind < (len(temp_stem) - 1) and temp_stem[ind + 1] not in vowels and \
                                    temp_stem[ind + 1] != 'x' and temp_stem[ind + 1] != 'w' and ind + 1 == len(
                                temp_stem) - 1:
                                temp_stem = temp_stem + 'e'
                    stemming = temp_stem

                elif stemming.endswith('ed'):
                    temp_stem = stemming
                    if any(char in vowels for char in temp_stem[:-2]):
                        temp_stem = temp_stem[:-2]

                        if temp_stem.endswith('at') or temp_stem.endswith('bl') or temp_stem.endswith('iz'):
                            temp_stem = temp_stem + 'e'
                        elif temp_stem.endswith('bb') or temp_stem.endswith('dd') or temp_stem.endswith(
                                'ff') or temp_stem.endswith('gg') or temp_stem.endswith('mm') or temp_stem.endswith(
                            'nn') or temp_stem.endswith('pp') or temp_stem.endswith('rr') or temp_stem.endswith(
                            'tt'):
                            temp_stem = temp_stem[:-1]
                        elif temp_stem[0] in vowels and temp_stem[1] not in vowels and temp_stem.rfind(
                                temp_stem[1]) == len(temp_stem) - 1:
                            temp_stem = temp_stem + 'e'
                        elif temp_stem[0] not in vowels:
                            ind = 0
                            for j in range(1, len(temp_stem)):
                                if temp_stem[j] in vowels:
                                    ind = j
                                    break
                            if ind != 0 and ind < (len(temp_stem) - 1) and temp_stem[ind + 1] not in vowels and \
                                    temp_stem[ind + 1] != 'x' and temp_stem[ind + 1] != 'w' and ind + 1 == len(
                                temp_stem) - 1:
                                temp_stem = temp_stem + 'e'
                    stemming = temp_stem
                arr[i] = stemming
    return temp


def step_1c(l):
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    temp = l
    for line in temp:
        for arr in line:
            for i in range(1, len(arr)):
                stemming = arr[i]
                if stemming[-1] == 'y' and stemming[-2] not in vowels and stemming.rfind(stemming[-2]) != 0:
                    stemming = stemming[:-1] + 'i'
                arr[i] = stemming
    return temp


def tokens(inputF, prefix, tokenType, stopType, stemType):
    fle = gzip.open(inputF, 'rt')
    fleOut = open(prefix + '-tokens.txt', 'w')

    lst = []
    if tokenType == 'spaces':
        for line in fle:
            x = line.split()
            d = []
            for word in x:
                a = [word, word]
                d.append(a)
            lst.append(d)
    elif tokenType == 'fancy':
        for line in fle:
            x = line.split()
            d = []
            for word in x:
                ar = tokenize(word)
                d.append(ar)
            if len(d) != 0:
                lst.append(d)

    if stopType == 'yesStop':
        lst = stop(lst)
    if stemType == 'porterStem':
        lst = step_1a(lst)
        lst = step_1b(lst)
        lst = step_1c(lst)


    for line in lst:
        for arr in line:
            for word in arr:
                fleOut.write(word + ' ')
            fleOut.write('\n')

    heaps = open(prefix + '-heaps.txt', 'w')
    token_count = 0
    count = 0
    unique_count = 0
    x_axis = []
    y_axis = []
    visited = {}
    for line in lst:
        for arr in line:
            for word in arr[1:]:
                if len(arr)>1:
                    token_count = token_count + 1
                    if word not in list(visited.keys()):
                        unique_count = unique_count + 1
                        visited[word] = 1
                    else:
                        visited[word] += 1
                    count = count + 1
                if count == 10 or (line == lst[len(lst)-1] and arr == line[len(line)-1] and word == arr[len(arr)-1]):
                    x_axis.append(token_count)
                    y_axis.append(unique_count)
                    heaps.write(str(token_count) + ' ' + str(unique_count) + '\n')
                    count = 0

    plt.plot(x_axis,y_axis)
    plt.xlabel('Words in Collection')
    plt.ylabel('Words in Vocabulary')
    plt.savefig('heaps.jpg')

    sorted_tuples = sorted(visited.items(), key=lambda item: (-item[1], item[0]))
    sorted_dict = {k: v for k, v in sorted_tuples}

    stats = open(prefix+ '-stats.txt','w')
    stats.write(str(token_count) + '\n' + str(unique_count) + '\n')

    for key in list(sorted_dict.keys())[:100]:
        stats.write(key + ' ' + str(sorted_dict[key]) + '\n')


    fle.close()
    fleOut.close()
    heaps.close()
    stats.close()
if __name__ == '__main__':
    # Read arguments from command line; or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "sense-and-sensibility.gz"
    outputFilePrefix = sys.argv[2] if argv_len >= 3 else "SAS"
    tokenize_type = sys.argv[3] if argv_len >= 4 else "spaces"
    stoplist_type = sys.argv[4] if argv_len >= 5 else "noStop"
    stemming_type = sys.argv[5] if argv_len >= 6 else "noStem"

    # Below is stopword list
    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                    "was", "were", "with"]
    tokens(inputFile, outputFilePrefix, tokenize_type, stoplist_type, stemming_type)
