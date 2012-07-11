#!/usr/bin/python
#
# merge_clusters2.py
# Part of the clusterseq tool
# Merge clustered output files generated by the attached cluster.cpp code.
#
# Author: Lee C. Baker, VBI
# Last modified: 11 July 2012
#
# Author: Lee Baker, VBI
#         leecb@vt.edu
#
# See https://github.com/adaptivegenome/clusterseq for more information.
#
# This file is released under the Virginia Tech Non-Commercial 
# Purpose License. A copy of this license has been provided as 
# LICENSE.txt.
#
###
#
# Usage: ./merge_clusters.py file_1 file_2 file_3 file_n
#
# For the filtered output file, we eliminate any sequence
# that has less than this number of reads in ANY of the input
# files.
min_count_for_filter = 3

import sys;

file_data = list()
for f in sys.argv[1:]:
    data = dict()
    txt = open(f, 'r').read()
    lines = txt.split('\n')
    for l in lines:
        d = l.split(',')
        if(len(d) != 2):
            continue;
        data[d[0]] = int(d[1])
    file_data.append(data)

keys = set()
for data in file_data:
    keys = keys.union(data.keys())

header = "sequence," + ','.join(sys.argv[1:]) + '\n'

outfile = open('merged_clusters.csv', 'w')
outfile_filtered = open('merged_clusters_filtered.csv', 'w')
outfile.write(header)
outfile_filtered.write(header)
for key in keys:
    keep = False
    line = key
    for data in file_data:
        if key in data:
            line += ",%s" % data[key]
            if int(data[key]) >= min_count_for_filter:
                keep = True
        else:
            line += ",0"
    outfile.write(line + '\n')
    if keep:
        outfile_filtered.write(line + '\n')