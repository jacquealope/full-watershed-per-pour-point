# full-watershed-per-pour-point
Python to create a full and complete watershed for every pour point you have based on the USGS flow raster data per HUC. 
Script loops through a pour point at a time to create a watershed and at the end will add the polygon watershed to a 
Feature Class in a File Geodatabase.

Made in 2018 for the Nevada Bureau of Water Quality and Planning for the batch deliniation of watersheds individually

LICENSE:  Feel free to use, share, change this script, it was a lot of work and I know Nevada is not the only 
state or people that needs the ability to create an individual watershed for hundreds or thousands of pour points. 
No need to give credit as I am sharing this without any restrictions.

This script was made for Python 2.7.x but a conversion to 3.x should be fairly easy as this was written clean enough to do so. 
I found the print functions usually is the only thing I change in most scripts but anything not compatible will be 
flagged once you try to run it in 3.x and you can fix them as they come up.

My poor description of this script (LOL)...  Full outline of the script below that has better details...
This script will create individual FULL watersheds for as many pour points as you have The watershed tool in
ArcGIS iteslf moved through a raster format so if you ran more than one along a segment of a stream they would end up 
"erased" downstream and you'd end up with weird shaped watersheds. This script allows you to get accurate watershed 
coverage for EACH pour point as well as accurate area calculations and you won't have to run each individual pour 
point seperate. Hope this explination helps..LOL! If not the outline is below.


---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------

NOTES!!!!

NOTE: This script has some hard coded values for Nevada HUC numbers, you can change these easily.  
The top of each of the loops are the only places where they are hard coded at, the "walks" will gather your 
HUC numbers regardless of what they are, it puts those values in the list then will look for that value hard coded in each loop.  
Just change the values at the top of the loop and then comment out or copy/paaste each for any additional or less than needed.

NOTE: the "walks" are finding raster types of GRID and only those with _fd or _fa endings, which is the 
USGS naming convention for the files you need to complete this.

  _fd = Flow direction
  
  _fa = Flow accumulation

NOTE: the final coordinate system is NAD 83 UTM Z11N so if you need to convert to something else you will need the 
coordinate system parameters and the transformation if not from NAD83. These projection variables are at the bottom 
of the script after the last loop.

---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------

 SCRIPT OUTLINE
 
1. Gather paths and create variables

2. Check out Spatial Analyst License

3. Set environments

4. Create File Geodatabase for project

5. Set workspace to new File Geodatabase

6. Split pour point shapefile by HUC4 using the USGS polygon

7. Create list variables to hold file paths

8. “Walk” the network paths provided to find the necessary DEMs and Feature Classes we need and store them in lists.

9. Create an empty polygon Feature Class to append all the watersheds to

10. Add a field to store the acreage value

11. Create variable for all the loops to use

12. Loop each HUC4 pour point Feature Class created:

    a. Create loop specific variables
  
    b. Identify HUC4 being run (by variables) and print
  
    c. IF this HUC4 has pour points (if not, exit loop)
  
      i. Grab a count of number of points in the specified HUC4
   
      ii. Find the Flow accumulation DEM, if exists (if not, exit loop)
   
      iii. If the FA dem exists, find the Flow Direction DEM, if exists (if not, exit loop)
   
      iii. If the FA dem exists, find the Flow Direction DEM, if exists (if not, exit loop)

      iv. If the FD dem exists, select the first row in that HUC pour point Feature Class
   
    1. Create a point Feature Class out of that single point in the project FGDB
    
    2. Run the Snap Pour Point tool on the new Feature Class to create a PourPoint Raster in the project FGDB
    
    3. Delete the single Pour Point Feature Class it created
    
    4. Run the watershed tool on the Pour Point Raster
    
    5. Save the Watershed Raster in the project FGDB
    
    6. Convert the Watershed to Polygon, saving it in the project FGDB
    
    7. Delete the Raster Watershed
    
    8. Append the poly watershed to empty Feature Class created before the loop
    
    9. Delete the polygon watershed
    
    10. Repeat until all Points done for this HUC4
    
   d. Delete the HUC4 point Feature Class the loop just finished with
   
   e. Move to the next loop for the next HUC4 until all HUC4’s are completed.
   
13. Reproject the completed Watershed polygon Feature Class to UTM

14. Calculate acreage

15. Delete the non-UTM watershed

16. Remove the “dangly bits” on the watersheds (anything less than an acre)

17. Reproject the original Pour Point Shapefile for the state to the project FGDB

18. Done!

---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------


 INSTRUCTIONS
 
1. Close out of everything ESRI (if you had it open, check the Task Manager too!)

2. Gather locations for the script:

	a. Folder directory for your project
  
	b. What you want to call your File Geodatabase (FGDB) (no need to create one as it does so here)
  
	c. Where the original pour point shapefile is (in the project folder is ideal)
  
	d. Where the USGS HUC4 Shapefile is
  
	e. The upper directory of the DEM’s (from the USGS)
  
3. Open the IDLE

	a. Open start menu and type IDLE and it will come up, press enter
  
 4. Open the script:
 
	a. Name: FINAL_watershed_script.py
  
	b. NOTE: Do NOT just double-click on the script, you must open it in the IDLE
  
		i. You can also right-click>Edit with IDLE
    
    ii. NOTE: Do not use the ArcPro or a version of python that is not 2.7.x, the syntax is a bit different, not too bad so you can edit this to conform to ArcPro in the future.

5. Change green text (indicates a string) areas in the script noted by a comment that says “change”, you can use the find tool to flag these

    a. If wanting to use a Find tool: best to use a program like notepad++, the IDLE one is not the best
    
	b. Comments start with a #
  
			 All the areas to be changed are at the top of script:
       
			 change to reflect project folder location
       
			 projectLocation = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Projects\BIO_PredictiveModelWatershed\2017"
       
			 change to reflect project name and year
       
			 fgdb_name = "WatershedDeliniation2017.gdb"
       
			 Change this to reflect your original pourPoints file, I have it here already in my project folder location
       
			 pourPointsOrig = projectLocation + "\\2017PointData.shp"
       
			 change the usgsHUC4 to reflect the HUC4 shapefile or feature class location
       
			 usgsHUC4 = r"L:/GIS_Bureaus/GIS_BWQP/GIS_Data/WatershedData/HUC4_usgs.shp"
       
			 This is the upper folder level of the DEM directory
       
			 change the variable here if the DEM location changes
       
			 demDirectory = r"L:\GIS_Bureaus\GIS_BWQP\GIS_Data\WatershedData\DEMs"
       
6. Once you have changed the file paths, save the script (File>Save OR ctrl+S)

7. To run the script: press F5 or under the menu Run> Run Module

---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
