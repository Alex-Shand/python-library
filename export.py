"""Export decorators."""

import sys

# From: https://speakerdeck.com/dabeaz/modules-and-packages-live-and-let-die?slide=56
def export(func):
    """Module level export decorator, appends function name to __all__."""
    mod = sys.modules[func.__module__]
    all_list = getattr(mod, '__all__', [])
    all_list.append(func.__name__)
    setattr(mod, '__all__', all_list)
    return func
export(export)

@export
def cls_export(func):
    """Class level export decorator, should be used in conjuction with
    collect_exports."""
    setattr(func, '_exported', True)
    return func

@export
def collect_exports(cls):
    """Fill the __all__ list of a class with functions marked with _exported."""
    for name, func in cls.__dict__.items():
        if getattr(func, '_exported', False):
            all_list = getattr(cls, '__all__', [])
            all_list.append(func.__name__)
            setattr(cls, '__all__', all_list)
    return cls
