#!/usr/bin/env python
import getopt, sys, time, re
import matplotlib.pyplot as plt
plt.switch_backend('GTKAgg')
import numpy as np
#import collections

g_same_value = 0
g_zero_line = 0
g_narrow_value = 0
g_aligned_value = 0
g_bytes = []
g_upper_bytes = []
g_lower_bytes = []
g_upper_words = []
g_lower_words = []
g_words = []
g_u_words = []
g_l_words = []
g_delta_zero_lower_words = []
g_delta_ffff_lower_words = []
g_delta_multi_lower_words = []

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

	FILE_IN = open(input_file, "r+")
	FILE_OUT = open(output_file, "wb")

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


	#analysis of upper and lower half-words. 
	temp_g_lower_bytes = [int(l, 16) for l in g_lower_bytes]
	plt.grid(True)
	bins=[0, 4, 8, 16, 32, 64, 128, 256]
	#plt.xticks(np.arange(len(bins)) + 0.8/2)
	plt.hist(temp_g_lower_bytes, bins)
	print np.histogram(temp_g_lower_bytes, bins)
	#plt.show()

	temp_g_upper_bytes = [int(l, 16) for l in g_upper_bytes]
	plt.grid(True)
	bins=[0, 4, 8, 16, 32, 64, 128, 256]
	#plt.xticks(np.arange(len(bins)) + 0.8/2)
	plt.hist(temp_g_upper_bytes, bins)
	print np.histogram(temp_g_upper_bytes, bins)
	#plt.show()

	temp_g_l_words = [int(l, 16) for l in g_l_words]
	plt.grid(True)
	bins=[0, 128, 4096, 65536, 65536*65536]
	#plt.xticks(np.arange(len(bins)) + 0.8/2)
	plt.hist(temp_g_l_words, bins)
	print np.histogram(temp_g_l_words, bins)
	#plt.show()

	temp_g_u_words = [int(l, 16) for l in g_u_words]
	plt.grid(True)
	bins=[0, 128, 4096, 65536, 65536*65536]
	#plt.xticks(np.arange(len(bins)) + 0.8/2)
	plt.hist(temp_g_u_words, bins)
	print np.histogram(temp_g_u_words, bins)
	#plt.show()


	#analyse words for zeros, narrow values, repeated values. 
	print "num of zero lines = %d. " % (g_zero_line)
	print "num of same value lines = %d " % g_same_value
	print "num of narrow value lines = %d " % g_narrow_value
	print "num of aligned value lines = %d " % g_aligned_value
	#counter=collections.Counter(g_bytes)

	#labels, values = zip(*collections.Counter(g_bytes).items())
	#indexes = np.arange(len(labels))
	#width = 5

	#plt.bar(indexes, values, width)
	#plt.xticks(indexes + width, labels)
	#plt.savefig('foo.png')

	# calculate freq of deltas of lower words wrt 0 and ffff
	#counter_delta_zero = collections.Counter(g_delta_zero_lower_words)
	#counter_delta_ffff = collections.Counter(g_delta_ffff_lower_words)
	#counter_delta_multi = collections.Counter(g_delta_multi_lower_words)

	#print "delta zero"
	#print counter_delta_zero
	#print "delta ffff"
	#print counter_delta_ffff
	#print "delta multi"
	#print counter_delta_multi

	FILE_OUT.close()

	common_words = []
	for l in g_l_words:
		if l in g_u_words:
			common_words.append(l)

	#print "no. u words = %d . no. of l words = %d. no. of common elements = %d " % (len(g_u_words), len(g_l_words), len(common_words))



def line_analysis(line):
	global g_same_value
	global g_zero_line
	global g_narrow_value
	global g_aligned_value
	global g_bytes
	global g_upper_bytes
	global g_lower_bytes
	global g_upper_words
	global g_lower_words
	global g_words
	global g_u_words
	global g_l_words
	global g_delta_zero_lower_words
	global g_delta_ffff_lower_words
	global g_delta_multi_lower_words

	bytes = []

	match = match_re.match(line)
	if match:
		for i in range(1, 65):
			bytes.append(hex(int(match.group(i), 16))[2:])

	upper_bytes = bytes[0::4]
	upper_bytes += bytes[1::4]
	lower_bytes = bytes[2::4]
	lower_bytes += bytes[3::4]

	#print lower_bytes
	g_upper_bytes += upper_bytes
	g_lower_bytes += lower_bytes

	upper_words = []
	lower_words = []
	words = []
	u_words = []
	l_words = []

	

	for i in xrange(0, 64, 4):
		upper_words.append(bytes[i] + bytes[i+1])
	for i in xrange(2, 64, 4):
		lower_words.append(bytes[i] + bytes[i+1])
	for i in xrange(0, 64, 4):
		words.append(bytes[i] + bytes[i+1] + bytes[i+2] + bytes[i+3])

	for i in xrange(0, 64, 8):
		u_words.append(bytes[i] + bytes[i+1] + bytes[i+4] + bytes[i+5])

	for i in xrange(2, 64, 8):
		l_words.append(bytes[i] + bytes[i+1] + bytes[i+4] + bytes[i+5])

	flag = 0
	for b in words[1:]:
		if int(b, 16) == int(words[0], 16):
			flag = 1
		else:
			flag = 0
			break
	if flag:
		g_same_value+=1

	flag = 0
	for b in words:
		if int(b, 16) == 0:
			flag = 1
		else:
			flag = 0
			break
	if flag:
		g_zero_line+=1

	for b in upper_words:
		if int(b, 16) == 0:
			g_narrow_value+=1

	for b in lower_words:
		if int(b, 16) == 0:
			g_aligned_value+=1

	#print bytes
	g_upper_words += upper_words
	g_lower_words += lower_words
	g_words += words
	g_u_words += u_words
	g_l_words += l_words

	delta_zero = 0
	delta_ffff = 0
	delta_multi = 0
	for word in lower_words:
		delta_zero += abs(int(word, 16));
		delta_ffff += abs((int(word, 16) - int('0xffff', 16)));
		delta_multi += min(delta_zero, delta_ffff)
	delta_zero = delta_zero/len(lower_words)
	delta_ffff = delta_ffff/len(lower_words)
	delta_multi = delta_multi/len(lower_words)
	#print "delta_zero for lower_words", delta_zero
	#print "delta_ffff for lower_words", delta_ffff
	g_delta_zero_lower_words.append(delta_zero)
	g_delta_ffff_lower_words.append(delta_ffff)
	g_delta_multi_lower_words.append(delta_multi)

	

	
	g_bytes = g_bytes + bytes
	#print bytes
	#print len(bytes)
	#counter = collections.Counter(delta_bytes)
	#print counter
	#counter=collections.Counter(bytes)
	#print counter
	#return counter

def usage():
	print "Incorrect usage"
	print "cache_content_analysis.py -i <input-file> -o <output-file> \nalternately, --input --output";
	exit()

#-------------------------------
if __name__ == "__main__":
    main()
