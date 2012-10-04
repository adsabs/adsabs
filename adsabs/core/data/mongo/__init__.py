from models import *

import sys
import inspect

def data_models():
    dc = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, DataCollection):
            dc.append(obj)
    return dc
        