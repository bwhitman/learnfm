# learnfm


Download the DX7 sysex patches from http://dxsysex.com/ and put them in a folder called `patches/`
```
python dx7db.py
```

Will create a database called `combined.bin` and `names.txt` with all of the unique voices from all the banks in the patches (I count 31,380.) 
The unique-finding-algorithm looks at the data in the voice, not the name. Many voices have different names but the same voice information.


```
cd dx7core
make
./dx7 # a test, will create /tmp/foo.wav with all the patches in order if you want

python setup.py install # will create a python module called dx7
```

```
>>> import dx7
>>> patch_number = 324 
>>> midi_note = 60
>>> velocity = 99
>>> samples = 44100 * 10 
>>> keyup_sample = 44100 * 5 # when to let the key up
>>> data = dx7.render(patch_number, midi_note, velocity, samples, keyup_sample)
```
