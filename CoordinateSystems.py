# Working with coordinate systems

import arcpy, os

def printMsg(msg):
   arcpy.AddMessage(msg)
   print msg

def ProjectToMatch (fcTarget, fcTemplate):
   """Project a target feature class to match the coordinate system of a template feature class"""
   # Get the spatial reference of your target and template feature classes
   srTarget = arcpy.Describe(fcTarget).spatialReference # This yields an object, not a string
   srTemplate = arcpy.Describe(fcTemplate).spatialReference 

   # Get the geographic coordinate system of your target and template feature classes
   gcsTarget = srTarget.GCS # This yields an object, not a string
   gcsTemplate = srTemplate.GCS

   # Compare coordinate systems and decide what to do from there. 
   if srTarget.Name == srTemplate.Name:
      printMsg('Coordinate systems match; no need to do anything.')
      return fcTarget
   else:
      printMsg('Coordinate systems do not match; proceeding with re-projection.')
      if fcTarget[-3:] == 'shp':
         fcTarget_prj = fcTarget[:-4] + "_prj.shp"
      else:
         fcTarget_prj = fcTarget + "_prj"
      if gcsTarget.Name == gcsTemplate.Name:
         printMsg('Datums are the same; no geographic transformation needed.')
         arcpy.Project_management (fcTarget, fcTarget_prj, srTemplate)
      else:
         printMsg('Datums do not match; re-projecting with geographic transformation')
         # Get the list of applicable geographic transformations
         # This is a stupid long list
         transList = arcpy.ListTransformations(srTarget,srTemplate) 
         # Extract the first item in the list, assumed the appropriate one to use
         geoTrans = transList[0]
         # Now perform reprojection with geographic transformation
         arcpy.Project_management (fcTarget, fcTarget_prj, srTemplate, geoTrans)
      printMsg("Re-projected data is %s." % fcTarget_prj)
      return fcTarget_prj
      
# Use the section below to enable a function (or set of functions) to be run directly from this free-standing script (i.e., not as an ArcGIS toolbox tool)
def main():
   # Set up your variables here
   #fcTarget = r'C:\Testing\RCL_Test.gdb\BoatRamps_conus'
   #fcTarget = r'C:\Testing\RCL_Test.gdb\BoatRamps'
   fcTarget = r'C:\Testing\BoatRamps_conus.shp'
   fcTemplate = r'C:\Testing\RCL_Test.gdb\RCL2017Q3_Subset'
   
   # Include the desired function run statement(s) below
   ProjectToMatch (fcTarget, fcTemplate)
   
   # End of user input
   
if __name__ == '__main__':
   main()