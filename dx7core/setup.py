from distutils.core import setup, Extension
import glob
import os
# the c++ extension module
sources = glob.glob("*.cc")
sources.remove("main.cc")
sources.remove("test_ringbuffer.cc")
sources.remove("test_filter.cc")
sources.remove("test_neon.cc")
os.environ["CC"] = "gcc"
os.environ["CXX"] = "g++"

# This seems ridiculous, and i'm sorry it's here. But Xcode 10 removed something that worked fine before
# When I run this on a high sierra laptop, it errors the first time on the linker, and I just have to copy
# and paste the command again and it works the second time. annoying, and i will look into it later.
extension_mod = Extension("dx7", sources=sources,extra_compile_args = ["-stdlib=libc++","-mmacosx-version-min=10.7"]) #["pydx7.cc"])

setup(name = "dx7", ext_modules=[extension_mod])
