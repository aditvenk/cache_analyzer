#!/usr/bin/env python
import getopt, sys, time, re
import matplotlib.pyplot as plt
plt.switch_backend('GTKAgg')
import numpy as np
import math
import counter

# global flags
enable_plots = 1
enable_profiling = 1
enable_bdi = 1
enable_fpc = 1
enable_unique_analysis = 1
enable_av_compression = 1
enable_markov_analysis = 1

#global lists for words, upper-words, lower-words etc.
g_words = []
g_upper_words = []
g_lower_words = []
g_i_u_words = []
g_i_l_words = []

av_l_words = []
av_u_words = []
l_cum_dist = []

#global counters for zero value lines, same value lines etc.
g_same_value_lines = 0
g_zero_lines = 0
g_narrow_value_lines = 0
g_aligned_value_lines = 0

# global list for num of narrow values in each line
g_num_narrow_list = []
g_num_aligned_list = []

# bdi analysis -- we will consider fixed base of 0 and one additional base
bases = [0]
# no. of lines which are compressible under bdi --> no. of compressed bits < no. of uncompressed bits
g_num_bdi_lines = 0
g_bdi_lines_list = []

# av_compression
av_comp_bits = 0

g_segments = range(1, 65)
dict_segments = {}

#fpc analysis
g_num_zeros = 0
g_num_4b_se = 0
g_num_8b_se = 0
g_num_2_hw_se = 0
g_num_hw_se = 0
g_num_hw_zp = 0
g_rep_byte = 0
g_uncompressible = 0

##!/s/python-2.7.3/bin/python
#64B line match
match_re = re.compile(r"^\s0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+) 0x([a-f0-9]+).*$")

def main():
	input_file = ""
	output_file = ""

	system = {}
	try:
		opts, args = getopt.getopt(sys.argv[1:],"i:o:", ["input=", "output="])
	except getopt.GetoptError:
		usage()

	for o, a in opts:
		if o in ("-i", "--input"):
			input_file = str(a);
		if o in ("-o", "--output"):
			output_file = str(a)
	if len(input_file) == 0:
		usage()
	if len(output_file) == 0:
		usage()
	print input_file
	FILE_IN = open(input_file, "r+")
	FILE_OUT = open(output_file, "wb")
	init_segment_dict()
	start_block = 0
	c = FILE_IN.read(1)
	while c :
		if c == '[':
			start_block = 1
			line = ''
		elif c == ']':
			start_block = 0
			line_analysis(line)
		if start_block:
			if c != '[' and c != ']':
				line = line + c
		c = FILE_IN.read(1)


	#print line
	FILE_IN.close()

	if enable_profiling :
		#analyse words for zeros, narrow values, repeated values.
		print "num of zero lines = %d " % (g_zero_lines)
		print "num of same value lines = %d " % g_same_value_lines
		print "num of narrow value lines = %d " % g_narrow_value_lines
		print "num of aligned value lines = %d " % g_aligned_value_lines

		# print histogram of narrow/aligned lines.
		bins=[0, 4, 8, 12, 16]
		print "Histogram of narrow lines"
		print np.histogram(g_num_narrow_list, bins)
		if (enable_plots):
			plt.title('Histogram of narrow lines (no. of narrow words within a line)')
			plt.ylabel('No. of lines')
			plt.xlabel('Buckets')
			plt.hist(g_num_narrow_list, bins)
			plt.show()


		print "Histogram of aligned lines"
		print np.histogram(g_num_aligned_list, bins)
		if (enable_plots):
			plt.title('Histogram of aligned lines (no. of aligned words within a line)')
			plt.ylabel('No. of lines')
			plt.xlabel('Buckets')
			plt.hist(g_num_aligned_list, bins)
			plt.show()

	if enable_bdi:
		# bdi outputs
		print "No. of bdi potential lines = ", g_num_bdi_lines
		print "Histogram of bdi lines"
		bins = [0, 4, 16, 32, 64, 64]
		print np.histogram(g_bdi_lines_list, bins)
		#if (enable_plots):
		#	plt.title('Histogram of bdi potential lines')
		#	plt.ylabel('No. of lines')
		#	plt.xlabel('Buckets')
		#	plt.hist(g_bdi_lines_list, bins)
		#	plt.show()

		# plot segments histogram
		#print "No. of segments per line: "
		#print dict_segments
		if (enable_plots):
			plt.figure(figsize=(20,10))
			plt.title('BDI - compressibility at byte granularity')
			plt.ylabel('No. of lines')
			plt.xlabel('Buckets')
			X = np.arange(len(dict_segments))
			plt.bar(X, dict_segments.values(),  width = 0.5)
			plt.xticks(X, dict_segments.keys())
			plt.show()

	if enable_fpc:
		print "FPC pattern analysis: "
		print "Num of zero words = %d" % g_num_zeros
		print "Num of 4-bit sign extended = %d " % g_num_4b_se
		print "Num of 8-bit sign extended = %d " % g_num_8b_se
	 	print "Num of two half-words sign extended = %d " % g_num_2_hw_se
	 	print "Num of half-word sign extended = %d " % g_num_hw_se
	 	print "Num of half-word zero-padded = %d " % g_num_hw_zp
	 	print "Num of repeated byte = %d " % g_rep_byte
	 	print "Num of uncompressible words = %d " % g_uncompressible

	if enable_unique_analysis:
	 	cnt = counter.Counter(g_words)
	 	common = cnt.most_common(10)
	 	print "Most common words:"
	 	print common
	 	print "No. of unique words = ", len(cnt.most_common())

	 	if (enable_plots):
			plt.figure(figsize=(20,10))
			plt.title('Most common words:')
			plt.ylabel('No. of occurences')
			plt.xlabel('Words')
			X = np.arange(len(common))
			plt.bar(X, [c[1] for c in common],  width = 0.5)
			plt.xticks(X, [c[0] for c in common])
			plt.show()

		#interleaved --> consider each word is [byte3][byte2][byte1][byte0] --> we consider word1([byte3][byte2])word2([byte3][byte2]) to be an interleaved upper word. Similarly, we define interleaved lower word
		cnt = counter.Counter(g_i_u_words)
	 	common = cnt.most_common(10)
	 	print "Most common interleaved upper words:"
	 	print common
	 	print "No. of unique interleaved upper words = ", len(cnt.most_common())
	 	if (enable_plots):
			plt.figure(figsize=(20,10))
			plt.title('Most common interleaved upper words:')
			plt.ylabel('No. of occurences')
			plt.xlabel('Words')
			X = np.arange(len(common))
			plt.bar(X, [c[1] for c in common],  width = 0.5)
			plt.xticks(X, [c[0] for c in common])
			plt.show()

		cnt = counter.Counter(g_i_l_words)
	 	common = cnt.most_common(10)

	 	print "Most common interleaved lower words:"
	 	#print common
	 	print "No. of unique interleaved lower words = ", len(cnt.most_common())
	 	if (enable_plots):
			plt.figure(figsize=(20,10))
			plt.title('Most common interleaved lower words:')
			plt.ylabel('No. of occurences')
			plt.xlabel('Words')
			X = np.arange(len(common))
			plt.bar(X, [c[1] for c in common],  width = 0.5)
			plt.xticks(X, [c[0] for c in common])
			plt.show()


		cnt = counter.Counter(av_l_words)
		common = cnt.most_common()
		print "Most common lower words. len = %d" % (len(common))
		#print common
		print "Total no. of lower words = %d " % (sum([c[1] for c in common]))
		print "top 64+2 lower words contribute = %d" % sum(c[1] for c in cnt.most_common(66))

		cnt = counter.Counter(av_u_words)
		common = cnt.most_common()
		print "Most common upper words. len = %d" % (len(common))
		#print common
		print "Total no. of upper words = %d " % (sum([c[1] for c in common]))
		print "top 10 upper words contribute = %d" % sum(c[1] for c in cnt.most_common(10))

	if enable_av_compression:
		#print l_cum_dist
		if (enable_plots):
			plt.figure(figsize=(20,10))
			plt.title('Cumulative dist of most common 4 lower-words')
			plt.ylabel('no. of words')
			plt.xlabel('Cache line')
			X = np.arange(len(l_cum_dist))
			plt.bar(X, l_cum_dist,  width = 1)
			#lt.xticks(X, [c[0] for c in common])
			plt.show()

		if (av_comp_bits):
			print "av_compression: uncomressed size = %dB " %((len(g_words)/16+1)*64)
			print "av_compression: compressed size = %dB" % (av_comp_bits/8)
			print "av_compression: comp ratio = %f " % (((len(g_words)/16+1)*64)/(av_comp_bits/8))

	if enable_markov_analysis:
		# Markov analysis
		# zeroth order
		markov_analysis()
	
	FILE_OUT.close()
	#end main


def line_analysis(line):
	global g_same_value_lines
	global g_zero_lines
	global g_narrow_value_lines
	global g_aligned_value_lines
	global g_num_narrow_list
	global g_num_aligned_list
	global g_words
	global g_upper_words
	global g_lower_words
	global g_i_u_words
	global g_i_l_words
	global av_l_words 
	global av_u_words 
	global l_cum_dist

	bytes = []

	match = match_re.match(line)
	if match:
		for i in range(1, 65):
			bytes.append(hex(int(match.group(i), 16))[2:])

	upper_words = []
	lower_words = []
	words = []
	i_u_words = [] # interleaved upper words
	i_l_words = [] # interleaved upper words


	for i in xrange(0, 64, 4):
		upper_words.append(bytes[i] + bytes[i+1])
	for i in xrange(2, 64, 4):
		lower_words.append(bytes[i] + bytes[i+1])
	for i in xrange(0, 64, 4):
		words.append(bytes[i] + bytes[i+1] + bytes[i+2] + bytes[i+3])

	for i in xrange(0, 64, 8):
		i_u_words.append(bytes[i] + bytes[i+1] + bytes[i+4] + bytes[i+5])

	for i in xrange(2, 64, 8):
		i_l_words.append(bytes[i] + bytes[i+1] + bytes[i+4] + bytes[i+5])

	g_words += words
	g_upper_words += upper_words
	g_lower_words += lower_words
	g_i_u_words += i_u_words
	g_i_l_words += i_l_words

	# check whether this is a repeated line with non-zero value
	flag = 0
	same_value = words[0]
	for w in words[1:]:
		if int(w, 16) == int(same_value, 16) and int(w, 16) != 0:
			flag = 1
		else:
			flag = 0
			break
	if flag:
		g_same_value_lines+=1

	# check whether this is an all-zero line
	flag = 0
	for w in words:
		if int(w, 16) == 0:
			flag = 1
		else:
			flag = 0
			break
	if flag:
		g_zero_lines+=1

	common = []
	if flag==0 : 
		av_u_words += upper_words
		av_l_words += lower_words
		cnt = counter.Counter(lower_words)
		common = cnt.most_common(4)
		#print "Most common lower words within a line"
		#print common
		sum1 = 0
		for c in common:
			sum1+=c[1]
		l_cum_dist.append(sum1)

	if enable_av_compression:
		av_compression (upper_words, lower_words, flag, common)
		
	# check whether this line has narrow values
	line_narrow_values = 0

	for w in upper_words:
		if int(w, 16) == 0:
			line_narrow_values+=1
	g_narrow_value_lines += line_narrow_values/16
	g_num_narrow_list.append(line_narrow_values)

	# check whether this line has aligned values
	line_aligned_values = 0
	for w in lower_words:
		if int(w, 16) == 0:
			line_aligned_values+=1
	g_aligned_value_lines += line_aligned_values/16
	g_num_aligned_list.append(line_aligned_values)

	# bdi analysis
	# check delta w.r.t base[0] = 0
	# check with 1B, 2B and 4B offsets
	if enable_bdi:
		bdi_comp (words, bytes)

	# fpc analysis
	if enable_fpc:
		fpc_comp (words)


''' for upper word:
		if word == 0000 or ffff, 
			just store 1-bit
		else
			store word as is.
	for lower word:
		if word == 0000 or ffff,
			just store 1-bit
		else if word in most-common dict: 
				store dict index. 
			else
				store word as is. 
'''
def av_compression (upper_words, lower_words, flag, common):
	global av_comp_bits
	linebits = 0

	if flag == 1: #zero line
		return

	for word in upper_words:
		if int(word, 16) == 0 or int(word, 16) == 65535:
			linebits += 2
		else:
			linebits += 2*8
	for word in lower_words:
		if int(word, 16) == 0 or int(word, 16) == 65535:
			linebits += 2
		else:
			f = 0
			for c in common:
				if word == c[0]:
					f = 1
					linebits += 2
					break
			if f == 0:
				linebits += 2*8
	linebits += max((len(common) - 2), 0) * 2 * 8	
	av_comp_bits += linebits
	
	
def bdi_comp (words, bytes):
	global g_num_bdi_lines
	global g_bdi_lines_list

	min_comp_size = 64
	nz = 0
	for w in words:
		if int(w, 16) != 0:
			nz = 1
			break
	if nz == 0:
		min_comp_size = 1

	nsv = 0
	for w in words[1:]:
		if int(w, 16) != words[0]:
			nsv = 1
			break
	if nsv == 0:
		min_comp_size = 8

	# check the base, delta comp for base = 8B, 4B, 2B
	values = convert(bytes, 8)
	min_comp_size = min(min_comp_size, base_comp(values, 8, 4))
	min_comp_size = min(min_comp_size, base_comp(values, 8, 2))
	min_comp_size = min(min_comp_size, base_comp(values, 8, 1))

	values = convert(bytes, 4)
	min_comp_size = min(min_comp_size, base_comp(values, 4, 2))
	min_comp_size = min(min_comp_size, base_comp(values, 4, 1))

	values = convert(bytes, 2)
	min_comp_size = min(min_comp_size, base_comp(values, 2, 1))

	if min_comp_size < 64:
		g_num_bdi_lines += 1
		g_bdi_lines_list.append(min_comp_size)

	# calculate the num of segments this line will take.
	num_segments(min_comp_size)

def convert (bytes, base):
	values = []
	for i in xrange(0, len(bytes), base):
		val = bytes[i]
		for j in range(i+1, i+base):
			val += bytes[j]
		values.append(val)
	return values

def base_comp (values, base, limit) :
    max_offset = 0
    if limit == 1:
        max_offset = 255
    elif limit == 2:
        max_offset = 65535
    else:
        max_offset = 4294836225

    base_index = 0
    max_bases = 1
    # find the additional base
    for v in values:
        if (int(v, 16) - bases[base_index] > max_offset):
            base_index += 1
            bases.append(int(v, 16))
            if base_index >= max_bases:
                break
    comp_count = 0
    for v in values:
        for b in bases:
            if abs(int(v, 16) - b) <= max_offset:
                comp_count += 1
                break
    comp_size = limit*comp_count + base*max_bases + (len(values) - comp_count)*base #bytes
    return comp_size


def fpc_comp (words) :
	global g_num_zeros
	global g_num_4b_se
	global g_num_8b_se
	global g_num_2_hw_se
	global g_num_hw_se
	global g_num_hw_zp
	global g_rep_byte
	global g_uncompressible

	linebits = 0
	for word in words:
		wv = int(word, 16)
		if wv == 0:
			linebits += 3
			g_num_zeros +=1
		else: #not zero
			if ((wv & 0x0000000F) == wv) or ((wv | 0xFFFFFFF8) == wv):
				g_num_4b_se +=1
				linebits += 7
			else:
				if ((wv & 0x0000007F) == wv) or ((wv | 0xFFFFFF80) == wv):
					linebits += 11
					g_num_8b_se +=1
				else:
					if (   ( (((wv & 0x000000FF) == (wv & 0x0000FFFF)) and ((wv & 0x00000080) == 0) ) and
							 (((wv & 0x00FF0000) == (wv & 0xFFFF0000)) and ((wv & 0x00800000) == 0) ) ) or
							( ( ((wv | 0x0FFFFFF00) == (wv | 0xFFFF0000)) and (wv & 0x00000080) != 0)
                 			 and (((wv | 0xFF00FFFF) == (wv & 0x0000FFFF)) and (wv & 0x00800000) != 0))):
						linebits += 19
						g_num_2_hw_se += 1
					else:
						if ((wv & 0x00007FFF == wv) or (wv | 0xFFFF8000 == wv)):
							linebits += 19
							g_num_hw_se += 1
						else:
							if ((wv & 0xFFFF0000 == wv) and wv != 0):
								linebits += 19
								g_num_hw_zp += 1
							else:
								b0 = word[0:2]
								b1 = word[2:4]
								b2 = word[4:6]
								b3 = word[6:8]
								if (wv != 0 and b0 == b1 and b0 == b2 and b0 == b3):
									linebits += 11
									g_rep_byte += 1
								else:
									linebits += 35
									g_uncompressible += 1


def num_segments ( compressed_size ):
	#assuming compressed_size is in bytes
	for segment in g_segments:
		if (compressed_size <= segment):
			dict_segments[segment] += 1
			break


def init_segment_dict():
	for segment in g_segments:
		dict_segments[segment] = 0

def markov_analysis():
	global g_words
	global g_upper_words
	global g_lower_words
	global av_u_words
	global av_l_words
	global g_i_u_words
	global g_i_l_words

	print "Zero entropy of all words:"
	zero_entropy (g_words, 32)
	print "Markov Zeroth entropy of all words:"	
	Markov_zeroth (g_words, 32)

	# Markov analysis of upper & lower words
	print "Zero entropy of all upper half-words:"
	zero_entropy (g_upper_words, 16)
	print "Markov Zeroth entropy for all upper half-words:"
	Markov_zeroth (g_upper_words, 16)

	print "Zero entropy of all lower half-words:"
	zero_entropy (g_lower_words, 16)
	print "Markov Zeroth entropy for all lower half-words:"
	Markov_zeroth (g_lower_words, 16)


	# Markov analysis of upper & lower words
	#print "Zero entropy of all interleaved upper half-words:"
	#zero_entropy (g_i_u_words, 16)
	#print "Markov Zeroth entropy for all interleaved upper half-words:"
	#Markov_zeroth (g_i_u_words, 16)

	#print "Zero entropy of all interleaved lower half-words:"
	#zero_entropy (g_i_l_words, 16)
	#print "Markov Zeroth entropy for all interleaved lower half-words:"
	#Markov_zeroth (g_i_l_words, 16)

def zero_entropy (symbols, word_size):
	z_common = counter.Counter(symbols)
	print "No. of unique symbols in cache = %d" % (len(z_common))
	#print z_common
	zero_info_entropy = math.log(len(z_common), 2)
	print "Zero-information entropy of the cache = %d " % (zero_info_entropy)
	print "Comp ratio for zero-information entropy = %f " % (zero_info_entropy/word_size) #entropy divided by word size

def Markov_zeroth (symbols, word_size):
	# Zeroth-order Markov entropy
	z_common = counter.Counter(symbols)
	total_set = len(symbols)
	prob_common = {}
	for c in z_common.items():
		prob_common[c[0]] = float(c[1])/float(total_set)

	Mz_entropy = 0
	for p in prob_common.values():
		Mz_entropy += (-1) * p * math.log(p,2)

	print "Markov zeroth order entropy = %f" %  Mz_entropy
	print "Comp ratio for Markov zeroth order entropy = %f" % (float(Mz_entropy)/word_size)
	print 


def usage():
	print "Incorrect usage"
	print "cache_analyzer.py -i <input-file> -o <output-file> \nalternately, --input --output";
	exit()

#-------------------------------
if __name__ == "__main__":
    main()
