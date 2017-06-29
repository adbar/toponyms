#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) Adrien Barbaresi, 2015-2017.
# https://github.com/adbar/toponyms
# GNU GPLv3 license


## TODO:
# dates
# choice of canonical expression
# abbrv file: Sankt/St.
# lists of celebrities/other NEs
# filter 3: check coordinates
# memory issues


from __future__ import division, print_function, unicode_literals

import argparse
from collections import defaultdict
import exrex # regex expansion
from heapq import nlargest
from io import open, StringIO, BytesIO
from lxml import etree, html
from math import radians, cos, sin, asin, sqrt
from random import choice
import re
import sys
import time
# import ujson


## ARGS

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputfile', dest='inputfile', help='input file', required=True)
parser.add_argument('-o', '--outputfile', dest='outputfile', help='output file', required=True)
parser.add_argument('-f', '--filter', dest='filter', help='filter level')
parser.add_argument('--text', dest='text', action='store_true', help='text flag')
parser.add_argument('--tok', dest='tok', action='store_true', help='tokenized flag')
parser.add_argument('--xml', dest='xml', action='store_true', help='xml flag')
# parser.add_argument('--prepositions', dest='prepositions', action='store_true', help='prepositions switch')
parser.add_argument('--fackel', dest='fackel', action='store_true', help='Fackel switch')
parser.add_argument('--dta', dest='dta', action='store_true', help='DTA switch')
parser.add_argument('--dates', dest='dates', action='store_true', help='Dates switch')
parser.add_argument('--lines', dest='lines', action='store_true', help='Lines switch')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Verbosity switch')
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


## INIT

# can be changed
minlength = 4
if filter_level == 1:
    maxcandidates = 5 # was 10
elif filter_level == 2 or filter_level == 3:
    maxcandidates = 10 # was 10

# threshold = 1 # was 0.1 was 0.01 was 0.001
context_threshold = 20

# standard
codesdict = dict()
metainfo = dict()
results = dict()
if args.dates is True:
    datestok = dict()
level0 = dict()
level1 = dict()
level2 = dict()
level3 = dict()
level4 = dict()
i = 0
hparser = etree.HTMLParser(encoding='utf-8')
flag = False
slide2 = ''
slide3 = ''
lastcountry = ''
dictionary = set()
stoplist = set()
pair = list()
lines = list()
pair_counter = 0

if args.fackel is True:
    vicinity = set(['AT', 'BA', 'BG', 'CH', 'CZ', 'DE', 'HR', 'HU', 'IT', 'PL', 'RS', 'RU', 'SI', 'SK', 'UA'])
    reference = (float(48.2082), float(16.37169)) # Vienna
elif args.dta is True:
    vicinity = set(['AT', 'BE', 'CH', 'CZ', 'DK', 'FR', 'LU', 'NL', 'PL'])
    reference = (float(51.86666667), float(12.64333333)) # Wittenberg
else:
    print ('Specify either Fackel or DTA as reference')
    sys.exit(1)

# load normal dictionary
with open('wiktionary.json', 'r', encoding='utf-8') as dictfh:
    for line in dictfh:
        forms = re.findall(r'"(.+?)"', line)
        for form in forms:
            dictionary.add(form)
        # print (re.search('"word":"(.+?)"', line).group(1))
        # nominative = re.findall('"NOMINATIVE":\["(.+?)"', line)
        # for n in nominative:
        #     dictionary.add(n)
        # dative = re.findall('"DATIVE":\["(.+?)"', line)
        # for d in dative:
        #    dictionary.add(d)
print ('length dictionary:', len(dictionary))

# load extended blacklist
with open('stoplist', 'r') as dictfh:
    for line in dictfh:
        line = line.strip()
        stoplist.add(line)

def expand(expression):
    expresults = list(exrex.generate(expression))
    # no regex
    if len(expresults) == 1:
        results = list()
        results.append(expression)
        # genitive form if no s at the end of one component
        if not re.search(r's$', expression) and not re.search(r'\s', expression): 
            temp = expression + 's'
            results.append(temp)
        return results
    # serialize
    else:
        return expresults

def load_tsv(filename):
    d = dict()
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            line = line.strip()
            columns = re.split('\t', line)
            # sanity check
            if len(columns) == 3 and columns[1] is not None and columns[2] is not None:
                expansions = list()
                # strip
                for item in columns:
                    item = item.strip()
                # historical names
                if re.search(r';', columns[0]):
                    variants = re.split(r';', columns[0])
                    for item in variants:
                        expansions.extend(expand(item))
                else:
                    expansions.extend(expand(columns[0]))
                # append
                canonical = expansions[0]
                for variant in expansions:
                    d[variant] = [columns[1], columns[2], canonical]
                    if args.verbose is True:
                        print (variant, d[variant])
    return d

def load_csv(filename):
    d = dict()
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            line = line.strip()
            columns = re.split(',', line)
            if len(columns) == 4 and columns[2] is not None and columns[3] is not None:
                expansions = list()
                # strip
                for item in columns:
                    item = item.strip()
                # historical names
                if re.search(r';', columns[0]):
                    variants = re.split(r';', columns[0])
                    for item in variants:
                        expansions.extend(expand(item))
                else:
                    expansions.extend(expand(columns[0]))
                # current names
                if re.search(r';', columns[1]):
                    variants = re.split(r';', columns[1])
                    for item in variants:
                        expansions.extend(expand(item))
                else:
                    expansions.extend(expand(columns[1]))
                # canonical form?
                canonical = expansions[0]
                # process variants
                for variant in expansions:
                    # correction
                    if len(variant) > 1:
                        d[variant] = [columns[2], columns[3], canonical]
                        if args.verbose is True:
                            print (variant, d[variant])
    return d


# load infos level 0
level0 = load_tsv('rang0-makro.tsv')

# load infos level 1
level1 = load_tsv('rang1-staaten.tsv')

# load infos level 2
level2 = load_csv('rang2-regionen.csv')

# load infos level 3
level3 = load_csv('rang3-staedte.csv')

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
        # length filter
        if len(columns[0]) < minlength:
            continue
        # add codes
        for item in columns[1:]:
            # depends from filter level
            if item in metainfo:
                if columns[0] not in codesdict:
                    codesdict[columns[0]] = list()
                codesdict[columns[0]].append(item)
print ('different names:', len(codesdict))


# calculate distance
## source: http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points#4913653
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


# draw lines
def draw_line(lat, lon):
    global pair, lines, pair_counter
    if pair_counter <= context_threshold:
        if len(pair) == 1:
            pair.append((lat, lon))
            lines.append((pair[0], pair[1]))
            del pair[0]
        else:
            pair.append((lat, lon))
    else:
        pair = []
        pair.append((lat, lon))
    pair_counter = 0


# dict search
def filter_store(name, multiflag):
    # double check for stoplist
    if name in stoplist:
        return True
    # else
    global i, lastcountry, results
    winning_id = ''
    if name in codesdict:
        # single winner
        if not isinstance(codesdict[name], list) or len(codesdict[name]) == 1:
            winning_id = codesdict[name][0]
        else:
            # discard if too many
            if len(codesdict[name]) >= maxcandidates:
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
            if winning_id is None: ## NEVER HAPPENS??
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
        #if multiflag is False:
        #    freq = '{0:.4f}'.format(tokens[name]/numtokens)
        #else:
        #    freq = '0'
        freq = 'NULL'
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

        # lines flag
        if args.lines is True:
            draw_line(results[winning_id][0], results[winning_id][1])

        # result
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

    # search + canonicalize
    if name in level0:
        templist = [level0[name][0], level0[name][1], '0', 'NULL', 'NULL', level0[name][2]]
    elif name in level1:
        templist = [level1[name][0], level1[name][1], '1', 'NULL', 'NULL', level1[name][2]]
    elif name in level2:
        templist = [level2[name][0], level2[name][1], '2', 'NULL', 'NULL', level2[name][2]]
    elif name in level3:
        templist = [level3[name][0], level3[name][1], '3', 'NULL', 'NULL', level3[name][2]]
    # filter here?
    elif name not in dictionary and name.lower() not in dictionary and name in level4:
        templist = [level4[name][0], level4[name][1], '4', 'NULL', 'NULL', name] # level4[name][0]

    # canonical result
    if templist is not None:
        canonname = templist[-1]

    # results
    if templist is not None:
        # store whole result or just count
        if canonname not in results:
            # disable frequency count if multi-word on
            #if multiflag is False:
            #    freq = '{0:.4f}'.format(tokens[canonname]/numtokens)
            #else:
            #    freq = '0'
            freq = 'NULL'
            results[canonname] = templist
            results[canonname].append(freq)
            results[canonname].append(1)
        else:
            # increment last element
            results[canonname][-1] += 1
        # lines flag
        if args.lines is True:
            draw_line(templist[0], templist[1])
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
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
    elif args.tok is True:
        i = 0
        splitted = list()
        for line in inputfh:
            i += 1
            if i % 10000000 == 0:
                print (i)
            # consider dates
            if args.dates is True:
                columns = re.split('\t', line)
                if columns[0] not in datestok:
                    datestok[columns[0]] = set()
                datestok[columns[0]].add(columns[1])
            # take only first columns
            if re.search('\t', line):
                token = re.split('\t', line)[0]
            else:
                token = line.strip()
            splitted.append(token)
        # build frequency dict
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
# numtokens = len(tokens)
# print ('types:', numtokens)
print ('tokens:', len(splitted))

# search for places
for token in splitted:
    flag = True
    if token == ' ':
        continue
    # skip and reinitialize:
    if token == 'XXX' or re.match(r'[.,;:–]', token): # St.? -/–?
        slide2 = ''
        slide3 = ''
        continue
    ## grow or limit (delete first word)
    # 2-gram
    if len(slide2) == 0:
       slide2 = token
    elif slide2.count(' ') == 0:
       slide2 = slide2 + ' ' + token
    else:
       slide2 = re.sub(r'^.+? ', '', slide2)
       slide2 = slide2 + ' ' + token
    # 3-gram
    if len(slide3) == 0:
       slide3 = token
    #elif slide3.count(' ') < 1:
    #   slide3 = slide3 + ' ' + token
    elif slide3.count(' ') < 2:
       slide3 = slide3 + ' ' + token
    else:
       slide3 = re.sub(r'^.+? ', '', slide3)
       slide3 = slide3 + ' ' + token

    # control
    if args.verbose is True:
        print (token, slide2, slide3, sep=';')

    # flag test
    #if args.prepositions is True:
    #if multiword_flag is False:
    #    if token == 'aus' or token == 'bei' or token == 'bis' or token == 'durch' or token == 'in' or token == 'nach' or token == u'über' or token == 'von' or token == 'zu':
            # print (token)
    #        multiword_flag = True

    ## analyze sliding window first, then token if necessary
    # longest chain first
    if len(slide3) > 0 and slide3.count(' ') == 2:
        # selected lists first
        flag = selected_lists(slide3, True)
        # if nothing has been found
        if flag is True:
            flag = filter_store(slide3, True)
    # longest chain first
    if flag is True and len(slide2) > 0 and slide2.count(' ') == 1:
        # selected lists first
        flag = selected_lists(slide2, True)
        # if nothing has been found
        if flag is True:
            flag = filter_store(slide2, True)
    # just one token, if nothing has been found
    if flag is True:
        if len(token) >= minlength and not re.match(r'[a-zäöü]', token) and token not in stoplist:
        # and (tokens[token]/numtokens) < threshold
            flag = selected_lists(token, False)
            # dict check before
            if flag is True and token not in dictionary and token.lower() not in dictionary:
                flag = filter_store(token, False)
        
    # final check whether to keep the multi-word scan running
    if flag is False:
        slide2 = ''
        slide3 = ''

    #            if re.match(r'[A-ZÄÖÜ]', token, re.UNICODE):
    #                tempstring = token

    pair_counter += 1



print ('results:', len(results))
with open(args.outputfile, 'w', encoding='utf-8') as outputfh:
    outputfh.write('id' + '\t' + 'latitude' + '\t' + 'longitude' + '\t' + 'type' + '\t' + 'country' + '\t' + 'population' + '\t' + 'place' + '\t' + 'frequency' + '\t' + 'occurrences')
    if args.dates is True:
        outputfh.write('\t' + 'dates' + '\n')
    else:
        outputfh.write('\n')
    
    for key in sorted(results):
        outputfh.write(key)
        for item in results[key]:
            if isinstance(item, list):
                for subelement in item:
                    outputfh.write('\t' + str(subelement))
                # dates
                if args.dates is True:
                    if item[6] in datestok:
                    # filter century
                        dates = datestok[item[6]]
                        if len(dates) == 1:
                            outputfh.write('\t' + dates[0])
                        else:
                            outputfh.write('\t' + '|'.join(dates))
                    else:
                        outputfh.write('\t' + '0')
            else:
                outputfh.write('\t' + str(item))
        outputfh.write('\n')

if args.lines is True:
    with open('testlines.json', 'w') as outputfh:
        outputfh.write('{"type": "FeatureCollection","features": [')
        i = 1
        threshold = int(len(lines)/10) # https://github.com/alexpreynolds/colormaker
        color = 1
        #r = 0
        #g = 255
        #b = 255
        for l in lines:
            (lat1, lon1) = l[0]
            (lat2, lon2) = l[1]
            # htmlcolor = "#%02x%02x%02x" % (r,g,b)
            if i > 1:
                outputfh.write(',')
            outputfh.write('{"geometry": {"type": "LineString", "coordinates":[[')
            outputfh.write(lon1 + ',' + lat1 + '],[' + lon2 + ',' + lat2 + ']]')
            outputfh.write('},"type": "Feature", "properties": { "arc":' + str(i) + ',')
            outputfh.write(' "start": "' + lon1 + ',' + lat1 + '", "end": "' + lon2 + ',' + lat2 + '", ' )
            outputfh.write('"htmlcolor": "' + str(color) + '"}}')

            i += 1
            # affect color spectrum
            if i % threshold == 0:
                color += 1
                # g -= 1


        outputfh.write(']}')
