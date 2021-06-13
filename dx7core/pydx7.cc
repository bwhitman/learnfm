
#include <Python.h>
//#include <iostream>
#include <cstdlib>
#include <math.h>
#include "synth.h"
#include "module.h"
#include "aligned_buf.h"
#include "freqlut.h"
#include "wavout.h"
#include "sawtooth.h"
#include "sin.h"
#include "exp2.h"
#include "log2.h"
#include "resofilter.h"
#include "fm_core.h"
#include "fm_op_kernel.h"
#include "env.h"
#include "patch.h"
#include "controllers.h"
#include "dx7note.h"

char * unpacked_patches;

void write_data(const int32_t *buf_in, short * buf_out, unsigned int * pos, int n) {
  int32_t delta = 0x100;
  for (int i = 0; i < n; i++) {
    int32_t val = buf_in[i];
    int clip_val = val < -(1 << 24) ? 0x8000 : (val >= (1 << 24) ? 0x7fff :
                                                (val + delta) >> 9);
    delta = (delta + val) & 0x1ff;
    buf_out[*pos + i] = clip_val; 
  }
  *pos = *pos + n;
}

// take in a patch #, a note # and a velocity and a sample length and a sample # to lift off a key?
short * render(unsigned short patch, unsigned char midinote, unsigned char velocity, unsigned int samples, unsigned int keyup) {
  Dx7Note note;
  short * out = (short *) malloc(sizeof(short) * samples);
  unsigned int out_ptr = 0;
  note.init(unpacked_patches + (patch * 156), midinote, velocity);
  Controllers controllers;
  controllers.values_[kControllerPitch] = 0x2000;
  int32_t buf[N];

  for (int i = 0; i < samples; i += N) {
    for (int j = 0; j < N; j++) {
      buf[j] = 0;
    }
    if (i >= keyup) {
      note.keyup();
    }
    note.compute(buf, 0, 0, &controllers);
    for (int j = 0; j < N; j++) {
      buf[j] >>= 2;
    }
    write_data(buf, out, &out_ptr, N);
  }
  return out;
}

void init_synth(void) {
  double sample_rate = 44100.0;
  Freqlut::init(sample_rate);
  Sawtooth::init(sample_rate);
  Sin::init();
  Exp2::init();
  Log2::init();
}

static PyObject * render_wrapper(PyObject *self, PyObject *args) {
  int arg1, arg2, arg3, arg4, arg5;

  /* Default values. */
  arg1 = 8; // patch #
  arg2 = 50; // midi note
  arg3 = 70; // velocity
  arg4 = 44100; // samples
  arg5 = 22050; // keyup sample
  if (! PyArg_ParseTuple(args, "iiiii", &arg1, &arg2, &arg3, &arg4, &arg5)) {
    return NULL;
  }
  short * result;
  result = render(arg1, arg2, arg3, arg4, arg5);

  // Create a python list of ints (they are signed shorts that come back)
  PyObject* ret = PyList_New(arg4); // arg4 is samples
  for (int i = 0; i < arg4; ++i) {
    PyObject* python_int = Py_BuildValue("i", result[i]);
    PyList_SetItem(ret, i, python_int);
  }
  free(result);
  return ret;
}
// return one patch unpacked for sysex
static PyObject * unpack_wrapper(PyObject *self, PyObject *args) {
  int arg1 = 8; // patch #
  if (! PyArg_ParseTuple(args, "i", &arg1)) {
    return NULL;
  }
  PyObject* ret = PyList_New(155); 
  for (int i = 0; i < 155; i++) {
    PyObject* python_int = Py_BuildValue("i", unpacked_patches[arg1*156 + i]);
    PyList_SetItem(ret, i, python_int);    
  }
  return ret;
}

static PyMethodDef DX7Methods[] = {
 {"render", render_wrapper, METH_VARARGS, "Render audio"},
 {"unpack", unpack_wrapper, METH_VARARGS, "Unpack patch"},
 { NULL, NULL, 0, NULL }
};

static struct PyModuleDef dx7Def =
{
    PyModuleDef_HEAD_INIT,
    "dx7", /* name of module */
    "",          /* module documentation, may be NULL */
    -1,          /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    DX7Methods
};

extern "C" {
PyMODINIT_FUNC PyInit_dx7(void)
{
  // TODO: this file should go into the package directory from setup.py, but that is a PITA 
  FILE *f = fopen("/Users/bwhitman/outside/learnfm/compact.bin","rb");
  // See how many voices are in the file
  fseek(f, 0, SEEK_END);
  long fsize = ftell(f);
  char * all_patches = (char*)malloc(fsize);
  fseek(f,0,SEEK_SET);
  // Load them all in
  fread(all_patches, 1, fsize, f);
  fclose(f);
  int patches = fsize / 128;
  printf("%d patches\n", patches);
  // Patches have to be unpacked to go from 128 bytes to 156 bytes via DX7 spec
  unpacked_patches = (char*) malloc(patches*156);
  for(int i=0;i<patches;i++) {
    UnpackPatch(all_patches + (i*128), unpacked_patches + (i*156));
  }
  // Have to call this out as we're in C extern 
  init_synth();
  free(all_patches);
  return PyModule_Create(&dx7Def);
}
}

