
#include <Python.h>
#include <iostream>
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

  arg1 = 8; /* Default values. */
  if (! PyArg_ParseTuple(args, "iiiii", &arg1, &arg2, &arg3, &arg4, &arg5)) {
    return NULL;
  }
  short * result;
  result = render(arg1, arg2, arg3, arg4, arg5);

  PyObject* ret = PyList_New(arg4); // arg4 is samples
  for (int i = 0; i < arg4; ++i) {
    PyObject* python_int = Py_BuildValue("i", result[i]);
    PyList_SetItem(ret, i, python_int);
  }
  free(result);
  return ret;
}

static PyMethodDef DX7Methods[] = {
 {"render", render_wrapper, METH_VARARGS, "Render audio"},
 { NULL, NULL, 0, NULL }
};


extern "C" {
DL_EXPORT(void) initdx7(void)
{
  Py_InitModule("dx7", DX7Methods);

  FILE *f = fopen("/Users/bwhitman/outside/learnfm/compact.bin","rb");
  fseek(f, 0, SEEK_END);
  long fsize = ftell(f);
  char * all_patches = (char*)malloc(fsize);
  fseek(f,0,SEEK_SET);
  fread(all_patches, 1, fsize, f);
  fclose(f);
  int patches = fsize / 128;
  printf("%d patches\n", patches);
  unpacked_patches = (char*) malloc(patches*156);
  for(int i=0;i<patches;i++) {
    UnpackPatch(all_patches + (i*128), unpacked_patches + (i*156));
  }
  init_synth();
  free(all_patches);
}
}

