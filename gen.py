#! /usr/bin/env python

import os
import cPickle
import zlib
import base64

def main():
    assert os.path.isfile("scons-in.py"), "scons-in.py not found"
    assert os.path.isdir("SCons"), "please copy the SCons directory"
    
    files = []
    for dirpath, dirnames, filenames in os.walk("SCons"):
        for f in filenames:
            if f.endswith(".py"):
                files.append(os.path.join(dirpath, f))

    name2src = {}
    for f in files:
        k = f.replace('/', '.')[:-3]
        name2src[k] = open(f).read()

    data = cPickle.dumps(name2src, 2)
    data = zlib.compress(data, 9)
    data = base64.encodestring(data)

    data = '%s' % (data)
    
    
    scons = open("scons-in.py").read()
    scons = scons.replace('@SOURCES@', data)
    open("scons.py", "w").write(scons)
    os.chmod("scons.py", 0755)
    
if __name__=='__main__':
    main()
