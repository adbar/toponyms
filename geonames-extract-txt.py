#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division

from collections import defaultdict
from io import StringIO, BytesIO
from lxml import etree, html
import re
# import ujson


places = dict()
occurrences = dict()
i = 0
hparser = etree.HTMLParser(encoding='utf-8')
flag = False
tempstring = ''
threshold = 0.001
wiktionary = set()

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
print (len(wiktionary))
#for item in sorted(wiktionary):
#    print (item)

# load places
with open('geonames.filtered', 'r') as dictfh:
    for line in dictfh:
        line = line.strip()
        columns = re.split('\t', line)
        #if columns[0] not in wiktionary:
        places[columns[0]] = [columns[2], columns[3]]
        for variant in columns[1].split(','):
            if variant:
                # print (variant)
                places[variant] = [columns[2], columns[3]]
print (len(places))

# search for places
with open('/home/adrien/Arbeitsfläche/dta-all.txt', 'r') as inputfh:
    splitted = inputfh.read().replace('\n', ' ').split()
    # build frequency dict
    tokens = defaultdict(int)
    for elem in splitted:
        tokens[elem] += 1
    numtokens = len(tokens)
    print (numtokens)
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
        if flag is False:
            #if elem == 'aus' or elem == 'bei' or elem == 'bis' or elem == 'durch' or elem == 'in' or elem == 'nach' or elem == u'über' or elem == 'von' or elem == 'zu':
                # print (elem)
                # flag = True
            flag = True
        else:
            if len(elem) > 3 and elem in places and not re.match(r'[a-z]', elem) and elem not in wiktionary and elem.lower() not in wiktionary and (tokens[elem]/numtokens) < threshold:
                # store in dict
                if elem in occurrences:
                    occurrences[elem][3] += 1
                else:
                    occurrences[elem] = [places[elem][0], places[elem][1], '{0:.4f}'.format(tokens[elem]/numtokens), 1]
                # print (elem, places[elem][0], places[elem][1], '{0:.4f}'.format(tokens[elem]/numtokens))
                i += 1
                flag = False
            else:
                if tempstring:
                    tempstring = tempstring + ' ' + elem
                else:
                    tempstring = elem
                if tempstring.count(' ') > 0 and tempstring in places:
                    # store in dict
                    if tempstring in occurrences:
                        occurrences[tempstring][3] += 1
                    else:
                        occurrences[tempstring] = [places[tempstring][0], places[tempstring][1], 0, 1]
                    # print (tempstring, places[tempstring][0], places[tempstring][1])
                    i += 1
                    tempstring = ''
                    flag = False


print (i)
for key in sorted(occurrences):
    print (key, occurrences[key])

with open('out.tsv', 'w') as outputfh:
    outputfh.write('place' + ' \t' + 'latitude' + ' \t' + 'longitude' + ' \t' + 'occurrences' + '\n')
    for key in sorted(occurrences):
        outputfh.write(key + ' \t' + str(occurrences[key][0]) + ' \t' + str(occurrences[key][1]) + ' \t' + str(occurrences[key][3]) + '\n')
