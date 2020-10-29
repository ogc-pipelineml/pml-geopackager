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
This module defines the 'PipelineMLGeoPackagerAlgorithm' class.
"""

# Import (from the standard 'os' module) the 'path' sub-module.
from os import path

# Import (from the 'core' module in the 'qgis' package) the
# 'QgsProcessingAlgorithm', 'QgsProcessingParameterFile',
# and 'QgsProcessingParameterFileDestination' classes.
from qgis.core import (
  QgsProcessingAlgorithm, QgsProcessingParameterFile,
  QgsProcessingParameterFileDestination)

# Import (from the 'QtGui' module in the
# 'qgis.PyQt' package) the 'QIcon' class.
from qgis.PyQt.QtGui import QIcon

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the 'PipelineMLGeoPackagerAlgorithm' class
# (which extends the 'QgsProcessingAlgorithm' class).
class PipelineMLGeoPackagerAlgorithm(QgsProcessingAlgorithm):
    """
    This class implements the processing algorithm
    for the PipelineML GeoPackager QGIS plugin.
    """

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'groupId' method, which should return a fixed,
    # non-localized string containing only lowercase alphanumeric
    # characters and no spaces or other formatting characters.
    def groupId(self):
        """
        This method returns a string that uniquely
        identifies the group within a provider.
        """
        return 'tools'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'group' method, which
    # should return a localized string.
    def group(self):
        """
        This method returns the name of the
        group to which this algorithm belongs.
        """
        return 'Tools'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'name' method, which should return a fixed,
    # non-localized string containing only lowercase alphanumeric
    # characters and no spaces or other formatting characters.
    def name(self):
        """
        This method returns a string that uniquely
        identifies the algorithm within a provider.
        """
        return 'pml2gpkg'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'displayName' method, which should return a
    # localized string of no more than 4 words, using sentence case.
    def displayName(self):
        """
        This method returns a user-friendly algorithm name.
        """
        return 'PipelineML to GeoPackage'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'icon' method.
    def icon(self):
        """
        This method returns an icon for the algorithm.
        """
        return QIcon(path.join(path.dirname(__file__), 'icon.svg'))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'createInstance' method, which should
    # return a pristine instance of the algorithm class.
    def createInstance(self):
        """
        This method creates a new instance of the algorithm class.
        """
        return PipelineMLGeoPackagerAlgorithm()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'initAlgorithm' method, which should add
    # all required input parameters and output definitions.
    def initAlgorithm(self, config):
        """
        This method initializes the algorithm
        using the specified configuration.
        """

        # Add the input parameter: a PipelineML file.
        parameter = QgsProcessingParameterFile(
          'INPUT', 'Source PipelineML file',
          fileFilter='PipelineML files (*.pml;*.xml)')
        self.addParameter(parameter)

        # Add the output parameter: a GeoPackage file destination.
        parameter = QgsProcessingParameterFileDestination(
          'OUTPUT', 'Destination GeoPackage', 'GeoPackage files (*.gpkg)')
        self.addParameter(parameter)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'processAlgorithm' method, which should implement
    # processing logic and return a map of algorithm outputs.
    def processAlgorithm(self, parameters, context, feedback):
        """
        This method runs the algorithm using the specified parameters.
        """
        return {}
