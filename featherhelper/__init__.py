from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .feather_helper import setdir, name, push, pull, FeatherHelperError, exc
