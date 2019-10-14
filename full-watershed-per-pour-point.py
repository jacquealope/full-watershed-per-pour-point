##-------------------------------------------------------
## Scripted in 2018 for the Bureau of Water Quality and Planning for the batch deliniation of watersheds individually
##
##  LICENSE:  Feel free to use, share, change this script, it was a lot of work to put together and I know Nevada is not the only  
##  state or people that needs the ability to create an individual watershed for hundreds or thousands of pour points. 
##  No need to give credit as I am sharing this without any restrictions.
##
## PYTHON VERSION PARTICULARS:
## This script was made for Python 2.7.x but a conversion to 3.x should be fairly easy as this was written clean enough to do so. 
## once you try to run it in 3.x and you can fix them as they come up.
##
## My poor description of this script (LOL)... Full outline bewlow this....
## This script will create individual FULL watersheds for as many pour points as you have
## The watershed tool iteslf moved through a raster format so if you ran more than one along a segment of a stream
## they would end up "erased" downstream and you'd end up with weird shaped watersheds like horseshoes rather than the full normal watershed shape.
## This script allows you to get accurate watershed coverage for EACH pour point as well as accurate area calculations
## and you won't have to run each individual pour point seperate. Hope this explination helps..LOL! If not the outline is below.
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##  NOTES!
##
##  NOTE: This script has some hard coded values for Nevada HUC numbers, you can change these easily.  
##  The loops are the only places where they are hard coded at, the "walks" will gather your HUC numbers regardless of what they are, 
##  it puts those values in the list then will look for that value in each loop.
##  Just change the values at the top of the loop and then comment out or copy/paaste each for any additional or less than needed.
##
##  NOTE: the walks are finding raster types of GRID and only those with _fd or _fa endings, which is the 
##  USGS naming convention for the files you need to complete this.
##
##  		_fd = Flow direction
##  		_fa = Flow accumulation
##
##  NOTE: Also the final coordinate system is NAD 83 Z11N so if you need to convert to something else you will need the 
##  coordinate system parameters and the transformation if not from NAD83.
##  These projection variables are at the bottom of the script after the last loop.
##
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------



##---------------------------------------------------------------------------------------------------------------------------
# SCRIPT OUTLINE
	# 1. Gather paths and create variables
	# 2. Check out Spatial Analyst License
	# 3. Set environments
	# 4. Create File Geodatabase for project
	# 5. Set workspace to new File Geodatabase
	# 6. Split pour point shapefile by HUC4 using the USGS polygon
	# 7. Create list variables to hold file paths
	# 8. “Walk” the network paths provided to find the necessary DEMs and Feature Classes we need and store them in lists.
	# 9. Create an empty polygon Feature Class to append all the watersheds to
	# 10. Add a field to store the acreage value
	# 11. Create variable for all the loops to use
	# 12. Loop each HUC4 pour point Feature Class created:
		# a. Create loop specific variables
		# b. Identify HUC4 being run (by variables) and print
		# c. IF this HUC4 has pour points (if not, exit loop)
			# i. Grab a count of number of points in the specified HUC4
			# ii. Find the Flow accumulation DEM, if exists (if not, exit loop)
			# iii. If the FA dem exists, find the Flow Direction DEM, if exists (if not, exit loop)
			# iv. If the FD dem exists, select the first row in that HUC pour point Feature Class
				# 1. Create a point Feature Class out of that single point in the project FGDB
				# 2. Run the Snap Pour Point tool on the new Feature Class to create a PourPoint Raster in the project FGDB
				# 3. Delete the single Pour Point Feature Class it created
				# 4. Run the watershed tool on the Pour Point Raster
				# 5. Save the Watershed Raster in the project FGDB
				# 6. Convert the Watershed to Polygon, saving it in the project FGDB
				# 7. Delete the Raster Watershed
				# 8. Append the poly watershed to empty Feature Class created before the loop
				# 9. Delete the polygon watershed
				# 10. Repeat until all Points done for this HUC4
		# d. Delete the HUC4 point Feature Class the loop just finished with
		# e. Move to the next loop for the next HUC4 until all HUC4’s are completed.
	# 13. Reproject the completed Watershed polygon Feature Class to UTM
	# 14. Calculate acreage
	# 15. Delete the non-UTM watershed
	# 16. Remove the “dangly bits” on the watersheds (anything less than an acre)
	# 17. Reproject the original Pour Point Shapefile for the state to the project FGDB
	# 18. Done!
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
## INSTRUCTIONS
# 1. Close out of everything ESRI (if you had it open, check the Task Manager too!)
# 2. Gather locations for the script:
	# a. Folder directory for your project
	# b. What you want to call your File Geodatabase (FGDB) (no need to create one as it does so here)
	# c. Where the original pour point shapefile is (in the project folder is ideal)
	# d. Where the USGS HUC4 Shapefile is
	# e. The upper directory of the DEM’s (from the USGS)
# 3. Open the IDLE
	# a. Open start menu and type IDLE and it will come up, press enter
# 4. Open the script:
	# a. Name: FINAL_watershed_script.py
	# b. NOTE: Do NOT just double-click on the script, you must open it in the IDLE
		# i. You can also right-click>Edit with IDLE
		# ii.
		# iii. NOTE: Do not use the ArcPro or a version of python that is not 2.7.x, the syntax is a bit different, not too bad so you can edit this to conform to ArcPro in the future.
# 5. Change green text (indicates a string) areas in the script noted by a comment that says “change”, you can use the find tool to flag these
	# a. If wanting to use a Find tool: best to use a program like notepad++, the IDLE one sucks
	# b. Comments start with a #.
			# All the areas to be changed are at the top of script:
			# #change to reflect project folder location
			# projectLocation = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Projects\BIO_PredictiveModelWatershed\2017"
			# #change to reflect project name and year
			# fgdb_name = "WatershedDeliniation2017.gdb"
			# #Change this to reflect your original pourPoints file, I have it here already in my project folder location
			# pourPointsOrig = projectLocation + "\\2017PointData.shp"
			# #change the usgsHUC4 to reflect the HUC4 shapefile or feature class location
			# usgsHUC4 = r"L:/GIS_Bureaus/GIS_BWQP/GIS_Data/WatershedData/HUC4_usgs.shp"
			# #This is the upper folder level of the DEM directory
			# #change the variable here if the DEM location changes
			# demDirectory = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Data\WatershedData\DEMs"
# 6. Once you have changed the file paths, save the script (File>Save OR ctrl+S)
# 7. To run the script: press F5 or under the menu Run> Run Module
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------
##---------------------------------------------------------------------------------------------------------------------------


#Import Modules
import arcpy
import os
import time
print "==================================================================================================================="
print "==================================================================================================================="
print"Script started at " + time.strftime('%A, %d %b %Y %H:%M:%S')
print "==================================================================================================================="
print "==================================================================================================================="

#change to reflect project folder location
projectLocation = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Projects\BIO_PredictiveModelWatershed\2017"
#change to reflect project name and year
fgdb_name = "WatershedDeliniation2017.gdb"

#Change this to reflect your original pourPoints file, I have it here already in my project folder location
pourPointsOrig = projectLocation + "\\2017PointData.shp"

#change the usgsHUC4 to reflect the HUC4 shapefile or feature class location
usgsHUC4 = r"L:/GIS_Bureaus/GIS_BWQP/GIS_Data/WatershedData/HUC4_usgs.shp"

#This is the upper folder level of the DEM directory
#change the variable here if the DEM location changes
demDirectory = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Data\WatershedData\DEMs"

#Checkout Spatial Analyst extension
arcpy.AddMessage("Checking license... ")
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
    arcpy.AddMessage("Spatial Analyst license checked out... ")
    print "Got a Spatial Analyst License!"
else:
    arcpy.AddMessage("Spatial Analyst license needed... ")
    raise LicenseError

#Set environments
arcpy.env.overwriteOutput = True
arcpy.env.XYResolution = "0.00001 Meters"
arcpy.env.XYTolerance = "0.0001 Meters"

#Creates File GDB for the watersheds
arcpy.CreateFileGDB_management(projectLocation, fgdb_name)
print "created File Geodatabase"
arcpy.env.workspace = projectLocation + "\\" + fgdb_name
wrkSpace = projectLocation + "\\" + fgdb_name
print "set wrkSpace Variable to newly created File Geodatabase"

#create individual pour point feature classes by the HUC4 value
arcpy.Split_analysis(pourPointsOrig, usgsHUC4, "HUC4", wrkSpace, "")

#---------------------------------------------------------------------------------------------------------------------#
#"walking" through the project locations specified at the top of the script to find the files we need for the script and then placing them in a list we can pull from
#If you are getting a lot of files "not found" when there should be, un-comment out (remove #) the print line at the bottom of each walk (ex: print "flow direction list is " + str(flowDirList))
#un-commenting out that line will show you the contents of the list, if it prints: flow direction list is [] and there is nothing in the brackets, perhaps a file name was not correct or the path was wrong

#this is just a placeholder for this variable
flowDirList = []
flowDir = r""

#This "walk" finds the FLOW DIRECTION DEM that we need
#I have the DEM directory at the top level and it will search through the sub folders.
walk = arcpy.da.Walk(demDirectory, type="GRID")
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        #Change the filename variable in quotes below
        if filename.endswith("_fd"):
            flowDir = dirpath + "\\" + filename
            flowDirList.append(flowDir)
flowDirList.sort()
#print "flow direction list is " + str(flowDirList)
print "flow direction raster list created"

#this is just a placeholder for this variable
flowAcList = []
flowAc = r""
#This "walk" finds the FLOW ACCUMULATION DEM that we need
#I have the DEM directory at the top level and it will search through the sub folders.
walk = arcpy.da.Walk(demDirectory, type="GRID")
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        #Change the filename variable in quotes below
        if filename.endswith("_fa"):
            flowAc = dirpath + "\\" + filename
            flowAcList.append(flowAc)
flowAcList.sort()
#print "flow accumulation list is " + str(flowAcList)
print "flow accumulation raster list created"

pourPointFCList = []
featureClass = ""

#This "walk" finds the pour point feature classes that we just made using the split tool and creates a list to store them
walk = arcpy.da.Walk(wrkSpace, type="POINT")
for dirpath, dirnames, filenames in walk:
    for filename in filenames:
        if filename.startswith('r'):
            featureClass = dirpath + "\\" + filename
            pourPointFCList.append(featureClass)
pourPointFCList.sort()
print "pour point FC list created"
#print "my pour point list by HUC4 is "+ str(pourPointFCList)

#---------------------------------------------------------------------------------------------------------------------#
#create empty feature class for the final merging of watersheds

outName = "AllWatersheds"
schemaType = "NO_TEST"
fieldMappings = ""
subtype = ""

print "Creating Feature Class to merge all watersheds into..."
# the FC (templateFC) called out in this tool is a template FC to use for the new one that will have all the necessary fields we need
#Not sure why everything is in NAD83 Albers but it is so I am making the final merged FC Albers as well.Since it is NAD83, a transformation is not needed to reproject to UTM
templateFC = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Projects\BIO_PredictiveModelWatershed\PythonScripts\PythonTemplateFCs.gdb\TemplateWatershed"
spatial_reference_ALBERS = "PROJCS['NAD_1983_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',29.5],PARAMETER['Standard_Parallel_2',45.5],PARAMETER['Latitude_Of_Origin',23.0],UNIT['Meter',1.0]];-16901100 -6972200 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
arcpy.CreateFeatureclass_management(wrkSpace, outName, "POLYGON", templateFC, "DISABLED", "DISABLED", spatial_reference_ALBERS, config_keyword="", spatial_grid_1="0", spatial_grid_2="0", spatial_grid_3="0")
print "Feature class " + outName + " created"
emptyFC = wrkSpace + "\\" + outName
print "New Feature Class is " + emptyFC

fieldName = "DA_acresUS"

#adds acres column into new FC
arcpy.AddField_management (emptyFC, fieldName, "DOUBLE")

#---------------------------------------------------------------------------------------------------------------------#
#loop time!
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print "LOOP TIME! YEAH!  This may take a long while.... be patient"
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"

#loop variables
pourPointPoly = ""
pourPointRaster = ""
pointSelection = ""

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1501")
demFA = demDirectory + str("\\r1501\\r1501_fa")
demFD = demDirectory + str("\\r1501\\r1501_fd")
pourPointPolyOutput = wrkSpace + "\\p1501"

#loop for HUC4 1501
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1501 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1501..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1501, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1501!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1501_fD not found"
    else:
        print "Flow Accumulation DEM r1501_fa not found"
        
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1501"
    
else:
    print "1501 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1501 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"


#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1503")
demFA = demDirectory + str("\\r1503\\r1503_fa")
demFD = demDirectory + str("\\r1503\\r1503_fd")
pourPointPolyOutput = wrkSpace + "\\p1503"

#loop for HUC4 1503
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1503 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1503..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1503, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1503!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1503_fD not found"
    else:
        print "Flow Accumulation DEM r1503_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1503"
    
else:
    print "1503 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1503 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1601")
demFA = demDirectory + str("\\r1601\\r1601_fa")
demFD = demDirectory + str("\\r1601\\r1601_fd")
pourPointPolyOutput = wrkSpace + "\\p1601"

#loop for HUC4 1601
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1601 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1601..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1601, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1601!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1601_fD not found"
    else:
        print "Flow Accumulation DEM r1601_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1601"
    
else:
    print "1601 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1601 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1602")
demFA = demDirectory + str("\\r1602\\r1602_fa")
demFD = demDirectory + str("\\r1602\\r1602_fd")
pourPointPolyOutput = wrkSpace + "\\p1602"

#loop for HUC4 1602
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1602 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1602..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1602, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1602!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1602_fD not found"
    else:
        print "Flow Accumulation DEM r1602_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1602"
    
else:
    print "1602 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1602 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1603")
demFA = demDirectory + str("\\r1603\\r1603_fa")
demFD = demDirectory + str("\\r1603\\r1603_fd")
pourPointPolyOutput = wrkSpace + "\\p1603"

#loop for HUC4 1603
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1603 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1603..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1603, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------ready for the next row in 1603!------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1603_fD not found"
    else:
        print "Flow Accumulation DEM r1603_fa not found"

    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1603"
    
else:
    print "1603 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1603 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1604")
demFA = demDirectory + str("\\r1604\\r1604_fa")
demFD = demDirectory + str("\\r1604\\r1604_fd")
pourPointPolyOutput = wrkSpace + "\\p1604"

#loop for HUC4 1604
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1604 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1604..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1604, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1604!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1604_fD not found"
    else:
        print "Flow Accumulation DEM r1604_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1604"
    
else:
    print "1604 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1604 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1605")
demFA = demDirectory + str("\\r1605\\r1605_fa")
demFD = demDirectory + str("\\r1605\\r1605_fd")
pourPointPolyOutput = wrkSpace + "\\p1605"

#loop for HUC4 1605
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1605 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1605..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1605, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1605!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1605_fD not found"
    else:
        print "Flow Accumulation DEM r1605_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1605"
    
else:
    print "1605 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1605 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1606a")
demFA = demDirectory + str("\\r1606a\\r1606a_fa")
demFD = demDirectory + str("\\r1606a\\r1606a_fd")
pourPointPolyOutput = wrkSpace + "\\p1606a"

#loop for HUC4 1606a
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1606a started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1606a..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1606a, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1606a!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1606a_fD not found"
    else:
        print "Flow Accumulation DEM r1606a_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1606a"
    
else:
    print "1606a pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1606a at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1606b")
demFA = demDirectory + str("\\r1606b\\r1606b_fa")
demFD = demDirectory + str("\\r1606b\\r1606b_fd")
pourPointPolyOutput = wrkSpace + "\\p1606b"

#loop for HUC4 1606b
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1606b started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1606b..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1606b, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1606b!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1606b_fD not found"
    else:
        print "Flow Accumulation DEM r1606b_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1606b"
    
else:
    print "1606b pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1606b at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1704")
demFA = demDirectory + str("\\r1704\\r1704_fa")
demFD = demDirectory + str("\\r1704\\r1704_fd")
pourPointPolyOutput = wrkSpace + "\\p1704"

#loop for HUC4 1704
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1704 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1704..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1704, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1704!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1704_fD not found"
    else:
        print "Flow Accumulation DEM r1704_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1704"
    
else:
    print "1704 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1704 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1705")
demFA = demDirectory + str("\\r1705\\r1705_fa")
demFD = demDirectory + str("\\r1705\\r1705_fd")
pourPointPolyOutput = wrkSpace + "\\p1705"

#loop for HUC4 1705
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1705 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1705..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1705, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1705!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1705_fD not found"
    else:
        print "Flow Accumulation DEM r1705_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1705"
    
else:
    print "1705 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1705 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1712")
demFA = demDirectory + str("\\r1712\\r1712_fa")
demFD = demDirectory + str("\\r1712\\r1712_fd")
pourPointPolyOutput = wrkSpace + "\\p1712"

#loop for HUC4 1712
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1712 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1712..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1712, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1712!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1712_fD not found"
    else:
        print "Flow Accumulation DEM r1712_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1712"
    
else:
    print "1712 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1712 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1808")
demFA = demDirectory + str("\\r1808\\r1808_fa")
demFD = demDirectory + str("\\r1808\\r1808_fd")
pourPointPolyOutput = wrkSpace + "\\p1808"

#loop for HUC4 1808
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1808 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1808..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1808, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1808!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1808_fD not found"
    else:
        print "Flow Accumulation DEM r1808_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1808"
    
else:
    print "1808 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1808 at " + time.strftime('%A, %d %b %Y %H:%M:%S') + ", moving onto the next one!"

#---------------------------------------------------------------------------------------------------------------------#

#these variables will be repeated before each HUC4 loop
item = wrkSpace + str("\\r1809")
demFA = demDirectory + str("\\r1809\\r1809_fa")
demFD = demDirectory + str("\\r1809\\r1809_fd")
pourPointPolyOutput = wrkSpace + "\\p1809"

#loop for HUC4 1809
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print"HUC4 1809 started " + time.strftime('%A, %d %b %Y %H:%M:%S')
if item in pourPointFCList:
    print "pour point feature class list contains HUC 1809..."+ str(item)
    countPourPount = arcpy.GetCount_management(item)
    print "-------------------------------------------------------------"
    print "In HUC4 1809, there are " + countPourPount.getOutput(0) + " number of points"
    print "-------------------------------------------------------------"
    updateRows = arcpy.da.UpdateCursor(item, ["OBJECTID_1"])
    if demFA in flowAcList:
        print "Flow Accumulation DEM found..." + str(demFA)
        if demFD in flowDirList:
            print "Flow Direction DEM found..." + str(demFD)
            for row in updateRows:
                #SQL condition variable where it loops for every FID in the dataset
                where_clause = "OBJECTID_1 = {0}".format(row[0])
                #the feature class name variable for the output
                out_feature_class = wrkSpace + "\\ws" + str(row[0])

                #Use select by condition to create individual feature class for each pour point row for this HUC
                pointSelection = arcpy.Select_analysis(item, out_feature_class, where_clause)
                print "feature class created for..." + str(pointSelection)

                #create the pour point raster
                pourPointRasterOutput = projectLocation + "\\ppr" + str(row[0])
                pourPointRaster = arcpy.gp.SnapPourPoint_sa(pointSelection, demFA, pourPointRasterOutput, "60", "OBJECTID_1")
                print "Snap Pour Point tool run for HUC4 points..." + str(pourPointRaster)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pointSelection)
                print "pour point feature class deleted..." + str(pointSelection)
                
                #Use watershed method in spatial analyst to create watershed delineation for each pour point, then save as raster
                watershed = arcpy.sa.Watershed(demFD, pourPointRaster, "VALUE")
                watershed.save(projectLocation + "\\ws" + str(row[0]))
                print "watershed created..." + str(watershed)

                #Delete pour point feature class as it's no longer needed
                arcpy.Delete_management(pourPointRaster)
                print "pour point raster deleted..." + str(pourPointRaster)
  
                #Convert the raster of the watershed into a polygon of the watershed
                wsPoly = arcpy.RasterToPolygon_conversion(watershed, wrkSpace + "\\ws" + str(row[0]), "SIMPLIFY", "VALUE")
                print "converted raster watershed to polygon"

                #Delete the raster watershed file as it's no longer needed
                arcpy.Delete_management(watershed)
                print "deleted raster watershed..." + str(watershed)

                #Add a drainage area field to calculate drainage area
                arcpy.AddField_management (wsPoly, "DA_acresUS", "DOUBLE")

                #Calculate drainage area
                arcpy.CalculateField_management(wsPoly, "DA_acresUS", "!SHAPE.AREA@ACRES!", "PYTHON", "")
                print "calculated acres"

                #merge all 1604 HUC watersheds
                arcpy.Append_management(wsPoly, emptyFC, schemaType, fieldMappings, subtype)
                print "appended..." + str(wsPoly)
      
                #deleting the Albers FC
                arcpy.Delete_management(wsPoly)
                print "Deleted the watershed FC " + str(wsPoly)
            
                updateRows.updateRow(row)
                print "------------------------ready for the next row in 1809!------------------------"
                
            del updateRows
            del row
            
        else:
            print "Flow Direction DEM r1809_fD not found"
    else:
        print "Flow Accumulation DEM r1809_fa not found"
            
    #deleting the split pour point feature class because we don't need it anymore
    arcpy.Delete_management(item)
    print "Deleted the split pour point Feature Class for 1809"
    
else:
    print "1809 pour point not found"
    print "...only be worried if you know you have points here..."
print "done with 1809 at " + time.strftime('%A, %d %b %Y %H:%M:%S')

print "-------------------------------------------------------------"
print "-------------------------------------------------------------"
print "This was the last HUC4, cleaning up and reprojecting next..."
print "-------------------------------------------------------------"
print "-------------------------------------------------------------"

#---------------------------------------------------------------------------------------------------------------------#

#Reprojecting the merged FC to UTM
print "reprojecting the feature classes to UTM"
spatialRef = arcpy.SpatialReference('NAD 1983 UTM Zone 11N')
albersFC = emptyFC
utmFC = emptyFC + "_UTM"

#reprojecting to UTM
arcpy.Project_management(albersFC, utmFC, spatialRef)
print "reprojected Albers watershed to UTM"

#Calculate drainage area
arcpy.CalculateField_management(utmFC, "DA_acresUS", "!SHAPE.AREA@ACRES!", "PYTHON", "")
print "calculated acres"

#deleting the Albers FC
arcpy.Delete_management(albersFC)
print "Deleted the Albers watershed FC"

#removing all the dangly bits on the watersheds
print "deleting dangly bits on watersheds...."

with arcpy.da.UpdateCursor(utmFC, fieldName) as cursor:
    for row in cursor:
        if row[0]<1:
            cursor.deleteRow()
            
print "deleted dangly bits!  Now your watersheds are soooo pretty!"

#Reprojecting the orig pour point shapefile to UTM
print "reprojecting the orig pour point shapefile to UTM"
albersFC = pourPointsOrig
utmFC = wrkSpace + "\\PourPoints_UTM"

#reprojecting to UTM
arcpy.Project_management(albersFC, utmFC, spatialRef)
print "reprojected Albers pour point to UTM"
print "The pour points are now in the" + fgdb_name +" File Geodatabase"

#done!
print "==================================================================================================================="
print "==================================================================================================================="
print "Done! Completed at " + time.strftime('%A, %d %b %Y %H:%M:%S') + " Now get back to work!!!"
print "==================================================================================================================="
print "==================================================================================================================="