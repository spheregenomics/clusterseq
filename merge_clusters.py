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

# Clusters with <= the following edit distance will
# be combined with each other.
cluster_edit_distance_threshold = 2

histogram_bin_growth_factor = 1.4

import sys;

def edit_distance(a,b):
    s = 0
    assert(len(a) == len(b))
    for i in range(len(a)):
        if a[i] != b[i] and a[i] != 'N' and b[i] != 'N':
            s += 1
           
    return s

def cluster_name(a,b):
    assert(len(a) == len(b))
    n = ''
    for i in range(len(a)):
        if a[i] == b[i]:
            n = n + a[i]
        else:
            n = n + 'N'
    return n

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
keys = frozenset(keys)

# identify keys to be remapped
remapped_keys = dict()
counts = dict() # key => count(reads) mapping
for key in keys:
    counts[key] = 0
    for data in file_data:
        if key in data:
            counts[key] += data[key]

attached = 0;
reverse_sorted_keys = sorted(counts.iteritems(), key=lambda (k,v): (v,k))
for key1,val1 in sorted(counts.iteritems(), key=lambda (k,v): (v,k),reverse=True): #cluster center
    for key2,val2 in reverse_sorted_keys: #cluster attacher
        if key1 == key2:
            break
        if edit_distance(key1,key2) <= cluster_edit_distance_threshold:
            if key2 not in remapped_keys.keys():
                remapped_keys[key2] = key1
                if key1 not in remapped_keys.keys():
                    remapped_keys[key1] = key1
                print("Attaching " + key2 + " to cluster " + key1)
                attached += 1

# remove keys mapped to a cluster node that doesn't exist any more
keys_seen_once = set()
keys_seen_twice = set()
for orig_key,new_key in remapped_keys.items():
    if new_key not in keys_seen_once:
        keys_seen_once.add(new_key)
        continue
    if new_key not in keys_seen_twice:
        keys_seen_twice.add(new_key)

keys_seen_once = keys_seen_once - keys_seen_twice
removed = 0
for orig_key,new_key in remapped_keys.items():
    if new_key in keys_seen_once:
        del remapped_keys[orig_key]
        print("Removing orphan cluster mapping " + orig_key + " to " + new_key)
        removed += 1

print("Attached %d and removed %d" % (attached, removed))

# generate new names for cluster centers
remapped_names = dict()
for k,v in remapped_keys.items():
    if v in remapped_names:
        remapped_names[v] = cluster_name(k, remapped_names[v])
    else:
        remapped_names[v] = v
for k,v in remapped_names.items():
    print("Renaming %s as %s"% (k,v))

# now, actually merge
new_file_data = list()
for data in file_data:
    new_data = dict()
    for key in keys:
        if key in data:
            if key in remapped_keys:
                cluster_key = remapped_keys[key]
                cluster_name = remapped_names[cluster_key]
                if cluster_name in new_data:
                    new_data[cluster_name] += data[key]
                else:
                    new_data[cluster_name] = data[key]
            else:
                new_data[key] = data[key]
    new_file_data.append(new_data)
file_data = new_file_data

#regenerate keys list after clustering
keys = set()
for data in file_data:
    keys = keys.union(data.keys())
keys = frozenset(keys)

# write output
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


#histogram output
sizes = list()
for key in keys:
    ct = 0
    for data in file_data:
        if key in data:
            ct += data[key]
    sizes.append(ct)

sizes.sort()

outfile = open('merged_clusters_histogram.csv', 'w')
bin_size = 1.0

bins = list()
bins.append(1)
while bin_size < sizes[len(sizes)-1]:
    new_bin_size = bin_size * histogram_bin_growth_factor
    if int(bin_size) != int(new_bin_size):
        bins.append(int(bin_size))
    bin_size = new_bin_size
    
bins.append(int(bin_size))

bin_ct = 0
s = 0

for i in range(len(sizes)):
    while sizes[i] > bins[bin_ct+1] :
        if bins[bin_ct] != bins[bin_ct+1]:
            outfile.write("%d-%d,%d\n" % (bins[bin_ct], bins[bin_ct+1], s))
            s = 0
        bin_ct += 1
    s += sizes[i]

outfile.write("%d-%d,%d\n" % (bins[bin_ct], bins[bin_ct+1], s))
