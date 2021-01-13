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
from osgeo.osr import SpatialReference
from qgis.core import (
  QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback,
  QgsProcessingParameterFile, QgsProcessingParameterFileDestination)
from qgis.PyQt.QtGui import QIcon


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the '_reset_globals' function, which
# should be called every time the algorithm runs.
def _reset_globals() -> None:
    """
    This function resets global variables for the algorithm.
    """

    # This list serves as a stack of XML element names.
    global _stack
    _stack = []

    # This dictionary keeps track of layers
    # that have been created in the GeoPackage.
    global _layers
    _layers = {}

    # This dictionary stores names and values
    # of fields for the current feature.
    global _fields
    _fields = {}

    # This event is used to signal
    # completion of the XML parsing thread.
    global _event
    _event = Event()

    # This object represents the default spatial
    # reference system (SRS) of the GeoPackage.
    global _srs
    _srs = SpatialReference()

    # This dictionary is used to determine the data
    # types of numeric fields.  Any field not appearing
    # in this dictionary is taken as text/string.
    global _types
    _types = {
      'length': ogr.OFTReal,
      'startEngineeringStation': ogr.OFTReal,
      'endEngineeringStation': ogr.OFTReal,
      'pressureRating': ogr.OFTReal,
      'startPosition': ogr.OFTReal,
      'endPosition': ogr.OFTReal,
      'compressorPowerRating': ogr.OFTReal,
      'compressorRatedFlow': ogr.OFTReal,
      'compressorPressureSuction': ogr.OFTReal,
      'compressorPressureDischarge': ogr.OFTReal,
      'linepipeCoverDepthMinimum': ogr.OFTReal,
      'meterFlowRateMinimum': ogr.OFTReal,
      'meterFlowRateMaximum': ogr.OFTReal,
      'pumpPowerRating': ogr.OFTReal,
      'pumpRatedFlow': ogr.OFTReal,
      'pumpPressureSuction': ogr.OFTReal,
      'pumpPressureDischarge': ogr.OFTReal,
      'teeCenterToEndRun': ogr.OFTReal,
      'teeCenterToEndOutlet': ogr.OFTReal,
      'valveActuationTime': ogr.OFTReal,
      'casingVentCount': ogr.OFTInteger,
      'coatingLayerNumber': ogr.OFTInteger,
      'sleevePressureRating': ogr.OFTReal,
      'pipeconnectorNumber': ogr.OFTInteger}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the '_handle_element_start' function, which is called (by the
# XML parser) for the start of every element in the PipelineML file.
def _handle_element_start(name: str, attributes: dict) -> None:
    """
    This function processes the start-tag of a PipelineML element.
    """

    global _feedback
    global _dataset
    s = ''
    for i in range(len(_stack)):
        s += '.'
    _feedback.pushDebugInfo(s + name + ' (start)')

    # If the stack is empty, all that's needed is to
    # push the name of this element onto the stack (to
    # indicate that this element is now being processed).
    if len(_stack) < 1:
        _stack.append(name)
        return

    # If 'component' is on top of the stack,
    # this element must represent a feature.
    if _stack[-1] == 'component' and name not in _layers:
        # If necessary, create the layer for this feature.
        _feedback.pushInfo('Creating ' + name + ' layer')
        _layers[name] = _dataset.CreateLayer(name, _srs, ogr.wkbUnknown)

    # If 'component' is second from the top of the stack, this element
    # must represent a field for the current feature.  (The 'location'
    # element represents the geometry field and is handled separately.)
    elif (len(_stack) > 2 and _stack[-2] == 'component'
          and name != 'location'):
        # If necessary, create the field.
        layer_name = _stack[-1]
        if _layers[layer_name].FindFieldIndex(name, 1) < 0:
            _feedback.pushInfo('Creating ' + name + ' field'
                               ' in ' + layer_name + ' layer')
            if name in _types:
                type = _types[name]
            else:
                type = ogr.OFTString
            field_defn = ogr.FieldDefn(name, type)
            _layers[layer_name].CreateField(field_defn)

        # If this element has a 'title' attribute, use that
        # attribute's value as the field value.  (Otherwise,
        # the field value should be in the character data.)
        for key in list(attributes):
            if key == 'title' or key.endswith(':title'):
                _fields[name] = attributes[key]
                break

    # Push the name of this element onto the stack to
    # indicate that this element is now being processed.
    _stack.append(name)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the '_handle_character_data' function, which is called
# (by the XML parser) for character data in the PipelineML file.
def _handle_character_data(data: str) -> None:
    """
    This function processes the content of a PipelineML element.
    """

    # Ignore whitespace.
    if data.isspace():
        return

    global _feedback
    s = ''
    for i in range(len(_stack)):
        s += '.'
    _feedback.pushDebugInfo(s + 'Character Data: "' + data + '"')

    # If 'defaultCRS' is on top of the stack, this element specifies
    # the default coordinate reference system for the dataset.
    if len(_stack) > 1 and _stack[-1] == 'defaultCRS':
        name = data.partition(' ')[2].strip('()')
        _srs.SetFromUserInput(name)
        return

    # Any further processing of character data
    # requires at least four items in the stack.
    if len(_stack) < 4:
        return

    # If 'component' is third from the top of the stack,
    # this element should represent a field for the current
    # feature, and the character data should be used as the
    # field value (except for the 'location' element, which
    # represents the geometry field and is handled separately).
    if _stack[-3] == 'component' and _stack[-1] != 'location':
        _fields[_stack[-1]] = data

    # If 'location' is third from the top of the stack, this element
    # should represent a set of geospatial coordinates in GML format.
    elif _stack[-3] == 'location':
        # The element name second from the top
        # should indicate the geometry type.
        gml_type = _stack[-2].split(':', 1)[-1]
        if gml_type == 'Point':
            wkb_type = ogr.wkbPoint
        elif gml_type == 'LineString':
            wkb_type = ogr.wkbLineString
        elif gml_type == 'Polygon':
            wkb_type = ogr.wkbPolygon
        else:
            _feedback.reportError('Unknown geometry type: ' + gml_type)
            wkb_type = ogr.wkbUnknown

        # Create a geometry object from the GML coordinates.
        _feedback.pushInfo('Creating ' + gml_type + ' geometry'
                           ' for ' + _stack[-4] + ' feature')
        geom = ogr.Geometry(wkb_type)
        pos_list = data.split()
        for i in range(0, len(pos_list), 2):
            x = float(pos_list[i])
            y = float(pos_list[i + 1])
            geom.AddPoint_2D(x, y)
        _fields['location'] = geom


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Define the '_handle_element_end' function, which is called (by the
# XML parser) for the end of every element in the PipelineML file.
def _handle_element_end(name: str) -> None:
    """
    This function processes the end-tag of a PipelineML element.
    """

    global _feedback
    global _fields
    s = ''
    for i in range(len(_stack) - 1):
        s += '.'
    _feedback.pushDebugInfo(s + name + ' (end)')

    # If 'component' is second from the top of the
    # stack (just beneath the name of this element),
    # this element must represent a feature.
    if len(_stack) > 2 and _stack[-2] == 'component':
        # Use the schema information from the appropriate
        # layer to create a new feature object.
        _feedback.pushInfo('Creating ' + name + ' feature')
        feature_defn = _layers[name].GetLayerDefn()
        feature = ogr.Feature(feature_defn)

        # Set the value of each field for the feature.  (Note
        # that the 'location' field represents the geometry).
        for key, value in _fields.items():
            if key == 'location':
                feature.SetGeometryDirectly(value)
            else:
                feature.SetField(key, value)

        # Add the feature to the appropriate layer.
        _feedback.pushInfo('Adding feature to ' + name + ' layer')
        _layers[name].CreateFeature(feature)
        feature.Destroy()
        _fields = {}

    # Pop the stack to indicate that this
    # element is no longer being processed.
    _stack.pop()

    # If the stack is empty, XML parsing
    # is complete.  Signal the main thread.
    if len(_stack) < 1:
        _feedback.pushDebugInfo('XML parsing completed')
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

        # Reset the values of global variables.
        _reset_globals()

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
            parser.buffer_text = True
            parser.StartElementHandler = _handle_element_start
            parser.CharacterDataHandler = _handle_character_data
            parser.EndElementHandler = _handle_element_end
            parser.ParseFile(pml_file)

        # Wait for the XML parsing thread to signal completion.
        while not _event.wait(1) and not feedback.isCanceled():
            pass

        # Close the dataset to ensure that all data is written
        # and resources are recovered (file handle closed, etc.).
        _dataset = None

        # Add the GeoPackage layers to the current project.
        project = context.project()
        for name in list(_layers):
            layer_path = gpkg_path + '|layername=' + name
            details = QgsProcessingContext.LayerDetails(name, project)
            context.addLayerToLoadOnCompletion(layer_path, details)

        # Return the output.
        return {'OUTPUT': gpkg_path}
