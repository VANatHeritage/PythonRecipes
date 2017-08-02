# ------------------------------------------------------------------------------------------
# CombineNHDPolygons.py
# Version:  ArcGIS 10.2 / Python 2.7
# Creation Date:  2015-07-10
# Last Edit:  2015-07-10
# Creator:  Kirsten R. Hazler
#
# Summary:  Combines NHDArea and NHDWaterbody into a single polygon feature class.  Why aren't 
#           these combined as a single feature class to begin with?  I do not know.
#
# Usage Tips:
# 
# Required Arguments:
# ------------------------------------------------------------------------------------------

# Import required standard modules
import arcpy, os, sys, traceback

# Script arguments to be input by user
in_GDB = arcpy.GetParameterAsText(0) # Input NHD geodatabase
out_GDB = arcpy.GetParameterAsText(1) # Output geodatabase

# Environment settings and derived variables
arcpy.env.overwriteOutput = True
nhdArea = in_GDB + os.sep + 'Hydrography' + os.sep + 'NHDArea'
nhdWB = in_GDB + os.sep + 'Hydrography' + os.sep + 'NHDWaterbody'
nhdMerged = out_GDB + os.sep + 'NHD_Polys'

try:
   # Copy NHD feature classes to output GDB
   arcpy.AddMessage('Copying NHD polygon feature classes to output %s...' % nhdMerged)
   arcpy.FeatureClassToFeatureClass_conversion (nhdArea, out_GDB, 'tmpArea')
   arcpy.FeatureClassToFeatureClass_conversion (nhdWB, out_GDB, 'tmpWB')
   
   # Add and populate the SourceFC field
   arcpy.AddMessage('Adding source feature class attribute...')
   fcList = [['tmpArea', 'NHDArea'],['tmpWB', 'NHDWaterbody']]
   for Item in fcList:
      fc = out_GDB + os.sep + Item[0]
      sourceFC = Item[1]
      arcpy.AddField_management (fc, 'SourceFC', 'TEXT', '', '', 12, '', '', '', '')
      expression = "'%s'" % sourceFC
      arcpy.CalculateField_management (fc, 'SourceFC', expression, 'PYTHON')
      
   # Merge feature classes
   arcpy.AddMessage('Merging feature classes')
   arcpy.Merge_management ([out_GDB + os.sep + 'tmpArea', out_GDB + os.sep + 'tmpWB'], nhdMerged)
   
   # Add missing subtypes removed by Merge tool, and reattach their domains
   # It's possible this section may need modification in the future
   arcpy.AddMessage('Adding missing subtypes and reattaching domains...')
   TypeList = [[493, 'Estuary', 'Estuary FCode'],
             [378, 'Ice Mass', 'Ice Mass FCode'],
             [390, 'LakePond', 'LakePond FCode'],
             [361, 'Playa', 'Playa FCode'], 
             [436, 'Reservoir', 'Reservoir FCode'],
             [466, 'SwampMarsh', 'SwampMarsh FCode']]
   for Type in TypeList:
      arcpy.AddSubtype_management (nhdMerged, Type[0], Type[1])
      arcpy.AssignDomainToField_management (nhdMerged, 'FCode', Type[2], Type[0])
      arcpy.AssignDomainToField_management(nhdMerged,'FCode', Type[2], "'%s: %s'" % (Type[0], Type[1]))
   
# Cleanup   
   arcpy.AddMessage('Deleting temp data...')
   for Item in fcList:
      fc = out_GDB + os.sep + Item[0]
      arcpy.Delete_management (fc)
        
except:
  # Error handling code swiped from "A Python Primer for ArcGIS"
   tb = sys.exc_info()[2]
   tbinfo = traceback.format_tb(tb)[0]
   pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
   msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

   arcpy.AddError(msgs)
   arcpy.AddError(pymsg)
   arcpy.AddMessage(arcpy.GetMessages(1))

   print msgs
   print pymsg
   print arcpy.AddMessage(arcpy.GetMessages(1))
   