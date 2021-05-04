import os, glob, inspect
from importlib import import_module
import filetype as ft

# this is the worst thing ever
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__filetypes = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
__kl_classes = [inspect.getmembers(import_module("." + f, package="filetypes"), inspect.isclass)[0] for f in __filetypes]
for kl_class in __kl_classes:
    ft.add_type(kl_class[1]())