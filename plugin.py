# -*- coding: utf-8 -*-
"""This module defines the PipelineMLGeoPackagerPlugin class."""

# Import the standard 'inspect' module.
import inspect

# Import (from the 'core' module in the 'qgis'
# package) the 'Qgis' and 'QgsMessageLog' classes.
from qgis.core import Qgis, QgsMessageLog

# Define the PipelineMLGeoPackagerPlugin class.
class PipelineMLGeoPackagerPlugin:
    """
    This class implements the PipelineML GeoPackager plugin for QGIS.
    """

    # Define the required __init__ function (i.e., the constructor),
    # which is called when a new object of this class is instantiated.
    def __init__(self, iface):
        """Save a reference to the QGIS interface."""
        log_function_name()
        self.iface = iface

    # Define the required initGui function,
    # which is called when the plugin is loaded.
    def initGui(self):
        """Initialize a connection to the GUI."""
        log_function_name()

    # Define the required unload function, which
    # is called when the plugin is unloaded.
    def unload(self):
        """Cleanup the GUI."""
        log_function_name()

# Define a 'log_function_name' function,
# which is used internally by our plugin.
def log_function_name():
    """
    Add to the log instance a message containing
    the name of the calling function.
    """
    QgsMessageLog.logMessage(
      inspect.currentframe().f_back.f_code.co_name,
      'PipelineML GeoPackager', Qgis.Info)
