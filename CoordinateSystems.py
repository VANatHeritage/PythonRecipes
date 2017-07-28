# Working with coordinate systems

import arcpy, os
# Define your feature class
fc1 = r'insert_path_to_dataset_here'

# Get the spatial reference of your feature class
sr1 = arcpy.Describe(fc1).spatialReference # This yields an object, not a string
sr1_name = sr1.Name # This yields a string

# Get the geographic coordinate system of your feature class
gcs1 = sr1.GCS # This yields an object, not a string
gcs1_name = gcs1.Name # This yields a string

# Assuming you have already defined a second feature class, fc2, and its spatial reference and coordinate system, similar to above for fc1, you can compare coordinate systems and decide what to do from there. 

# Let's say you want fc1 to be projected to the same coordinate system as fc2.
if sr1_name == sr2_name:
   arcpy.AddMessage('Coordinate systems match; no need to do anything.')
else:
   arcpy.AddMessage('Coordinate systems do not match; proceeding with re-projection.')
   fc1_prj = r'insert_output_path_here'
   if gs1_name == gcs2_name:
      arcpy.AddMessage('Datums are the same; no geographic transformation needed.')
      arcpy.Project_management (fc1, fc1_prj, sr2)
   else:
      arcpy.AddMessage('Datums do not match; re-projecting with geographic transformation')
      # Get the list of applicable geographic transformations
      transList = arcpy.ListTransformations(sr1,sr2) # This is a stupid long list
      # Extract the first item in the list which I hope is the right transformation to use
      geoTrans = transList[0]
      # Now perform reprojection with geographic transformation
      arcpy.Project_management (fc1, fc1_prj, sr2, geoTrans)