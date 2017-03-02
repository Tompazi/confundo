#! /usr/bin/python
import sys, getopt
import collections, itertools

files = ['confusables.txt', 'intentional.txt']
encoding = None
reverse = False
extreme = False
visual = False
limit = -1
try:
	with open('usage.txt','r') as f:
		usage_text = f.read()
except:
	usage_text = "usage.txt is missing"	
def usage(): print(usage_text)

#Parse arguments
if len(sys.argv) < 2:
	usage()
	sys.exit(2)

real = unicode(sys.argv[-1],'utf-8')
depth = [1,len(real)]

try:
	opts, args = getopt.getopt(sys.argv[1:],"hxpirXvd:n:",["help","xml","python","identical","reverse","depth=","limit=","extreme","visual"])
except getopt.GetoptError:
	usage()
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h' or opt == "--help":
		usage()
		sys.exit()
	elif opt in ("-x", "--xml"):
		encoding = 'xmlcharrefreplace'
	elif opt in ("-p", "--python"):
		encoding = 'backslashreplace'
	elif opt in ("-i", "--identical"):
		files = ['intentional.txt']
	elif opt in ("-n", "--limit"):
		try:
			limit = int(arg)
		except:
				print("Please supply an integer as limit")
				sys.exit(2)
		skip = 2
	elif opt in ("-r", "--reverse"):
		reverse = True
	elif opt in ("-X", "--extreme"):
		extreme = True
	elif opt in ("-v", "--visual"):
		visual = True
	elif opt in ("-d", "--depth"):
		d = arg.split(':')
		if len(d) != 2:
			print("Please supply correct format for depth range. e.g. 1:2")
			sys.exit(2)			
		else:
			try:
				if d[0] != '': 
					depth[0] = int(d[0])
				else:
					depth[0] = 1
				if d[1] != '': 
					depth[1] = int(d[1])
				else:
					depth[1] = len(real)
			except:
				print("Please supply integers for depth range. e.g. 1:2")
				sys.exit(2)
		for x in depth:
			if x < 1:
				print("Depth cannot be below 1.")
				sys.exit(2)

# Read and parse data files
raw = ""
try:
	for i in files:
		with open(i, 'r') as f:
			raw += f.read()
except:
	print("File(s) missing, please run ./update.sh")
	sys.exit(2)

confuse = [(x.split(';')[0].strip(), x.split(';')[1].strip()) for x in raw.split('\n') if not x.strip().startswith('#') and len(x.split(';'))>1]

for i,p in enumerate(confuse):
	x,y = p
	if '#' in y: y=y[:y.index('#')].strip()
	y = u''.join([unichr(int(z,16)) for z in y.split()])
	confuse[i] = (unichr(int(x,16)),y)

confundo = collections.defaultdict(list)
for k,v in confuse:
	confundo[k].append(v)
	if reverse or extreme:
		if len(v) == 1:
			confundo[v].append(k)
			
# Select similar characters
confusion = {}
for c in real:
	if c in confundo:
		confusion[c]= confundo[c]
		if extreme:
			for x in confusion[c]:
				y = confundo[x]
				for z in y:
					if z not in confusion[c] and z != c:
						confusion[c].append(z)
		confusion[c] = list(set(confusion[c]))

if len(confusion) == 0:
	print("Could not find any confusing characters. You could try it with the -r or -X option.")
	sys.exit(1)
	
indexes = []
length = 0
for i,x in enumerate(real):
	if x in confusion:
		conf = confusion[x]
		for c in conf:	
			indexes.append((i,c))
		length +=1
		
# Adjust depth		
if depth[0] > length:
	depth[0] = length
if depth[1] > length or depth[1] == 0:
	depth[1] = length
depth.sort()

# Print combinations
printed = 0

try:
	for l in range(depth[0],depth[1]+1):
		for combo in itertools.combinations(indexes, l):
			if collections.Counter([x[0] for x in combo]).most_common(1)[0][1] > 1:
				continue		
			confused = list(real)
			for c in combo:
				confused[c[0]] = c[1]
			confused = "".join(confused)
			if encoding:
				if visual:
					print(confused.encode('utf-8')+'\t'+confused.encode('ascii',encoding))
				else:
					print(confused.encode('ascii',encoding))
			else:
				print(confused.encode('utf-8'))
			printed += 1
			if printed >= limit and limit != -1:
				break
		if printed >= limit and limit != -1:
			break
except KeyboardInterrupt:
	print("Quitting")
finally:
	print("Printed "+str(printed)+" similar strings.")
	
