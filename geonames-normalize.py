#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function

from os import listdir
import re


directory = 'geonames'
places = dict()

def store(values):
    global places_adm, places_pop, places_all
    places[values[1]] = (values[3], values[4], values[5])

for filename in listdir(directory):
    path = directory + '/' + filename
    with open(path, 'r') as inputfh:
        for line in inputfh:
            columns = re.split('\t', line)
            # filters
            if columns[1].count(' ') > 3:
                continue
            if columns[7] == 'BANK' or columns[7] == 'BLDG' or columns[7] == 'HTL' or columns[7] == 'PLDR' or columns[7] == 'PS' or columns[7] == 'SWT' or columns[7] == 'TOWR':
                continue
            # name, alternatenames, latitude, longitude
            # dict check
            if columns[1] not in places:
                store(columns)
            else:
                # if more alternatives
                if len(columns[3]) > len(places[columns[1]][0]):
                    store(columns)
                else:
                    # if more precise coordinates
                    if len(columns[4]) > len(places[columns[1]][1]) and len(columns[5]) > len(places[columns[1]][2]):
                        store(columns)


for key in sorted(places):
    print (key, places[key][0], places[key][1], places[key][2], sep='\t')
#print (columns[1], columns[3], columns[4], columns[5], sep='\t')




