# -*- coding: utf-8 -*-

# Libaddon for Anki
# Updated for modern Anki (2.1.45+)

"""
Components related to packaging third-party code and libraries
with Anki add-ons
"""

import sys
import os

__all__ = [
    "VersionSpecificImporter",
    "addPathToModuleLookup",
    "addSubdirPathToModuleLookup"
]


class VersionSpecificImporter:
    """
    A PEP 302 meta path importer for finding the right vendored package
    among bundled packages specific to Anki 2.1 and packages common to both.
    """

    module_dir = "anki21"

    def __init__(self, root_name, managed_imports=(), vendor_pkg=None):
        self.root_name = root_name
        self.managed_imports = set(managed_imports)
        self.vendor_pkg = vendor_pkg or self.root_name

    @property
    def search_path(self):
        yield ".".join((self.vendor_pkg, self.module_dir, ""))
        yield ".".join((self.vendor_pkg, "common", ""))
        yield ''

    def find_module(self, fullname, path=None):
        root, base, target = fullname.partition(self.root_name + '.')
        if root:
            return
        if not any(map(target.startswith, self.managed_imports)):
            return
        return self

    def load_module(self, fullname):
        root, base, target = fullname.partition(self.root_name + '.')
        for prefix in self.search_path:
            try:
                extant = prefix + target
                __import__(extant)
                mod = sys.modules[extant]
                sys.modules[fullname] = mod
                if sys.version_info >= (3, ):
                    del sys.modules[extant]
                return mod
            except ImportError:
                pass
        else:
            raise ImportError(
                "The '{target}' package is required; "
                "normally this is bundled with this add-on so if you get "
                "this warning, consult the packager of your "
                "distribution.".format(**locals())
            )

    def install(self):
        if self not in sys.meta_path:
            sys.meta_path.append(self)


STRINGTYPES = (str,)
LOOKUP_SUBDIRS = ["common", "anki21"]

def _addPathToModuleLookup(path):
    sys.path.insert(0, path)

def addPathToModuleLookup(path):
    assert isinstance(path, STRINGTYPES)
    assert os.path.isdir(path)
    _addPathToModuleLookup(path)

def addSubdirPathToModuleLookup(path):
    assert isinstance(path, STRINGTYPES)
    assert os.path.isdir(path)
    for path in [os.path.join(path, subdir) for subdir in LOOKUP_SUBDIRS]:
        if not os.path.isdir(path):
            continue
        _addPathToModuleLookup(path)
