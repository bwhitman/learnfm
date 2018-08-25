# dx7db.py

import os, sys, re, json, pickle, hashlib


def get_all_syx_files():
	sysexs = []
	for path, directories, files in os.walk('patches'):
		for file in files:
			d = os.path.join(path, file)
			if d.endswith("syx") or d.endswith("SYX"):
				sysexs.append(d)
	return sysexs


def parse_128b(buf):
	name = bytearray(buf[118:128])
	digest = hashlib.md5(buf[:118]).hexdigest()
	return (buf, name, digest)

def parse_4104b(buf):
	voices = []
	for i in range(32):
		start_byte = 6 + (i*128)
		end_byte = start_byte + 128
		voices.append(parse_128b(buf[start_byte:end_byte]))
	return voices

def parse_4096b(buf):
	buf = "000000" + buf + "00"
	return parse_4104b(buf)

def parse_8208b(buf):
	return parse_4104b(buf) + parse_4104b(buf[4104:])

def parse_all():
 	all_files = get_all_syx_files()
	all_patches =[]
	total = 0
	cant = 0
	dedup = {}
	for i,f in enumerate(all_files):
		data = open(f, 'rb').read()
		if(len(data) == 4104):
			p = parse_4104b(data)
		elif(len(data) == 4096):
			p = parse_4096b(data)
		elif(len(data) == 8208):
			p = parse_8208b(data)
		else:
			cant = cant + 1
		for patch in p:
			total = total + 1
			dedup[patch[2]] = patch
	return dedup

def main():
	compact = open("compact.bin", "wb")
	names = open("names.txt", "w")
	dedup = parse_all()
	for r in dedup.items():
		compact.write(r[1][0])
		name = r[1][1]
		for i,char in enumerate(name):
			if(char < 32): name[i] = ' '
			if(char > 126): name[i] = ' '
		names.write(name)
		names.write('\n')
	compact.close()
	names.close()
	print "Wrote %d patches to compact.bin & names.txt" % (len(dedup.items()))


if __name__ == "__main__":
	main()




