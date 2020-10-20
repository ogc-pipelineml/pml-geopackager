# -*- coding: utf-8 -*-
"""
This package encapsulates the PipelineML GeoPackager plugin for QGIS.
"""

# The presence of this file defines the directory that
# contains it (e.g., 'pmlgpkg') as a Python package.

# Import (from the 'plugin' module within this package) the
# 'PipelineMLGeoPackagerPlugin' class directly into this
# module's symbol table so that the class can be referred
# to by its name alone (without the package.module prefix).
from .plugin import PipelineMLGeoPackagerPlugin

# Define the required 'classFactory' function,
# which is called when the plugin is loaded.
def classFactory(iface):
    """Return an instance of the plugin class."""
    plugin.log_function_name()
    return PipelineMLGeoPackagerPlugin(iface)
