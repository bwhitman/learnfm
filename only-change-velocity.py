#!/usr/bin/env python2
"""
Generate all patches, playing note A440, changing the velocity but
normalizing the audio, writing ogg files to output/
"""

import os
import os.path
import glob
import string
import sys

import numpy as np
import soundfile as sf
from slugify import slugify
from tqdm.auto import tqdm
import multiprocessing

import dx7
import random

random.seed(0)

SR = 44100
NOTE = 69       # A440

DURATION = 4
NOTE_ON = 3
VELOCITY_RANGE = [1, 127]

def render(patch_and_velocity):
    patch, patchname, velocity = patch_and_velocity

    slug = "output/%06d-%s-note%d-velocity%03d.wav" % (patch, slugify(patchname, lowercase=False), NOTE, velocity)
    #slug = slugify(slug, lowercase=False) + f"-{NOTE}.wav"
    if os.path.exists(slug.replace(".wav", ".ogg")):
        return
    print(slug)
    #s.loadPatch(patch)

    #data = dx7.render(300, 60, 99, 44100 * 10 , 44100 * 5)
    data = dx7.render(patch, NOTE, velocity, int(SR * DURATION), int(SR * NOTE_ON))
    data = np.array(data) / 32768.0

    # Normalize
    data /= np.max(np.abs(data))

    print(data.shape)

    #sf.write(slug, data, SR)
    ## os.system(f"oggenc --quality 10 {slug}")
    #os.system("oggenc -Q %s && rm %s" % (repr(slug), repr(slug)))

npatches = len(open("names.txt").readlines())
ncores = multiprocessing.cpu_count()
print "%d cores" % ncores
patch_and_velocities = []
patches = open("names.txt").readlines()
random.shuffle(patches)
for i, patch in enumerate(open("names.txt").readlines()):
    for velocity in range(VELOCITY_RANGE[0], VELOCITY_RANGE[1] + 1):
        patch_and_velocities.append((i, string.strip(patch), velocity))
#for pn in patch_and_velocities:
#    render(pn)
p = multiprocessing.Pool(ncores)
#r = p.map(render, patch_and_velocities)
r = list(tqdm(p.imap(render, patch_and_velocities), total=len(patch_and_velocities)))
