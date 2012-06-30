##Purpose
ClusterSeq is a tool used to analyze the distribution of barcodes across multiple tagged samples.

##Description

ClusterSeq consists of two separate tools- an executable for filtering and clustering of barcode sequences, and a python script for comparing sequences 

###Cluster command (cluster.cpp)

The cluster command expects reads in a FASTQ format, and expects reads with the following format:

[tag][start_marker][data][end_marker]

Where tag is a multiplexing tag identified in a required taglist file (see format below), and start_marker and end_marker are constant sequences before and after the barcode data. These are specified as command line options.

When run, the cluster command separates each read by tag, then performs the following:

* Check for begin and end 'markers' identifying a valid barcode. Sequences with invalid tags are discarded.
* Cluster barcode sequences with a limited number of differences, in order to tolerate sequencing errors. The number of acceptable differences is specified on the command line.
* Write a file containing a list of all reads and quality strings for this tag. Each line of the file contains the data sequence, a tab, and the corresponding Phred quality.
* Write a file containing a list of barcodes identified, along with the number of similar barcodes found with this tag. This file is a CSV consisting of barcode data followed by the number of times this barcode occurs in the input data (with the current tag).

The taglist file should consist of one or more lines in the following format:

<pre>
[FASTQ_name1] [whitespace] [TAG1]
              [whitespace] [TAG2]
[FASTQ_name2] [whitespace] [TAG1]
              [whitespace] [TAG2]
</pre>

###Cluster comparison tool (merge_clusters.py)
The cluster merging tool combines the CSV output from multiple tags of the cluster tool so that the frequency of occurrence of barcodes can be compared across multiplexing tags. The files input t

##Compilation

With OpenMP:
g++ cluster.cpp -o cluster -O3 -fopenmp -DUSE_OPENMP
Without OpenMP:
g++ cluster.cpp -o cluster -O3

##Running
Usage is:
<pre>
cluster min_quality max_n_allowed num_diff_allowed FASTQ_name_no_ext [tag_file_name] [start_marker] [end_marker]
</pre>
For example:
<pre>
./cluster 30 2 2 SNP456 taglist.txt AAAAAAAA TTTTTT
</pre>
The name of the FASTQ input file should have no extension- this is also used to load the proper tags of from the taglist file.

The cluster comparison tool simply needs a list files to merge:
<pre>
./merge_clusters.py SNP456.CTAG_clusters.csv SNP456.ACGT_clusters.csv
</pre>

##Author contact
Lee Baker, VBI: leecb@vt.edu
David Mittelman, VBI: david.mittelman@vt.edu
