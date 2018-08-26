from distutils.core import setup, Extension
import glob

# the c++ extension module
sources = glob.glob("*.cc")
sources.remove("main.cc")

extension_mod = Extension("dx7", sources=sources) #["pydx7.cc"])

setup(name = "dx7", ext_modules=[extension_mod])
