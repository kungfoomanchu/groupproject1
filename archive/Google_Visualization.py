#!/usr/bin/env python
# coding: utf-8

# # Google Map Visualization

# In[39]:


# Dependencies
from census import Census
from config import (census_api_key, gkey)
import gmaps
import numpy as np
import pandas as pd
import requests
import time
from us import states
from ipywidgets.embed import embed_minimal_html

# Census API Key
c = Census(census_api_key, year=2013)

# Configure gmaps with API key
gmaps.configure(api_key=gkey)


# In[44]:


just_cities_merged = pd.read_csv("output/just_cities_merged.csv", encoding="ISO-8859-1")
# merged_wc5_csv_for_google_df = merged_wc5_csv_for_google_df.loc[:, ["StateDesc","CityName","PopulationCount","GeoLocation","Poverty Rate","CityFIPS"]]
# merged_wc5_csv_for_google_df = merged_wc5_csv_for_google_df.drop_duplicates()
# merged_wc5_csv_for_google_df.count()
# merged_wc5_csv_for_google_df.to_csv("output/google_data_df.csv")
just_cities_merged.count()


# In[45]:


google_df = []
google_df = pd.DataFrame()
google_df["lat"] = ""
google_df["long"] = ""
google_df["CityFIPS"] = ""

lat_series = []
long_series = []

for index, row in just_cities_merged.iterrows():
    latlong = str(row["GeoLocation"])
    try:
        # (33.5275663773, -86.7988174678)
        lat = latlong.split(", ")[0]
        long = latlong.split(", ")[1]
        lat = lat.replace("(","")
        long = long.replace(")","")
        google_df.loc[index, "lat"] = lat
        google_df.loc[index, "long"] = long
        google_df.loc[index, "CityFIPS"] = row["CityFIPS"]
#         print(f"{lat} and {long}")

    except Exception as e:
        print(f"{index} This skipped")
google_df.count()


# In[46]:


# Get google_df to have the right number of rows
google_df = google_df.drop_duplicates(subset = ["CityFIPS"])
google_df.count()

# Get merged_wc5_csv_for_google_df to have the right number of rows


# In[49]:


# Store 'Lat' and 'Lng' into  locations 
# locations = census_data_complete[["Lat", "Lng"]].astype(float)
locations = google_df[["lat","long"]].astype(float)

print(locations.count())

# Convert Poverty Rate to float and store
# HINT: be sure to handle NaN values
poverty_rate = just_cities_merged["Poverty Rate"].astype(float)
poverty_rate.count()


# In[50]:


# Create a poverty Heatmap layer
fig = gmaps.figure()

heat_layer = gmaps.heatmap_layer(locations, weights=poverty_rate, 
                                 dissipating=False, max_intensity=100,
                                 point_radius = 1)

# Adjust heat_layer setting to help with heatmap dissipating on zoom
heat_layer.dissipating = False
heat_layer.max_intensity = 100
heat_layer.point_radius = 1

fig.add_layer(heat_layer)

fig


# In[52]:


embed_minimal_html('output/exportmap.html', views=[fig])

