"""
    PyICS

    Framework for the UvA bachelor course `Introduction Computational Science'.
    Contains functionality for creating, visualizing and testing simulations.
    See documentation of `Model' and `paramsweep' for more details.
"""

# Placeholder file to make the `pyics' directory a python module.
# Additionally, we expose the Model and paramsweep as direct members of this
# module, so scripts can do
#   >>> import pyics.Model
#   >>> import pyics.paramsweep
# etc.

from .pycx_gui import GUI
from .model import Model
from .paramsweep import paramsweep

# When importing everything (from pyics import *) limit it so useful stuff.
__all__ = ['GUI', 'Model', 'paramsweep']
