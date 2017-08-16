# ----------------------------------------------------------------------------------------
# libToolboxHacks.py
# Version:  ArcGIS 10.3.1 / Python 2.7.8
# Creation Date: 2017-08-16
# Last Edit: 2017-08-16
# Creator:  Kirsten R. Hazler

# Summary:
# Functions to simplify the creation of Python toolboxes
# ----------------------------------------------------------------------------------------

import arcpy

def defineParam(p_name, p_displayName, p_datatype, p_parameterType, p_direction, defaultVal = None):
   '''Simplifies parameter creation. Thanks to http://joelmccune.com/lessons-learned-and-ideas-for-python-toolbox-coding/'''
   param = arcpy.Parameter(
      name = p_name,
      displayName = p_displayName,
      datatype = p_datatype,
      parameterType = p_parameterType,
      direction = p_direction)
   param.value = defaultVal 
   return param