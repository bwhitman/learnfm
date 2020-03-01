# Takes a directory full of DX7 sysex patches and outputs a compacted unique list of voices
import os, sys, hashlib

import mido

# I got this by paying $2 for https://gumroad.com/dxsysex
def get_all_syx_files():
    sysexs = []
    for path, directories, files in os.walk('patches'):
        for file in files:
            d = os.path.join(path, file)
            if d.endswith("syx") or d.endswith("SYX"):
                sysexs.append(d)
    return sysexs

# Pull the name and voice out of a 128 byte buffer, and compute a hash of just the parameters
def parse_128b(buf):
    name = buf[118:128]
    digest = hashlib.md5(buf[:118]).hexdigest()
    return (buf, name, digest)

# Pull 32 voices out of a sysex patch bank, the most common form 
def parse_4104b(buf):
    voices = []
    for i in range(32):
        start_byte = 6 + (i*128)
        end_byte = start_byte + 128
        voices.append(parse_128b(buf[start_byte:end_byte]))
    return voices

# Pull 32 patches out of a headerless bank
def parse_4096b(buf):
    buf = "000000" + buf + "00"
    return parse_4104b(buf)

# Two sysex messages
def parse_8208b(buf):
    return parse_4104b(buf) + parse_4104b(buf[4104:])

# There's many other types in the dataset but the counts per type are too low to worry about



def sysex_message(patch_number, channel):
    import dx7
    # get the 155 bytes for the patch number from the C extension
    patch_data = dx7.unpack(patch_number)
    # generate the twos complement checksum for the patch data 
    # from these dudes fighting w/ each other about who has the best programming skills sigh 
    # https://yamahamusicians.com/forum/viewtopic.php?t=6864
    check = ~sum(patch_data) + 1 & 0x7F

    # Generate the sysex message
    byte_count = 155 # always 155 bytes of patch information (the operator-on message is only for live mode)
    msb = byte_count / 127
    lsb = (byte_count % 127) - 1
    return [0x43, channel, 0, msb, lsb] + patch_data + [check]

_port = mido.open_output()
def update_voice(patch_number, channel):
    sysex = sysex_message(patch_number, channel)
    msg = mido.Message('sysex', data=sysex)
    #_port.send(program)
    _port.send(msg)

def play_note(note, channel):
    msg = mido.Message('note_on', note=note, channel=channel)
    _port.send(msg)
def stop_note(note,channel):
    msg = mido.Message('note_off',note=note, channel = channel, velocity=0)
    _port.send(msg)

def parse_all():
    all_files = get_all_syx_files()
    all_patches =[]
    total = 0
    cant = 0
    dedup = {}
    for i,f in enumerate(all_files):
        data = bytearray(open(f, 'rb').read())
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

def unpack_packed_patch(p):
    # Input is a 128 byte thing from compact.bin
    # Output is a 156 byte thing that the synth knows about
    o = [0]*156
    for op in xrange(6):
        o[op*21:op*21 + 11] = p[op*17:op*17+11]
        leftrightcurves = p[op*17+11]
        o[op * 21 + 11] = leftrightcurves & 3
        o[op * 21 + 12] = (leftrightcurves >> 2) & 3
        detune_rs = p[op * 17 + 12]
        o[op * 21 + 13] = detune_rs & 7
        o[op * 21 + 20] = detune_rs >> 3
        kvs_ams = p[op * 17 + 13]
        o[op * 21 + 14] = kvs_ams & 3
        o[op * 21 + 15] = kvs_ams >> 2
        o[op * 21 + 16] = p[op * 17 + 14]
        fcoarse_mode = p[op * 17 + 15]
        o[op * 21 + 17] = fcoarse_mode & 1
        o[op * 21 + 18] = fcoarse_mode >> 1
        o[op * 21 + 19] = p[op * 17 + 16]
    
    o[126:126+9] = p[102:102+9]
    oks_fb = p[111]
    o[135] = oks_fb & 7
    o[136] = oks_fb >> 3
    o[137:137+4] = p[112:112+4]
    lpms_lfw_lks = p[116]
    o[141] = lpms_lfw_lks & 1
    o[142] = (lpms_lfw_lks >> 1) & 7
    o[143] = lpms_lfw_lks >> 4
    o[144:144+11] = p[117:117+11]
    o[155] = 0x3f

    # Clamp the unpacked patches to a known max. 
    maxes =  [
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, # osc6
        3, 3, 7, 3, 7, 99, 1, 31, 99, 14,
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, # osc5
        3, 3, 7, 3, 7, 99, 1, 31, 99, 14,
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, # osc4
        3, 3, 7, 3, 7, 99, 1, 31, 99, 14,
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, # osc3
        3, 3, 7, 3, 7, 99, 1, 31, 99, 14,
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, # osc2
        3, 3, 7, 3, 7, 99, 1, 31, 99, 14,
        99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, # osc1
        3, 3, 7, 3, 7, 99, 1, 31, 99, 14,
        99, 99, 99, 99, 99, 99, 99, 99, # pitch eg rate & level 
        31, 7, 1, 99, 99, 99, 99, 1, 5, 7, 48, # algorithm etc
        126, 126, 126, 126, 126, 126, 126, 126, 126, 126, # name
        127 # operator on/off
    ]
    for i in xrange(156):
        if(o[i] > maxes[i]): o[i] = maxes[i]
        if(o[i] < 0): o[i] = 0
    return o

def convert_compact_to_unpacked():
    # Take a compact.bin and make it unpacked.bin
    f = bytearray(open("compact.bin").read())
    o = open("unpacked.bin", "w")
    num_patches = len(f)/128
    for patch in xrange(num_patches):
        patch_data = f[patch*128:patch*128+128]
        unpacked = unpack_packed_patch(patch_data)
        o.write(bytearray(unpacked))
    o.close()

# Writes all the voices to a binary file of 128 x patches, and also the names in ASCII to a txt file.
def main():
    compact = open("compact.bin", "wb")
    names = open("names.txt", "w")
    dedup = parse_all()
    for r in dedup.items():
        compact.write(r[1][0])
        name = r[1][1] # the name will be the first name of this voice we saw
        for i,char in enumerate(name):
            # Make sure the name is actually ASCII printable
            if(char < 32): name[i] = ' '
            if(char > 126): name[i] = ' '
        names.write(name)
        names.write('\n')
    compact.close()
    names.close()
    print "Wrote %d patches to compact.bin & names.txt" % (len(dedup.items()))

if __name__ == "__main__":
    main()


