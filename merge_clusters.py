#!/usr/bin/python
#
# Merge clustered output files generated by the attached cluster.cpp code.
#
# Usage: ./merge_clusters.py file_1 file_2 file_3 file_n
#
# Author: Lee Baker, VBI
#         leecb@vt.edu
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
    filtered = False
    line = key
    for data in file_data:
        if key in data:
            line += ",%s" % data[key]
            if data[key] < min_count_for_filter:
                filtered = True
        else:
            line += ",0"
            if min_count_for_filter > 0:
                filtered = True
    outfile.write(line + '\n')
    if not filtered:
        outfile_filtered.write(line + '\n')
