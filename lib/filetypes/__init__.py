import glob, os, inspect, importlib
import filetype as ft

modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
kl2_filetypes = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
__kl_classes = [inspect.getmembers(importlib.import_module("." + f, package="lib.filetypes"), inspect.isclass)[0] for f in kl2_filetypes]
for kl_class in __kl_classes:
    ft.add_type(kl_class[1]())