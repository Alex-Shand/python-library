"""Export decorators."""

import sys

# From: https://speakerdeck.com/dabeaz/modules-and-packages-live-and-let-die?slide=56
def export(func):
    """Module level export decorator, appends function name to __all__."""
    mod = sys.modules[func.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(func.__name__)
    else:
        mod.__all__ = [func.__name__]
    return func
export(export)

@export
def cls_export(func):
    """Class level export decorator, should be used in conjuction with
    collect_exports."""
    func._exported = True # pylint: disable=protected-access
    return func

@export
def collect_exports(cls):
    """Fill the __all__ list of a class with functions marked with _exported."""
    if not hasattr(cls, '__all__'):
        cls.__all__ = []
    for name, func in cls.__dict__.items():
        if getattr(func, '_exported', False):
            cls.__all__.append(name)
    return cls
