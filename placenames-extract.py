#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Adrien Barbaresi, 2015.
# https://github.com/adbar/toponyms


## TODO:
# multi-word expression logic
# levels 1, 2, and 3: variants coding
# year switch
# lists of celebrities
# mehrwortausdrücken first
# memory
# Genitiv
# filter 3: check coordinates


from __future__ import print_function
from __future__ import division

import argparse
from collections import defaultdict
from heapq import nlargest
from io import open, StringIO, BytesIO
from lxml import etree, html
from math import radians, cos, sin, asin, sqrt
from random import choice
import re
import sys
import time
# import ujson


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputfile', dest='inputfile', help='input file', required=True)
parser.add_argument('-o', '--outputfile', dest='outputfile', help='output file', required=True)
parser.add_argument('-f', '--filter', dest='filter', help='filter level')
parser.add_argument('--text', dest='text', action='store_true', help='text flag')
parser.add_argument('--tok', dest='tok', action='store_true', help='tokenized flag')
parser.add_argument('--xml', dest='xml', action='store_true', help='xml flag')
# parser.add_argument('--prepositions', dest='prepositions', action='store_true', help='prepositions switch')
parser.add_argument('--fackel', dest='fackel', action='store_true', help='Fackel switch')
parser.add_argument('--year', dest='year', action='store_true', help='Year switch')
args = parser.parse_args()

if args.xml is True:
    print ('XML switch not implemented yet')

if args.filter:
    try:
        filter_level = int(args.filter)
        if filter_level < 1 or filter_level > 3:
            print ('The filter argument must be 1, 2, or 3')
            sys.exit(1)
    except ValueError:
        print ('The filter argument must be an integer')
        sys.exit(1)
else:
    filter_level = 0

args.fackel = True
print ('## Fackel flag True by default')

codesdict = dict()
metainfo = dict()
results = dict()
level0 = dict()
level1 = dict()
level2 = dict()
level3 = dict()
level4 = dict()
i = 0
hparser = etree.HTMLParser(encoding='utf-8')
multiword_flag = False
tempstring = ''
lastcountry = ''
threshold = 1 # was 0.1 was 0.01 was 0.001
wiktionary = set()
blacklist = set(['Alle', 'Aller', 'Alles', 'Amerika', 'Auch', 'Beim', 'Beste', 'Centrum', 'Classe', 'Darum', 'Dich', 'Dies', 'Diesen', 'Doch', 'Drum', 'Eine', 'Einem', 'Einen', 'Eines', 'Ferdinand', 'Franz', 'Gern', 'Grade', 'Grazie', 'Großen', 'Gunsten', 'Hatten', 'Hellen', 'Hier', 'Ihnen', 'Ihren', 'Ihrer', 'Immer', 'Jene', 'Jenen', 'Leuten', 'Manche', 'Meine', 'Noth', 'Ohne', 'Oskar', 'Seit', 'Shaw', 'Sich', 'Sind', 'Weil'])
# special modern
blacklist.add('Coole')
blacklist.add('Lasse')
blacklist.add('Naja')
blacklist.add('Sona')

if args.fackel is True:
    vicinity = set(['AT', 'BA', 'BG', 'CH', 'CZ', 'DE', 'HR', 'HU', 'IT', 'PL', 'RS', 'RU', 'SI', 'SK', 'UA'])
    reference = (float(48.2082), float(16.37169)) # Vienna

# load normal dictionary
with open('wiktionary.json', 'r', encoding='utf-8') as dictfh:
    for line in dictfh:
        forms = re.findall(r'"(.+?)"', line)
        for form in forms:
            wiktionary.add(form)
        # print (re.search('"word":"(.+?)"', line).group(1))
        # nominative = re.findall('"NOMINATIVE":\["(.+?)"', line)
        # for n in nominative:
        #     wiktionary.add(n)
        # dative = re.findall('"DATIVE":\["(.+?)"', line)
        # for d in dative:
        #    wiktionary.add(d)
print ('length dictionary:', len(wiktionary))

# load extended blacklist
with open('stoplist', 'r') as dictfh:
    for line in dictfh:
        blacklist.add(line.strip())


# load infos level 0
with open('rang0-makro.tsv', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split('\t', line)
        if len(columns) == 3 and columns[1] is not None and columns[2] is not None:
            # strip
            for item in columns:
                item = item.strip()
            # historical names
            if re.search(r';', columns[0]):
                variants = re.split(r';', columns[0])
                standard = variants[0]
                for item in variants:
                    level0[item] = [columns[1], columns[2], standard]
            else:
                level0[columns[0]] = [columns[1], columns[2], columns[0]]
            # genitive
            # level1[columns[0] + 's'] = [columns[1], columns[2], 1]

# load infos level 1
with open('rang1-staaten.tsv', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split('\t', line)
        if len(columns) == 3 and columns[1] is not None and columns[2] is not None:
            # strip
            for item in columns:
                item = item.strip()
            # historical names
            if re.search(r';', columns[0]):
                variants = re.split(r';', columns[0])
                standard = variants[0]
                for item in variants:
                    level1[item] = [columns[1], columns[2], standard]
            else:
                level1[columns[0]] = [columns[1], columns[2], columns[0]]
            # genitive
            # level1[columns[0] + 's'] = [columns[1], columns[2], 1]

# load infos level 2
with open('rang2-regionen.csv', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split(',', line)
        if len(columns) == 4 and columns[2] is not None and columns[3] is not None:
            # strip
            for item in columns:
                item = item.strip()
            # historical names
            if re.search(r';', columns[0]):
                variants = re.split(r';', columns[0])
                standard = variants[0]
                for item in variants:
                    level2[item] = [columns[2], columns[3], standard]
            else:
                standard = columns[0]
                level2[columns[0]] = [columns[2], columns[3], columns[0]]
            # current names
            if re.search(r';', columns[1]):
                variants = re.split(r';', columns[1])
                for item in variants:
                    level2[item] = [columns[2], columns[3], standard]
            else:
                level2[columns[1]] = [columns[2], columns[3], standard]

# load infos level 3
with open('rang3-staedte.csv', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split(',', line)
        if len(columns) == 4 and columns[2] is not None and columns[3] is not None:
            # strip
            for item in columns:
                item = item.strip()
            # historical names
            if re.search(r';', columns[0]):
                variants = re.split(r';', columns[0])
                standard = variants[0]
                for item in variants:
                    level3[item] = [columns[2], columns[3], standard]
            else:
                standard = columns[0]
                level3[columns[0]] = [columns[2], columns[3], columns[0]]
            # current names
            if re.search(r';', columns[1]):
                variants = re.split(r';', columns[1])
                for item in variants:
                    level3[item] = [columns[2], columns[3], standard]
            else:
                level3[columns[1]] = [columns[2], columns[3], standard]

# load infos level 4
with open('rang4-geographie.tsv', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split('\t', line)
        if len(columns) == 3 and columns[1] is not None and columns[2] is not None:
            level4[columns[0]] = [columns[1], columns[2]]

# geonames
with open('geonames-meta.dict', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split('\t', line)
        # no empty places at filter levels 1 & 2
        if filter_level == 1 or filter_level == 2:
            if columns[5] == '0':
                continue
        # filter: skip elements
        if filter_level == 1:
            if columns[3] != 'A':
                continue
        elif filter_level == 2:
            if columns[3] != 'A' and columns[3] != 'P':
                continue
        # process
        metainfo[columns[0]] = list()
        for item in columns[1:]:
            metainfo[columns[0]].append(item)
print ('different codes:', len(metainfo))

# load codes (while implementing filter)
with open('geonames-codes.dict', 'r', encoding='utf-8') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split('\t', line)
        for item in columns[1:]:
            # depends from filter level
            if item in metainfo:
                if columns[0] not in codesdict:
                    codesdict[columns[0]] = list()
                codesdict[columns[0]].append(item)
print ('different names:', len(codesdict))


# calculate distance
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return "{0:.1f}".format(km)

def find_winner(candidates, step):
    # test if list
    if not isinstance(candidates, list):
        print ('ERROR: not a list', candidates)
        return candidates
    # avoid single items
    if len(candidates) == 1:
        return candidates[0]

    # decisive argument: population
    headcounts = list()
    popdict = dict()
    for candidate in candidates:
        headcounts.append(metainfo[candidate][4])
        popdict[metainfo[candidate][4]] = candidate
    largest = nlargest(2, headcounts)
    # all null but one
    if largest[0] != 0 and largest[1] == 0:
        return popdict[largest[0]]
    # second-largest smaller by a factor of 1000
    if largest[0] > 1000*largest[1]:
        return popdict[largest[0]]

    # points: distance, population, vicinity, last country seen
    scores = dict()
    distances = dict()
    # step 2: filter places with no population
    if step == 2:
        for candidate in candidates:
            if int(metainfo[candidate][4]) == 0:
                candidates.remove(candidate)
    # double entries: place + administrative region
    if len(candidates) == 2:
        if metainfo[candidates[0]][2] == 'A' and metainfo[candidates[1]][2] == 'P':
            return candidates[1]
        elif metainfo[candidates[0]][2] == 'P' and metainfo[candidates[1]][2] == 'A':
            return candidates[0]
    # last country code seen
    #if lastcountry is not None:
    #    if metainfo[item][3] == lastcountry:
    #        scores[item] += 1

    # tests
    for candidate in candidates:
        # init
        scores[candidate] = 0
        # distance: lat1, lon1, lat2, lon2
        distances[candidate] = haversine(reference[0], reference[1], float(metainfo[candidate][0]), float(metainfo[candidate][1]))
        # population
        if int(metainfo[candidate][4]) > 1000:
            scores[candidate] += 1
        # vicinity
        if metainfo[candidate][3] in vicinity:
            scores[candidate] += 1
    # best distance
    smallest_distance = min(distances.values())
    for number in [k for k,v in distances.items() if v == smallest_distance]:
        scores[number] += 1
    # best score
    best_score = max(scores.values())
    best_ones = [k for k,v in scores.items() if v == best_score]
    # analyze
    if len(best_ones) == 1:
        #if isinstance(best_ones, list):
        return best_ones[0]
        #else:
        #    lastcountry = metainfo[best_ones][3]
    if len(best_ones) == 2:
        # double entries: place + administrative region
        if metainfo[best_ones[0]][2] == 'A' and metainfo[best_ones[1]][2] == 'P':
            return best_ones[1]
        elif metainfo[best_ones[0]][2] == 'P' and metainfo[best_ones[1]][2] == 'A':
            return best_ones[0]

# dict search
def filter_store(name, multiflag):
    global i, lastcountry, results
    winning_id = ''
    if name in codesdict:
        # single winner
        if not isinstance(codesdict[name], list) or len(codesdict[name]) == 1:
            winning_id = codesdict[name][0]
        else:
            # discard if too many
            if len(codesdict[name]) >= 10:
                try:
                    print ('WARN, discarded:', name, codesdict[name])
                except UnicodeEncodeError:
                    print ('WARN, discarded:', 'unicode error', codesdict[name])
                return True
            # 3-step filter
            step = 1
            while (step <= 3):
                # launch function
                if step == 1:
                    winners = find_winner(codesdict[name], step)
                else:
                    winners = find_winner(winners, step)
                # analyze result
                if winners is None:
                    try:
                        print ('ERROR, out of winners:', name, codesdict[name])
                    except UnicodeEncodeError:
                        print ('ERROR, out of winners:', 'unicode error', codesdict[name])
                    i += 1
                    return True
                if not isinstance(winners, list):
                    winning_id = winners
                    break
                # if len(winners) == 1
            if winning_id is None:
                try:
                    print ('ERROR, too many winners:', name, winners)
                except UnicodeEncodeError:
                    print ('ERROR, too many winners:', 'unicode error', winners)

                i += 1
                return True

        # throw dice and record
        #if len(winning_id) == 0:
        #    for element in best_ones:
        #        print (name, element, scores[element], distances[element], str(metainfo[element]), sep='\t')
        #        i += 1
            # random choice to store...
        #    winning_id = choice(best_ones)

        # disable frequency count if multi-word on
        if multiflag is False:
            freq = '{0:.4f}'.format(tokens[name]/numtokens)
        else:
            freq = '0'
        # store result
        if winning_id not in results:
            results[winning_id] = list()
            try:
                for element in metainfo[winning_id]:
                    results[winning_id].append(element)
            except KeyError:
                print ('ERROR, not found:', winning_id)
                return True
            results[winning_id].append(name)
            results[winning_id].append(freq)
            results[winning_id].append(1)
        else:
            # increment last element
            results[winning_id][-1] += 1
        lastcountry = metainfo[winning_id][3]
        return False
    else:
        # not found
        # print ('ERROR, not found:', name)
        return True


## search in selected databases
def selected_lists(name, multiflag):
    # init
    global results
    templist = None

    # search (+ genitive)
    if name in level0:
        templist = [level0[name][0], level0[name][1], '1', 'NULL', 'NULL', level0[name][2]]
    elif name in level1:
        templist = [level1[name][0], level1[name][1], '1', 'NULL', 'NULL', level1[name][2]]
    elif name in level2:
        templist = [level2[name][0], level2[name][1], '2', 'NULL', 'NULL', level2[name][2]]
    elif name not in wiktionary and name.lower() not in wiktionary:
        if name in level3:
            templist = [level3[name][0], level3[name][1], '3', 'NULL', 'NULL', level3[name][2]]
        elif name in level4:
            templist = [level4[name][0], level4[name][1], '4', 'NULL', 'NULL', name]

    # results
    if templist is not None:
        # store whole result or just count
        if name not in results:
            # disable frequency count if multi-word on
            if multiflag is False:
                freq = '{0:.4f}'.format(tokens[name]/numtokens)
            else:
                freq = '0'
            results[name] = templist
            results[name].append(freq)
            results[name].append(1)
        else:
            # increment last element
            results[name][-1] += 1
        # store flag
        return False
    else:
        return True

            


# load all tokens

with open(args.inputfile, 'r', encoding='utf-8') as inputfh:
    if args.text is True:
        # splitted = inputfh.read().replace('\n', ' ').split()
        text = inputfh.read().replace('\n', ' ')
        # very basic tokenizer
        splitted = re.split(r'([^\w-]+)', text, flags=re.UNICODE) # [ .,;:]
        # build frequency dict
        tokens = defaultdict(int)
        for elem in splitted:
            tokens[elem] += 1
    elif args.tok is True:
        i = 0
        splitted = list()
        for line in inputfh:
            i += 1
            if i % 10000000 == 0:
                print (i)
            if re.search('\t', line):
                token = re.split('\t', line)[0]
            else:
                token = line.strip()
            splitted.append(token)
        # build frequency dict
        tokens = defaultdict(int)
        for elem in splitted:
            tokens[elem] += 1
numtokens = len(tokens)
print ('types:', numtokens)

# search for places
for token in splitted:
    # skip and reinitialize:
    if token == 'XXX' or token == '.' or token ==',' or token in blacklist:
        tempstring = ''
        multiword_flag = False
        continue
    # reinitialize
    if tempstring.count(' ') >= 3:
        tempstring = ''
        multiword_flag = False
    # build tempstring
    else:
        tempstring = tempstring + ' ' + token
        multiword_flag = True

    # flag test
    #if args.prepositions is True:
    #if multiword_flag is False:
    #    if token == 'aus' or token == 'bei' or token == 'bis' or token == 'durch' or token == 'in' or token == 'nach' or token == u'über' or token == 'von' or token == 'zu':
            # print (token)
    #        multiword_flag = True

    ## analyze tempstring first, then token if necessary

    # name_s = re.sub(r's$', '', name)

    if len(tempstring) > 0:
        # selected lists first
        multiword_flag = selected_lists(tempstring, True)
        # if nothing has been found
        if multiword_flag is True:
            multiword_flag = filter_store(tempstring, True)
    # just one token, if nothing has been found
    if len(tempstring) == 0 or multiword_flag is True:
        if len(token) > 3 and not re.match(r'[a-z]', token) and (tokens[token]/numtokens) < threshold:
            multiword_flag = selected_lists(token, False)
            if multiword_flag is True and token not in wiktionary and token.lower() not in wiktionary:
                multiword_flag = filter_store(token, False)
        
    # final check whether to keep the multi-word scan running
    if multiword_flag is False:
        tempstring = ''


    #    else:
    #        if tempstring:
    #            tempstring = tempstring + ' ' + token
    #        else:
    #            if re.match(r'[A-ZÄÖÜ]', token, re.UNICODE):
    #                tempstring = token
    #        if tempstring.count(' ') > 0:
    #            # filter and store
    #            multiword_flag = filter_store(tempstring, True)
    #            if multiword_flag is False:
    #                tempstring = ''

# print (i)

print ('results:', len(results))
with open(args.outputfile, 'w', encoding='utf-8') as outputfh:
    outputfh.write(u'id' + '\t' + u'latitude' + '\t' + u'longitude' + '\t' + u'type' + '\t' + u'country' + '\t' + u'population' + '\t' + u'place' + '\t' + u'frequency' + '\t' + u'occurrences' + '\n')
    for key in sorted(results):
        outputfh.write(unicode(key))
        for item in results[key]:
            if isinstance(item, list):
                for subelement in item:
                    outputfh.write(u'\t' + unicode(subelement))
            else:
                outputfh.write(u'\t' + unicode(item))
        outputfh.write(u'\n')
