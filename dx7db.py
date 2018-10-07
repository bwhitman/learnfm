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


