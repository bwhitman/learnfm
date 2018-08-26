# learnfm


Download the DX7 sysex patches from http://dxsysex.com/ and put them in a folder called `patches/`
```
python dx7db.py
```

Will create a database called `compact.bin` and `names.txt` with all of the unique voices from all the banks in the patches (I count 31,380.) 
The unique-finding-algorithm looks at the data in the voice, not the name. Many voices have different names but the same voice information.


Then, to generate sounds, do
```
cd dx7core
make
./dx7 # a test, will create /tmp/foo.wav with all the patches in order if you want

python setup.py install # will create a python module called dx7
```

The python module renders a mono 44,100Hz 16-bit signed int sound from a patch number (0-31379), a midi note, a velocity and a sample length along with the key up sample position.

```
>>> import dx7
>>> patch_number = 324 
>>> midi_note = 60
>>> velocity = 99
>>> samples = 44100 * 10 
>>> keyup_sample = 44100 * 5 # when to let the key up
>>> data = dx7.render(patch_number, midi_note, velocity, samples, keyup_sample)
```
