import sys

filename = sys.argv[1]
in_file = open(filename)
for line in in_file:
	print line,
	if line == '.\n':
		print 'Training: 1\n',
	
