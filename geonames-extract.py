#!/usr/bin/python
# -*- coding: utf-8 -*-


## TODO:
# FIX broken types!
# filter pop
# problem line 150


from __future__ import print_function
from __future__ import division

import argparse
from collections import defaultdict
from io import StringIO, BytesIO
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
i = 0
hparser = etree.HTMLParser(encoding='utf-8')
flag = False
tempstring = ''
lastcountry = ''
threshold = 0.01 # was 0.001
wiktionary = set()
blacklist = set(['Alle', 'Aller', 'Alles', 'Amerika', 'Auch', 'Classe', 'Darum', 'Dich', 'Diesen', 'Drum', 'Ferdinand', 'Franz', 'Grade', 'Grazie', 'Großen', 'Gunsten', 'Hier', 'Ihnen', 'Jene', 'Jenen', 'Leuten', 'Meine', 'Noth', 'Ohne', 'Oskar', 'Sich', 'Sind', 'Weil'])

if args.fackel is True:
    vicinity = set(['AT', 'BA', 'BG', 'CH', 'CZ', 'DE', 'HR', 'HU', 'IT', 'PL', 'RS', 'RU', 'SI', 'SK', 'UA'])
    reference = (float(48.2082), float(16.37169)) # Vienna

# load normal dictionary
with open('wiktionary.json', 'r') as dictfh:
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

# load extended blacklists
with open('vornamen-historisch', 'r') as dictfh:
    for line in dictfh:
        blacklist.add(line.strip())
with open('vor+nachnamen-aktuell', 'r') as dictfh:
    for line in dictfh:
        blacklist.add(line.strip())

# load infos: combine?
with open('geonames-meta.dict', 'r') as inputfh:
    for line in inputfh:
        line = line.strip()
        columns = re.split('\t', line)
        # filter: skip elements
        if filter_level == 1 :
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

# load while implementing filter
with open('geonames-codes.dict', 'r') as inputfh:
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
    # points: distance, population, vicinity, last country seen
    scores = dict()
    distances = dict()
    # step 2: filter places with no population
    if step == 2:
        for candidate in candidates:
            try:
                if int(metainfo[candidate][4]) == 0:
                    candidates.remove(candidate)
            except KeyError:
                print ('ERROR, Key:', candidate)
    # avoid single items
    if len(candidates) == 1:
        return candidates[0]
    # double entries: place + administrative region
    elif len(candidates) == 2:
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
        try:
            distances[candidate] = haversine(reference[0], reference[1], float(metainfo[candidate][0]), float(metainfo[candidate][1]))
        except KeyError:
            # filter problem
            print ('ERROR, Key:', candidate)
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
    global i, lastcountry
    # blacklist
    if name in blacklist:
        return True
    if name in codesdict:
        # single winner
        if len(codesdict[name]) == 1:
            winning_id = codesdict[name][0]
        else:
            # 3-step filter, or while?
            winners = find_winner(codesdict[name], 1)
            if winners is not None and len(winners) == 1:
                winning_id = winners[0]
            else:
                winners = find_winner(winners, 2)
                if winners is not None and len(winners) == 1:
                    winning_id = winners[0]
                else:
                    winners = find_winner(winners, 3)
                    if winners is not None and len(winners) == 1:
                        winning_id = winners[0]
                    else:
                        # not found
                        return True
        # throw dice and record
        #if len(winning_id) == 0:
        #    for element in best_ones:
        #        print (name, element, scores[element], distances[element], str(metainfo[element]), sep='\t')
        #        i += 1
            # random choice to store...
        #    winning_id = choice(best_ones)
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
                print ('ERROR not found:', winning_id)
                return False
            results[winning_id].append(name)
            results[winning_id].append(freq)
            results[winning_id].append(1)
        else:
            results[winning_id][-1] += 1
        lastcountry = metainfo[winning_id][3]
        return False
    else:
        # not found
        return True


# search for places
with open(args.inputfile, 'r') as inputfh:
    if args.text is True:
        splitted = inputfh.read().replace('\n', ' ').split()
        # build frequency dict
        tokens = defaultdict(int)
        for elem in splitted:
            tokens[elem] += 1
    elif args.tok is True:
        splitted = list()
        for line in inputfh:
            if re.search('\t', line):
                token = re.split('\t', line)[0]
            else:
                token = line.strip()
            splitted.append(token)
        # build frequency dict
        tokens = defaultdict(int)
        for elem in splitted:
            tokens[elem] += 1

# 
numtokens = len(tokens)
print ('types:', numtokens)
for elem in splitted:
    # reinitialize
    if tempstring.count(' ') >= 3:
        #try:
        #    print (tempstring)
        #except UnicodeEncodeError:
        #    pass
        tempstring = ''
        flag = False
    # flag test
    #if args.prepositions is True:
    #if flag is False:
    #    if elem == 'aus' or elem == 'bei' or elem == 'bis' or elem == 'durch' or elem == 'in' or elem == 'nach' or elem == u'über' or elem == 'von' or elem == 'zu':
            # print (elem)
    #        flag = True
    #else:
    if True:
        if len(elem) > 3 and not re.match(r'[a-z]', elem) and elem not in wiktionary and elem.lower() not in wiktionary and (tokens[elem]/numtokens) < threshold:
            # filter and store
            flagresult = filter_store(elem, False)
            flag = flagresult
        else:
            if tempstring:
                tempstring = tempstring + ' ' + elem
            else:
                if re.match(r'[A-ZÄÖÜ]', elem, re.UNICODE):
                    tempstring = elem
            if tempstring.count(' ') > 0:
                # filter and store
                flagresult = filter_store(tempstring, True)
                flag = flagresult
                if flag is False:
                    tempstring = ''

print (i)

with open(args.outputfile, 'w') as outputfh:
    outputfh.write('id' + '\t' + 'latitude' + '\t' + 'longitude' + '\t' + 'type' + '\t' + 'country' + '\t' + 'population' + '\t' + 'place' + '\t' + 'frequency' + '\t' + 'occurrences' + '\n')
    for key in sorted(results):
        outputfh.write(key)
        for item in results[key]:
            if isinstance(item, list):
                for subelement in item:
                    outputfh.write('\t' + str(subelement))
            else:
                outputfh.write('\t' + str(item))
        outputfh.write('\n')
