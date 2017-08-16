# This is an automatically generated Python toolbox template, created in ArcCatalog.

import arcpy


class Toolbox(object):
   def __init__(self):
      """Define the toolbox (the name of the toolbox is the name of the
      .pyt file)."""
      self.label = "Toolbox"
      self.alias = ""

      # List of tool classes associated with this toolbox
      self.tools = [Tool]


class Tool(object):
   def __init__(self):
      """Define the tool (tool name is the name of the class)."""
      self.label = "Tool"
      self.description = ""
      self.canRunInBackground = False

   def getParameterInfo(self):
      """Define parameter definitions"""
      """See here for more info: http://pro.arcgis.com/en/pro-app/arcpy/classes/parameter.htm"""
      param1 = arcpy.Parameter(
         displayName = "Name displayed in toolbox",
         name = "Simple name for reference",
         datatype = "See here for valid types: http://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/defining-parameter-data-types-in-a-python-toolbox.htm",
         parameterType = "Required/Optional/Derived",
         direction = "Input/Output")
      params = [param1]
      return params

   def isLicensed(self):
      """Set whether tool is licensed to execute."""
      return True

   def updateParameters(self, parameters):
      """Modify the values and properties of parameters before internal
      validation is performed.  This method is called whenever a parameter
      has been changed."""
      return

   def updateMessages(self, parameters):
      """Modify the messages created by internal validation for each tool
      parameter.  This method is called after internal validation."""
      return

   def execute(self, parameters, messages):
      """The source code of the tool."""
      return