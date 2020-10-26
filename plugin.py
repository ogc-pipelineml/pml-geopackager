# -*- coding: utf-8 -*-

# Copyright (C) 2020 PipelineML
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
This module defines the 'PipelineMLGeoPackagerPlugin' class.
"""

# Import (from the 'core' module in the
# 'qgis' package) the 'QgsApplication' class.
from qgis.core import QgsApplication

# Import (from the 'provider' module within this
# package) the 'PipelineMLGeoPackagerProvider' class.
from .provider import PipelineMLGeoPackagerProvider

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the 'PipelineMLGeoPackagerPlugin' class.
class PipelineMLGeoPackagerPlugin:
    """
    This class implements the PipelineML GeoPackager plugin for QGIS.
    """

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Define the required '__init__' method (i.e., the constructor),
    # which is called when a new object of this class is instantiated.
    def __init__(self, iface):
        """
        This method saves a reference to the QGIS interface.
        """
        self.iface = iface

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Define the required 'initGui' method,
    # which is called when the plugin is loaded.
    def initGui(self):
        """
        This method initializes a connection to the GUI.
        """

        # Add the plugin's processing provider to the application's
        # processing registry, saving a reference to
        # the provider so that it can be removed from
        # the registry later (via the 'unload' method).
        self.provider = PipelineMLGeoPackagerProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Define the required 'unload' method, which
    # is called when the plugin is unloaded.
    def unload(self):
        """
        This method cleans up the GUI.
        """

        # Remove the plugin's processing provider implementation
        # from the application's processing registry.
        QgsApplication.processingRegistry().removeProvider(self.provider)
