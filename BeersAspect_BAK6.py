# -------------------------------------------------------------------------------------------------------
# BeersAspect.py
# Version:  Python 2.7.5 / ArcGIS 10.2.2
# Creation Date: 2015-06-04
# Last Edit: 2015-07-31
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Uses an input Digital Elevation Model (DEM) to derive aspect, and then the Beers transformation
# of aspect, which ranges from 0 (most exposed) to 2 (most sheltered). Processing is done by USGS quads
# or by other units defined by a polygon feature class. 

#     The ASPECT function is first applied.  For cells with a flat slope, the aspect is undefined,
# represented by the value -1.  The Beers aspect transformation is applied to all cells where aspect is 
# defined.  

#     A hydrography raster is then used to "burn in" water and wetland features, which are set to a
# "neutral" value of 1. For all remaining cells where the undefined aspect is coded as -1, Beers aspect 
# is derived from the focal mean of the smallest possible neighborhood around them.  The neighborhood is 
# expanded as needed, up to user-specified limit, until a valid zonal mean value is obtained for Beers Aspect.  

#     Once the neighborhood expansion limit has been reached, any remaining NoAspect cells are assigned
# the neutral value of 1, since it follows that these cells are surrounded by many other cells with flat slopes.

# Reference:
#     Beers, Thomas W., Peter E. Dress, and Lee C. Wensel.  1966.  Notes and observations.  Aspect 
# transformation in site productivity research.  Journal of Forestry 64:691-692.
#
# Note:  
#     It's important to distinguish between "NoData" which is the boundary areas outside the DEM,
# versus "NoAspect" (-1) cells within the DEM.  For focal mean to work properly, the NoAspect
# cells need to be coded "NoData", so that the -1 value doesn't contaminate the mean.  Thus 
# this script converts back and forth between -1 and NoData as needed.
#
# -------------------------------------------------------------------------------------------------------

# Import required modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system functionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
from datetime import datetime # for time-stamping

# Script arguments to be input by user
inDEM = arcpy.GetParameterAsText(0) # Input DEM
   # Default: N:\SDM\ProcessedData\NED_Products\NED_mosaics.gdb\rd_NED30m
inBurn = arcpy.GetParameterAsText(1) # Raster representing waterbodies to be "burned in"
   # Default: N:\SDM\ProcessedData\SDM_Masks.gdb\rd_BeersBurn
inBnd = arcpy.GetParameterAsText(2) # Polygon feature class determining outer processing boundary
   # Default: N:\SDM\ProcessedData\SDM_ReferenceLayers.gdb\fc_bndSDM_buff5k
inProcUnits = arcpy.GetParameterAsText(3) # Polygon feature class determining units to be processed
   # Default : N:\SDM\ProcessedData\SDM_ReferenceLayers.gdb\fc_ned_1arcsec_g
inFld = arcpy.GetParameterAsText(4) # Field containing the unit ID
   # Default: FILE_ID
nLimit = arcpy.GetParameter(5) # Limit to the neighborhood radius (in cells) used to interpolate Beers Aspect
   # Default: 5
outGDB = arcpy.GetParameterAsText(6) # Geodatabase to hold final products
scratchGDB = arcpy.GetParameterAsText(7) # Geodatabase to hold intermediate products
ProcLogFile = arcpy.GetParameterAsText(8) # Text file to contain processing results

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten
arcpy.env.snapRaster = inDEM
CellSize = int(arcpy.GetRasterProperties_management (inDEM, 'CELLSIZEX').getOutput(0))
LimitList = list() # List to hold processing results where neighborhood limit was reached
FailList = list() # List to keep track of units where processing failed
deg2rad = math.pi/180.0 # needed for conversion from degrees to radians for input to Cos function

# Create and write to a log file.
# If this log file already exists, it will be overwritten.  If it does not exist, it will be created.
Log = open(ProcLogFile, 'w+') 
FORMAT = '%Y-%m-%d %H:%M:%S'
timestamp = datetime.now().strftime(FORMAT)
Log.write("Process logging started %s \n\n" % timestamp)
Log.write('Input parameters are...\n')
Log.write('Input DEM: %s\n' % inDEM)
Log.write('Input hydro burn raster: %s\n' % inBurn)
Log.write('Input processing boundary: %s\n' % inBnd)
Log.write('Input processing units: %s\n' % inProcUnits)
Log.write('Processing unit ID field: %s\n' % inFld)
Log.write('Neighborhood expansion limit: %s\n' % str(nLimit))
Log.write('Output geodatabase: %s\n' % outGDB)
Log.write('Scratch geodatabase: %s\n' % scratchGDB)
Log.write('Processed unit(s): See below.\n')

ProcUnits = arcpy.da.SearchCursor(inProcUnits, [inFld])

for Unit in ProcUnits:
   UnitID = Unit[0]
   arcpy.AddMessage('Working on unit %s...' % UnitID)
   Log.write('Processing unit: %s\n' % UnitID)
     
   # Make a feature class with the single unit's shape, buffer it, then clip it
   where_clause = "%s = '%s'" %(inFld, UnitID) # Create the feature selection expression
   arcpy.MakeFeatureLayer_management (inProcUnits, 'selectFC', where_clause) 
   
   buffFC = scratchGDB + os.sep + 'buffFC' + UnitID
   buffDist = CellSize * nLimit
   arcpy.Buffer_analysis ('selectFC', buffFC, buffDist)
   
   clipFC = scratchGDB + os.sep + 'clipFC'
   arcpy.Clip_analysis (buffFC, inBnd, clipFC)
   
   # Clip the DEM to the above feature
   clipDEM = scratchGDB + os.sep + 'clipDEM'
   extent = arcpy.Describe(clipFC).extent
   XMin = extent.XMin
   YMin = extent.YMin
   XMax = extent.XMax
   YMax = extent.YMax
   rectangle = '%s %s %s %s' %(XMin, YMin, XMax, YMax) 
   arcpy.Clip_management (inDEM, rectangle, clipDEM, clipFC, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
   
   # Set processing mask
   arcpy.env.mask = clipDEM 
   
   try:
      # Create Aspect in degrees
      rdAspect = Aspect(clipDEM)
      rdAspect.save(scratchGDB + os.sep + 'rdAspect_' + UnitID)
      arcpy.AddMessage('Created aspect raster; saved to scratch geodatabase')

      # Create Beers Aspect
      # Set to -1 if Aspect = -1 (flat slope)
      outBeers = outGDB + os.sep + 'rdBeers_' + UnitID
      rdBeers = Con (rdAspect == -1, -1, (Cos((45 - rdAspect)*deg2rad) + 1))
      rdBeers.save(scratchGDB + os.sep + 'InitBeers_' + UnitID) # This version is not overwritten later; saved just in case
      rdBeers.save(outBeers) # This version will be overwritten repeatedly below
      arcpy.AddMessage('Created initial Beers Aspect raster.')
      
      # Burn in the waterbodies, setting to neutral value of 1
      arcpy.AddMessage('Burning in waterbodies...')
      rdBeers = Con (IsNull(inBurn) == 0, 1, rdBeers)
      burnBeers = scratchGDB + os.sep + 'BurnBeers_' + UnitID
      rdBeers.save(burnBeers) # This version is not overwritten later; saved just in case
      rdBeers.save(outBeers) # This version will be overwritten repeatedly below
      
      # Initialize a binary raster indicating where the NoAspect (-1) cells are: 1 if no aspect, otherwise 0
      rdNoAspect = Con (rdBeers, 1, 0, 'VALUE = -1') 
      rdNoAspect.save(scratchGDB + os.sep + 'InitNoAspect_' + UnitID) # This version is not overwritten later; saved just in case
      rdNoAspect.save(scratchGDB + os.sep + 'rdNoAspect') # This version will be overwritten repeatedly below

      # Get the number of cells with no aspect
      rows = arcpy.SearchCursor (rdNoAspect, "Value = 1", "", "Count", "")
      row = rows.next()
      if row:
         NumNulls = row.getValue("Count") # This yields the number of cells with no aspect
         NumCells = 0 # Initialize number of cells for neighborhood statistics
         arcpy.AddMessage('Now filling in NoAspect pixels with neighborhood means.  This will take some time...')
      else:
         NumNulls = 0
            
      while NumNulls > 0:
      # Use expanding neighborhoods as needed to fill in cells with undefined aspect
         arcpy.AddMessage('There are currently %s NoAspect cells in the Beers Aspect raster' %int(NumNulls))
         
         # Update neighborhood radius and decide whether to continue
         NumCells += 1 
         if NumCells > nLimit:
            arcpy.AddWarning('Neighborhood size limit has been reached for %s.' % UnitID)
            LimitList.append(UnitID)
            arcpy.AddMessage('Assigning a neutral value (1) to all remaining NoAspect cells')
            rdFinalBeers = Con(rdBeers, 1, rdBeers, 'VALUE = -1')
            rdFinalBeers.save(outBeers)
            break
         neighborhood = NbrCircle(NumCells, "CELL")
                  
         # Establish the focal zone
         Grow = int(NumCells)
         FocalZone = Expand (rdNoAspect, Grow, [1]) # NoAspect cells (zone 1) grow outward
         FocalZone.save(scratchGDB + os.sep + 'FocalZone')
         
         # Within focal zone, set values from the original burned Beers raster
         # Outside focal zone, set to NoData to avoid excessive memory usage/processing time
         FocalRaster1 = SetNull (FocalZone, burnBeers, 'VALUE = 0')
         
         # Set -1 values to NoData so they do not contaminate the neighborhood mean
         FocalRaster = SetNull (FocalRaster1, FocalRaster1, 'VALUE = -1')  
         FocalRaster.save(scratchGDB + os.sep + 'FocalRaster')
                  
         # arcpy.AddMessage('Calculating the focal mean')
         MeanRaster1 = FocalStatistics (FocalRaster, neighborhood, 'MEAN', 'DATA')

         # Convert nulls back to -1
         MeanRaster = Con (IsNull(MeanRaster1), -1, MeanRaster1, 'VALUE = 1')
         MeanRaster.save(scratchGDB + os.sep + 'MeanRaster')
         
         # Make a position raster; need to add one because positions are indexed from 1, not 0
         PosRaster = Plus(rdNoAspect, 1)
         PosRaster.save(scratchGDB + os.sep + 'PosRaster')
         
         # Update the Beers Aspect raster, with focal means assigned to NoAspect cells
         rdBeers = Pick (PosRaster, [outBeers, MeanRaster]) 
         rdBeers.save(scratchGDB + os.sep + 'Beers_%s_%s' % (UnitID, str(Grow))) # Keep track of series
         rdBeers.save(outBeers)
         
         # Determine the number of remaining NoAspect cells
         rdNoAspect = Con (rdBeers, 1, 0, 'VALUE = -1')
         rows = arcpy.SearchCursor (rdNoAspect, "Value = 1", "", "Count", "")
         row = rows.next()
         if row:
            NumNulls = row.getValue("Count")
         else:
            NumNulls = 0

      else:
         arcpy.AddMessage('There are no NoAspect cells remaining in the Beers Aspect raster.')
      
   except:
      # Error handling code swiped from "A Python Primer for ArcGIS"
      tb = sys.exc_info()[2]
      tbinfo = traceback.format_tb(tb)[0]
      pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
      msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

      arcpy.AddWarning('Unable to process unit %s' % UnitID)
      FailList.append(UnitID)
      arcpy.AddWarning(msgs)
      arcpy.AddWarning(pymsg)
      arcpy.AddMessage(arcpy.GetMessages(1))
      
# List the units where processing failed
if FailList:
   msg = '\nProcessing failed for some units: \n'
   Log.write(msg)
   arcpy.AddMessage('%s See the processing log, %s' % (msg, ProcLogFile))
   for unit in FailList:
      Log.write('\n   -%s' % unit)
      arcpy.AddMessage(unit) 
      
# List the units where the neighborhood limit caused incomplete processing
if LimitList:
   msg1 = 'The neighborhood size limit was reached for some processing units.'
   msg2 = 'The following units had a neutral value imposed for all remaining NoAspect cells.'
   Log.write('\n' + msg1)
   arcpy.AddMessage(msg1)
   Log.write('\n' + msg2)
   arcpy.AddMessage('%s These are also listed in the processing log, %s' % (msg2, ProcLogFile))
   for unit in LimitList:
      Log.write('\n   -%s' % unit)
      arcpy.AddMessage(unit)  
         
timestamp = datetime.now().strftime(FORMAT)
Log.write("\n\nProcess logging ended %s" % timestamp)   
Log.close()




