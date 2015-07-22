#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division

from collections import defaultdict
from io import StringIO, BytesIO
from lxml import etree, html
import re
# import ujson


filelist = ['schnitzler_anatol_1893.tcf.xml', 'schnitzler_else_1924.tcf.xml', 'schnitzler_liebelei_1896.tcf.xml', 'schnitzler_reigen_1903.tcf.xml', 'schnitzler_traumnovelle_1926.tcf.xml']
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
for filename in filelist:
    tree = etree.parse(filename, hparser)
    # build frequency dict
    tokens = defaultdict(int)
    for elem in tree.xpath('//token'):
        tokens[elem.text] += 1
    numtokens = len(tokens)
    print (numtokens)
    for elem in tree.xpath('//token'):
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
            #if elem.text == 'aus' or elem.text == 'bei' or elem.text == 'bis' or elem.text == 'durch' or elem.text == 'in' or elem.text == 'nach' or elem.text == u'über' or elem.text == 'von' or elem.text == 'zu':
                # print (elem.text)
                # flag = True
            flag = True
        else:
            if len(elem.text) > 3 and elem.text in places and not re.match(r'[a-z]', elem.text) and elem.text not in wiktionary and elem.text.lower() not in wiktionary and (tokens[elem.text]/numtokens) < threshold:
                # store in dict
                if elem.text in occurrences:
                    occurrences[elem.text][3] += 1
                else:
                    occurrences[elem.text] = [places[elem.text][0], places[elem.text][1], '{0:.4f}'.format(tokens[elem.text]/numtokens), 1]
                # print (elem.text, places[elem.text][0], places[elem.text][1], '{0:.4f}'.format(tokens[elem.text]/numtokens))
                i += 1
                flag = False
            else:
                if tempstring:
                    tempstring = tempstring + ' ' + elem.text
                else:
                    tempstring = elem.text
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
