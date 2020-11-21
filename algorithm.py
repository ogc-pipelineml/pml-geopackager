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

from os import path
from threading import Event
from xml.parsers import expat
from osgeo import gdal
from osgeo import ogr
from qgis.core import (
  QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback,
  QgsProcessingParameterFile, QgsProcessingParameterFileDestination)
from qgis.PyQt.QtGui import QIcon

# This list serves as a stack of XML elements.
_stack = []

# This event is used to signal completion of the XML parsing thread.
_event = Event()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the 'handle_element_start' function, which is called (by the
# XML parser) for the start of every element in the PipelineML file.
def handle_element_start(name: str, attributes: dict) -> None:
    global _feedback
    global _dataset
    if len(_stack) > 0 and _stack[-1] == 'component':
        _feedback.pushInfo('Creating ' + name + ' layer')
        _dataset.CreateLayer(name, None, ogr.wkbUnknown)
    _stack.append(name)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the 'handle_element_end' function, which is called (by the
# XML parser) for the end of every element in the PipelineML file.
def handle_element_end(name: str) -> None:
    _stack.pop()

    # If the stack is empty, XML parsing
    # is complete.  Signal the main thread.
    if len(_stack) < 1:
        _event.set()

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
    def groupId(self) -> str:
        """
        This method returns a string that uniquely
        identifies the group within a provider.
        """
        return 'tools'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'group' method, which
    # should return a localized string.
    def group(self) -> str:
        """
        This method returns the name of the
        group to which this algorithm belongs.
        """
        return 'Tools'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'name' method, which should return a fixed,
    # non-localized string containing only lowercase alphanumeric
    # characters and no spaces or other formatting characters.
    def name(self) -> str:
        """
        This method returns a string that uniquely
        identifies the algorithm within a provider.
        """
        return 'pml2gpkg'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'displayName' method, which should return a
    # localized string of no more than 4 words, using sentence case.
    def displayName(self) -> str:
        """
        This method returns a user-friendly algorithm name.
        """
        return 'PipelineML to GeoPackage'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'icon' method.
    def icon(self) -> QIcon:
        """
        This method returns an icon for the algorithm.
        """
        name = path.dirname(__file__)
        name = path.join(name, 'icon.svg')
        return QIcon(name)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'createInstance' method, which should
    # return a pristine instance of the algorithm class.
    def createInstance(self) -> 'PipelineMLGeoPackagerAlgorithm':
        """
        This method creates a new instance of the algorithm class.
        """
        return PipelineMLGeoPackagerAlgorithm()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Override the 'initAlgorithm' method, which should add
    # all required input parameters and output definitions.
    def initAlgorithm(self, config: 'Dict[str, Any]' = {}) -> None:
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
    def processAlgorithm(self, parameters: 'Dict[str, Any]',
            context: QgsProcessingContext,
            feedback: QgsProcessingFeedback) -> 'Dict[str, Any]':
        """
        This method runs the algorithm using the specified parameters.
        """

        # Retrieve the value of the output parameter
        # (i.e., the GeoPackage file destination).
        gpkg_path = self.parameterAsFileOutput(parameters, 'OUTPUT', context)

        # Fetch the GDAL driver for the GeoPackage file format.
        driver = gdal.GetDriverByName('GPKG')

        # Use the driver to create a new
        # dataset (i.e., a new GeoPackage).
        global _dataset
        _dataset = driver.Create(gpkg_path, 0, 0, 0, gdal.GDT_Unknown)

        # Retrieve the value of the input
        # parameter (i.e., the PipelineML file).
        pml_path = self.parameterAsFile(parameters, 'INPUT', context)

        # Open the PipelineML file for reading.  (Note that the XML
        # parser requires the file to be opened in binary mode.)
        with open(pml_path, 'rb') as pml_file:
            global _feedback
            _feedback = feedback

            # Parse the PipelineML file.  (The handler functions
            # called by the XML parser populate the GeoPackage
            # based on the PipelineML file's contents.)
            parser = expat.ParserCreate()
            parser.StartElementHandler = handle_element_start
            parser.EndElementHandler = handle_element_end
            parser.ParseFile(pml_file)

        # Wait for the XML parsing thread to signal completion.
        _event.wait()

        # Close the dataset to ensure that all data is written
        # and resources are recovered (file handle closed, etc.).
        _dataset = None

        # Return the output.
        return {'OUTPUT': gpkg_path}
