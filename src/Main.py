#General Note: The commented out sections below are an optional path to clean the original large data files
#The code as it currently stands loads a pre-cleaned version that isn't as large.

import pandas as pd
import geopandas as gpd
import os
import numpy as np
import matplotlib.pyplot as plt
import shapely
import os
import sys

#loads functions from the modules directory
sys.path.append('modules')
from clean_pcts import clean_pcts
from dist_decay import dist_decay

#load the opportunity sites
OppSites = gpd.read_file('data/OpportunitySites2/OpportunitySites2.shp')

# #PGParcels and Demogs are not loaded here and are commented out in several operations below, because they are
# #loaded later on in their smaller and pre-cleaned versions. 
# PgParcels = gpd.read_file('data/Property_Info_Py (1)/Property_Info_Py.shp')
# Demogs = gpd.read_file('data/PG_Blocks/PG_Blocks.shp')

#Select the opportunity sites that have a 3 mile radius completely withing Prince George's County
#and a small sliver of DC
OppSites = OppSites[OppSites['DissolveID'].isin([11,31,188,])]

#Convert all geodataframes to UTM-18 for distance measurement
# PgParcels = PgParcels.to_crs(epsg = 32618)
OppSites = OppSites.to_crs(epsg = 32618)
# Demogs = Demogs.to_crs(epsg = 32618)

#Create a buffer around each site of approximately three miles (4828 meters) to represent the market area
OppSitesBuffer = OppSites['geometry'].buffer(4828)

#Copy the Opportunity Sites layer so that it can be replaced with the buffer geometry
OppSitesWithBuffer = OppSites.copy()

#Replace original geometry with buffer geometry
OppSitesWithBuffer['geometry'] = OppSitesBuffer

#plot the buffers with the opportunity sites
ax = OppSitesBuffer.plot()
OppSites.plot(ax=ax, color = 'red')

# #Create a single shape to represent the maximum area of interest (3 miles from the three sites)
# #This was used to create the smaller files that are loaded below.
# MaxArea = OppSitesBuffer.unary_union
# #Convert this polygon object to a geodataframe
# MaxArea_series = gpd.GeoSeries(MaxArea)
# MaxAreaGDF = gpd.GeoDataFrame(geometry = MaxArea_series, crs = 32618)

# #Creates the smaller versions of the files by joining them with the buffer union shape
# PgParcelsSmall = gpd.sjoin(PgParcels, MaxAreaGDF,how="inner", op='intersects')
# DemogsSmall = gpd.sjoin(Demogs, MaxAreaGDF,how="inner", op='intersects')

#Load PgParcelsSmall from file (rather than performing the above process)
PgParcelsSmall = gpd.read_file('data/PgParcelsSmall3Miles/PgParcelsSmall3Mile.shp')

#Load DemogsSmall from file (rather than performing the above process)
DemogsSmall = gpd.read_file('data/DemogsSmall3Miles/DemogsSmall3Mile.shp')

#Remove all columns except the one containing the Geoid, total pop, hispanic pop, and hispanic percent
DemogsSmall = DemogsSmall[['GEOID','P0010001','P0020002','PCT_P00200','geometry']]

#Rename columns for ease of use
DemogsSmall.rename(columns={'P0010001': 'Total_Pop', 'P0020002': 'Hisp_Pop', 'PCT_P00200': 'Hisp_Pct'}, inplace=True)

#Get rid of index_right column in PgParcelsSmall which causes an error in a future join
PgParcelsSmall.drop('index_righ', axis=1, inplace=True)

#JoinPgParcelsSmall with demographic data
ParcelDemogs = gpd.sjoin(PgParcelsSmall,DemogsSmall,how="inner", op = "intersects")

# Group by the parcel account number so that there is one record per parcel
ParcelDemogsCln = ParcelDemogs[['ACCT_PRIMA','DUS','GEOID','Total_Pop','Hisp_Pop','Hisp_Pct','geometry']].groupby('ACCT_PRIMA').first()

#Running the CleanPcts function to remove nulls and make the percent Hispanic data into decimals
clean_pcts(ParcelDemogsCln)

#Running the dist_decay function with quadratic decline to calculate the expected customers
dist_decay(OppSites,ParcelDemogsCln,2)

#creating a percent column to show the percent Hispanic of the expected customers
OppSites['PctHisp'] = (OppSites['HispCustomers'] / OppSites['Customers'])

#checking the results
OppSites.head()

# # Optionally, exporting the results to csv
# OppSites.to_csv('/content/drive/MyDrive/Colab Notebooks/FinalProject/Results/May10Exponential2.csv')
