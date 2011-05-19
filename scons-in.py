#! /usr/bin/env python

sources = """
@SOURCES@"""

import sys
import cPickle
import base64
import zlib
import imp

sources = cPickle.loads(zlib.decompress(base64.decodestring(sources)))


class DictImporter(object):
    sources = sources

    def find_module(self, fullname, path=None):
        if fullname in self.sources:
            return self
        if fullname + '.__init__' in self.sources:
            return self
        return None

    def load_module(self, fullname):
        import new, sys

        try:
            s = self.sources[fullname]
            is_pkg = False
        except KeyError:
            s = self.sources[fullname + '.__init__']
            is_pkg = True

        co = compile(s, fullname, 'exec')
        module = sys.modules.setdefault(fullname, new.module(fullname))
        module.__file__ = __file__
        module.__loader__ = self
        if is_pkg:
            module.__path__ = [fullname]

        exec co in module.__dict__
        return sys.modules[fullname]

    def get_source(self, name):
        res = self.sources.get(name)
        if res is None:
            res = self.sources.get(name + '.__init__')
        return res


importer = DictImporter()

old_find_module = imp.find_module
old_load_module = imp.load_module


def find_module(name, path=None):
    if path and path[0].startswith("SCons"):
        fullname = "%s.%s" % (path[0], name)
        return None, fullname, importer

    if name.startswith("_scons"):
        fullname = "SCons.compat.%s" % name
        return None, fullname, importer

    return old_find_module(name, path)


def load_module(fullname, file, path, desc):
    if desc is importer:
        return importer.load_module(path)
    return old_load_module(fullname, file, path, desc)

imp.find_module = find_module
imp.load_module = load_module

sys.meta_path.append(importer)

if __name__ == "__main__":
    import SCons.Script
    SCons.Script.main()
