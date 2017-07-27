# Here are some examples of how to create and delete directories and ArcGIS file types

# Import necessary modules
import arcpy, os

# Specify the directory in which you want to store your data
dirPath = r'C:\\myProjects'

# If the directory 'myProjects' doesn't already exist on the C-drive, create it
if not arcpy.Exists(dirPath):
   arcpy.CreateFolder_management(r'C:\\', 'myProjects')

# Make a file geodatabase
gdbName = 'myGDB.gdb'
arcpy.CreateFileGDB_management(dirPath, gdbName)
# Further reference: http://desktop.arcgis.com/en/arcmap/10.3/tools/data-management-toolbox/create-file-gdb.htm

# Make a point feature class within the geodatabase
gdbPath = dirPath + os.sep + gdbName
fcName = 'myFeatures'
geomType = 'POINT'
myTemplate = dirPath + os.sep + 'myTemplate.shp' # reference to some shapefile
spatialRef = arcpy.Describe(myTemplate).spatialReference # get spatial reference from template
arcpy.CreateFeatureclass_management (gdbPath, fcName, geomType, myTemplate, '', '', spatialRef)

# Delete the geodatabase
arcpy.Delete_management(gdbPath)