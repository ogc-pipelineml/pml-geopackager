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
This module defines the 'PipelineMLGeoPackagerProvider' class.
"""

# Import (from the standard 'os' module) the 'path' sub-module.
from os import path

# Import (from the 'core' module in the 'qgis'
# package) the 'QgsProcessingProvider' class.
from qgis.core import QgsProcessingProvider

# Import (from the 'QtGui' module in the
# 'qgis.PyQt' package) the 'QIcon' class.
from qgis.PyQt.QtGui import QIcon

# Import (from the 'algorithm' module within this
# package) the 'PipelineMLGeoPackagerAlgorithm' class.
from .algorithm import PipelineMLGeoPackagerAlgorithm

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the 'PipelineMLGeoPackagerProvider' class
# (which extends the 'QgsProcessingProvider' class).
class PipelineMLGeoPackagerProvider(QgsProcessingProvider):
    """
    This class implements the processing provider
    for the PipelineML GeoPackager QGIS plugin.
    """

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'id' method, which should return
    # a short, non-localized, character-only string.
    def id(self):
        """
        This method returns a string that
        uniquely identifies the provider.
        """
        return 'pml'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'name' method, which should
    # return a short, localized string.
    def name(self):
        """
        This method returns a string that describes the provider.
        """
        return 'PipelineML'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'icon' method.
    def icon(self):
        """
        This method returns an icon for the provider.
        """
        return QIcon(path.join(path.dirname(__file__), 'pml.svg'))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'loadAlgorithms' method, which
    # should register all associated algorithms.
    def loadAlgorithms(self):
        """
        This method loads all algorithms belonging to this provider.
        """
        algorithm = PipelineMLGeoPackagerAlgorithm()
        self.addAlgorithm(algorithm)
