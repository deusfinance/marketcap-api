from .si import *

try:
    from .local_settings import *
except ImportError:
    print('WARNING: local_settings.py is missed')
