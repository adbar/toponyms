#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Adrien Barbaresi, 2015.
# https://github.com/adbar/toponyms


## TODO:
# sort and uniq output (meta)
# filter metadata with same values


from __future__ import print_function

import locale
from os import listdir
import re

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
directory = 'geonames'
metainfo = dict()
codesdict = dict()
seen_codes = set()

for filename in listdir(directory):
    path = directory + '/' + filename
    with open(path, 'r') as inputfh:
        for line in inputfh:
            columns = re.split('\t', line)
            # filters
            if len(columns[0]) < 1 or len(columns[1]) < 1:
                continue
            if columns[1].count(' ') > 3:
                continue
            if columns[7] == 'BANK' or columns[7] == 'BLDG' or columns[7] == 'HTL' or columns[7] == 'PLDR' or columns[7] == 'PS' or columns[7] == 'SWT' or columns[7] == 'TOWR':
                continue
            # check if exists in db
            if columns[0] in seen_codes:
                print ('WARN: code already seen', line)
                continue
            ## name, alternatenames, latitude, longitude, code, country, population
            # main
            if columns[1] not in codesdict:
                codesdict[columns[1]] = set()
            codesdict[columns[1]].add(columns[0])
            # alternatives
            alternatives = re.split(',', columns[3])
            if len(alternatives) > 0:
                for item in alternatives:
                    # filter non-German characters
                    if len(item) > 2 or re.match(r'[^\w -]+$', item, re.LOCALE):
                        continue
                    if item not in codesdict:
                        codesdict[item] = set()
                        codesdict[item].add(columns[0])
            metainfo[columns[0]] = (columns[4], columns[5], columns[6], columns[8], columns[14])
            seen_codes.add(columns[0])
 


#def writefile(filename, dictname):
#    with open(filename, 'w') as outfh:
#        for key in sorted(dictname):
#            outfh.write(key)
#            for item in dictname[key]:
#                outfh.write('\t' + item)
#            outfh.write('\n')

# writefile('geonames.filtered', places)


# control
with open('geonames-codes.dict', 'w') as out1:
    with open('geonames-meta.dict', 'w') as out2:
        for key in codesdict:
            #if len(key) > 1:
            out1.write (key)
            for item in codesdict[key]:
                out1.write ('\t' + item)
                out2.write (item)
                for metaelem in metainfo[item]:
                    out2.write ('\t' + metaelem)
                out2.write ('\n')
            out1.write ('\n')

