#!/usr/bin/env python
# coding: utf-8

# In[49]:


#Dependencies
import pandas as pd
import csv
import matplotlib
import seaborn
import os
import numpy as np
import time
import json
from config import wolf_api_key
from pprint import pprint
import requests


# In[50]:


#import csv into dataframe and preview
cities_df = pd.read_csv("500_Cities_original.csv", encoding="ISO-8859-1")


# In[51]:


#Keep only city-level rows
cities_df = cities_df.loc[cities_df["GeographicLevel"] == "City"]


# In[52]:


#keep only age-adjusted data values
#Keep only city-level rows
cities_df = cities_df.loc[cities_df["DataValueTypeID"] == "AgeAdjPrv"]
cities_df.head()


# In[53]:


#trim down columns
cities_cleaned_df = cities_df.loc[:, ["Year", "StateDesc", "CityName",
                                    "Category", "Measure", "DataValueTypeID", "Data_Value", "PopulationCount",
                                      "Count_of_Individuals", "GeoLocation", "MeasureId", "CityFIPS",
                                      "Short_Question_Text"]]
cities_cleaned_df.head(3)


# # Make a smaller "Just Cities" DataFrame

# In[228]:


just_cities = cities_df.loc[:, ["StateDesc","CityName","PopulationCount","GeoLocation","CityFIPS"]]
just_cities = just_cities.drop_duplicates()

# Make a small dataframe to play around with
just_cities_head = just_cities.head(3)
just_cities.head()


# # Add Weather
# # Don't rerun this

# In[169]:


# Get Weather Loop

# Build partial query URL
url = "https://api.wolframalpha.com/v2/query?format=plaintext&output=JSON&input="


print("Beginning Data Retrieval")
print("------------------------")

row_count = 1

# Make Weather DataFrame
weather_df = []
weather_df = pd.DataFrame()
weather_df["Average Temperature"] = ""
weather_df["Historic Low Temp"] = ""
weather_df["Average High Temp"] = ""
weather_df["Average Low Temp"] = ""
weather_df["Historic High Temp"] = ""

# Make Weather_Unfound DataFrame
weather_unfound_df = []
weather_unfound_df = pd.DataFrame()
weather_unfound_df["State"] = ""
weather_unfound_df["City"] = ""
weather_unfound_df["CityFIPS"] = ""

for index, row in just_cities.iterrows():
    city_query = row['CityName']
    state_query = row['StateDesc']
    if state_query == "South Carolin":
        state_query = "South Carolina"
    if state_query == "North Carolin":
        state_query = "North Carolina"
    if state_query == "District of C":
        state_query = "District of Columbia"
    print(f"This is the city query {city_query}, {state_query}")
    try:

        ten_year_query = "average+temperature+for+" + city_query.replace(" ","+") + ",+" + state_query.replace(" ","+") + "+past+ten+years"

        # Build query URL
        query_url = url + ten_year_query + "&appid=" + wolf_api_key

        # Get Response
        response = requests.get(query_url).json()

        # Obtain, then Append Overall Average Temp
        avg_temp = response["queryresult"]["pods"][1]["subpods"][0]["plaintext"]
        avg_temp_clean = int(avg_temp.split(" °F")[0])
        weather_df.loc[index, "Average Temperature"] = avg_temp_clean

        # Get Temp String (used for all other variables below)
        temp_string = response["queryresult"]["pods"][2]["subpods"][0]["plaintext"]

        # Historic Low Temp
        temp_low = temp_string.split(" | ")[2]
        temp_low = temp_low.split("low: ")[1]
        weather_df.loc[index, "Historic Low Temp"] = int(temp_low.split(" °F")[0])

        # Average High Temp
        temp_avghigh = temp_string.split(" | ")[4]
        weather_df.loc[index, "Average High Temp"] = int(temp_avghigh.split(" °F")[0])

        # Average Low Temp
        temp_avglow = temp_string.split(" | ")[5]
        weather_df.loc[index, "Average Low Temp"] = int(temp_avglow.split(" °F")[0])

        # Historic High Temp
        temp_high = temp_string.split(" | ")[6]
        temp_high = temp_high.split("high: ")[1]
        weather_df.loc[index, "Historic High Temp"] = int(temp_high.split(" °F")[0])

        # Add Place Holders
        weather_df.loc[index, "State"] = state_query
        weather_df.loc[index, "City"] = city_query
        weather_df.loc[index, "CityFIPS"] = row['CityFIPS']

#         # Temperature Range
#         average_temp_range_list.append(temp_avghigh - temp_avglow)

        print(f"Processing Record {row_count} of Set 1 | {city_query}, {state_query}")
        row_count += 1

    except Exception as e:
        # TODO Exception Handling needs to be Improved
        print(f"{city_query} not found")
        weather_unfound_df.loc[index, "State"] = state_query
        weather_unfound_df.loc[index, "City"] = city_query
        weather_unfound_df.loc[index, "CityFIPS"] = row['CityFIPS']
        row_count += 1

weather_unfound_df.count()


# In[ ]:


weather_df.to_csv("output/weather_df.csv")
weather_unfound_df.to_csv("output/weather_unfound_df.csv")


# # Run Weather loop again on weather_unfound_df

# In[229]:


weather_unfound_df.head()


# # Process weather_unfound_df

# In[245]:


#import csv into dataframe and preview
weather_unfound_df = pd.read_csv("output/weather_unfound_df.csv", encoding="ISO-8859-1")
#wc5_df.head()

# Make copy of weather unfound
weather_unfound_rerun_df = weather_unfound_df

# Add columns ot weather_unfound_rerun_df
weather_unfound_rerun_df["Average Temperature"] = ""
weather_unfound_rerun_df["Historic Low Temp"] = ""
weather_unfound_rerun_df["Average High Temp"] = ""
weather_unfound_rerun_df["Average Low Temp"] = ""
weather_unfound_rerun_df["Historic High Temp"] = ""

weather_unfound_rerun_df.head(30)


# In[246]:


# Get Weather Loop

# Build partial query URL
url = "https://api.wolframalpha.com/v2/query?format=plaintext&output=JSON&input="


print("Beginning Data Retrieval")
print("------------------------")

row_count = 1



# Make Weather_Unfound2 DataFrame
weather_unfound_df2 = []
weather_unfound_df2 = pd.DataFrame()
weather_unfound_df2["State"] = ""
weather_unfound_df2["City"] = ""
weather_unfound_df2["CityFIPS"] = ""

for index, row in weather_unfound_rerun_df.iterrows():
    city_query = row['City']
    state_query = row['State']
    if state_query == "South Carolin":
        state_query = "South Carolina"
    if state_query == "North Carolin":
        state_query = "North Carolina"
    if state_query == "District of C":
        state_query = "District of Columbia"
    print(f"This is the city query {city_query}, {state_query}")
    try:
        
        ten_year_query = "average+temperature+for+" + city_query.replace(" ","+") + ",+" + state_query.replace(" ","+") + "+past+ten+years"

        # Build query URL
        query_url = url + ten_year_query + "&appid=" + wolf_api_key
                       
        # Get Response
        response = requests.get(query_url).json()
                       
        # Obtain, then Append Overall Average Temp
        avg_temp = response["queryresult"]["pods"][1]["subpods"][0]["plaintext"]
        avg_temp_clean = int(avg_temp.split(" °F")[0])
        weather_unfound_rerun_df.loc[index, "Average Temperature"] = avg_temp_clean

        # Get Temp String (used for all other variables below)
        temp_string = response["queryresult"]["pods"][2]["subpods"][0]["plaintext"]
        
        # Historic Low Temp
        temp_low = temp_string.split(" | ")[2]
        temp_low = temp_low.split("low: ")[1]
        weather_unfound_rerun_df.loc[index, "Historic Low Temp"] = int(temp_low.split(" °F")[0])

        # Average High Temp
        temp_avghigh = temp_string.split(" | ")[4]
        weather_unfound_rerun_df.loc[index, "Average High Temp"] = int(temp_avghigh.split(" °F")[0])

        # Average Low Temp
        temp_avglow = temp_string.split(" | ")[5]
        weather_unfound_rerun_df.loc[index, "Average Low Temp"] = int(temp_avglow.split(" °F")[0])

        # Historic High Temp
        temp_high = temp_string.split(" | ")[6]
        temp_high = temp_high.split("high: ")[1]
        weather_unfound_rerun_df.loc[index, "Historic High Temp"] = int(temp_high.split(" °F")[0])
        
        # Add Place Holders
#         weather_unfound_rerun_df.loc[index, "State"] = state_query
#         weather_unfound_rerun_df.loc[index, "City"] = city_query
#         weather_unfound_rerun_df.loc[index, "CityFIPS"] = row['CityFIPS']

#         # Temperature Range
#         average_temp_range_list.append(temp_avghigh - temp_avglow)
        
        print(f"Processing Record {row_count} of Set 1 | {city_query}, {state_query}")
        weather_unfound_rerun_df.loc[index, "State"] = state_query
        row_count += 1
         
    except Exception as e:
        # TODO Exception Handling needs to be Improved
        print(f"{city_query} not found")
        weather_unfound_df2.loc[index, "State"] = state_query
        weather_unfound_df2.loc[index, "City"] = city_query
        weather_unfound_df2.loc[index, "CityFIPS"] = row['CityFIPS']
        row_count += 1


# In[251]:


# weather_unfound_df2.head(60)
weather_unfound_rerun_df.head()


# In[250]:


# to CSV
weather_unfound_df2.to_csv("output/weather_unfound_df2.csv")
weather_unfound_rerun_df.to_csv("output/weather_unfound_rerun_df.csv")


# # Census Data

# In[135]:


from census import Census
from us import states
import gmaps

# Census & gmaps API Keys
from config import (census_api_key, gkey)
c = Census(census_api_key, year=2013)

# Configure gmaps
gmaps.configure(api_key=gkey)


# In[224]:


# What is Available
# pprint(c.acs5.tables())


# # Figuring out how to manipulate CityFIPS

# 
# US places  
# (example: Fresno city in California is "27000", or prefixed with the state code "0627000")  
# state_place(fields, state_fips, place)
# 
# 
# Address	2630 CAHABA RD, BIRMINGHAM, AL, 35223  
# MSA/MD Code	13820  
# State Code	01  
# County Code	073  
# Tract Code	0108.02  
# MSA/MD Name	BIRMINGHAM-HOOVER, AL  
# State Name	ALABAMA  
# County Name	JEFFERSON COUNTY  
# 
# In the CSV = 0107000-01073010802  
# so State code = 01, Place Code = 07000  
# 
# ```python
# # state_county_tract Specification
# state_county_tract(fields, state_fips, county_fips, tract)
# 
# #The geographic name for all census tracts for county 170 in Alaska:
# c.sf1.get('NAME', geo={'for': 'tract:*',
#                        'in': 'state:{} county:170'.format(states.AK.fips)})
# 
# #The same call using the state_county_tract convenience method:
# c.sf1.state_county_tract('NAME', states.AK.fips, '170', Census.ALL)
# 
# 
# 
# #The Format To Use
# state_place(fields, state_fips, place)
# 
# ```

# In[345]:


# Copy DataFrame
census_cities_df = just_cities
# census_cities_df["State ID"] = ""
state_ID_series = []
place_ID_series = []

# Create State and Place IDs from CityFIPS
# for index, row in example_df.iterrows():
for index, row in census_cities_df.iterrows():
    city_FIPS = row['CityFIPS']
    city_FIPS = str(city_FIPS)
#     print(city_FIPS)
    
    if len(city_FIPS)==9:
        state_ID = city_FIPS[0:2]
#         state_ID_series.append(state_ID)
        place_ID = city_FIPS[2:]
    elif len(city_FIPS)==8:
        state_ID = city_FIPS[0:1]
        state_ID = "0" + state_ID
        place_ID = city_FIPS[1:]
    elif len(city_FIPS)==7:
        state_ID = city_FIPS[0:2]
#         state_ID = "0" + state_ID
        place_ID = city_FIPS[2:]
        place_ID = "00" + place_ID
        
#     print(state_ID_series)
#     print(state_ID)
    state_ID_series.append(state_ID)
#     print(place_ID)
    place_ID_series.append(place_ID)
#     print("")
    
# Add Result to DataFrame
census_cities_df["State ID"] = state_ID_series
census_cities_df["Place ID"] = place_ID_series

# Make Smaller DataFrame for testing
census_cities_df_head = census_cities_df.head()
census_cities_df.loc[census_cities_df["StateDesc"] == "Hawaii",:]
    


# # Census API - Single input

# In[367]:


census_data_test_single = c.acs5.state_place('NAME','15','71550')
census_data_test_single = pd.DataFrame(census_data_test_single)
census_data_test_single.head()

census_data_test_single = c.acs5.state_place(("NAME", "B19013_001E", "B01003_001E", "B01002_001E",
                          "B19301_001E",
                          "B17001_002E",
                          "B23025_005E"),'15','71550')

# Convert to DataFrame
census_data_test_single = pd.DataFrame(census_data_test_single)
# census_pd.head()

# Column Reordering
census_data_test_single = census_data_test_single.rename(columns={"B01003_001E": "Population",
                                      "B01002_001E": "Median Age",
                                      "B19013_001E": "Household Income",
                                      "B19301_001E": "Per Capita Income",
                                      "B17001_002E": "Poverty Count",
                                      "B23025_005E": "Unemployment Count",
                                      "NAME": "Name", "state": "State"})

# Add in Poverty Rate (Poverty Count / Population)
census_data_test_single["Poverty Rate"] = 100 * census_data_test_single["Poverty Count"].astype(
    int) / census_data_test_single["Population"].astype(int)

# Add in Employment Rate (Employment Count / Population)
census_data_test_single["Unemployment Rate"] = 100 * census_data_test_single["Unemployment Count"].astype(
        int) / census_data_test_single["Population"].astype(int)

# Final DataFrame
census_data_test_single = census_data_test_single[["State", "Name", "Population", "Median Age", "Household Income",
                       "Per Capita Income", "Poverty Count", "Poverty Rate", "Unemployment Rate"]]

census_data_test_single


# # Census API Loop
# 
# # Don't run this cell for a second time

# In[183]:


census_results_df = []

# census_results_df = census_cities_df_head

census_data_test_append = []
# census_data_test_fromrecords = []
# census_data_test_fromdict = []
# census_data_test_regular = []

for index, row in census_cities_df.iterrows():
# for index, row in census_cities_df_head.iterrows():
    state_id_query = row['State ID']
    place_id_query = row['Place ID']
    place_id_query = place_id_query.replace(".0","")
    
    
    # The main data submission
    census_data_test = c.acs5.state_place(("NAME", "B19013_001E", "B01003_001E", "B01002_001E", "B19301_001E", "B17001_002E", "B23025_005E"),state_id_query,place_id_query)

#     # Code just to prove the loop works
#     census_data_test.append([state_id_query, place_id_query])

    # Append new record to new variable to build list
    census_data_test_append.append(census_data_test)
    
    # Print to confirm workflow
    print(state_id_query)
    print(place_id_query)
#     print(census_data_test_append)


# In[184]:


# List of list of dictionaries which doesn't work
print(census_data_test_append)


# # Manipulate the Census Loop Results to Coerce them into a Dataframe

# In[226]:


example_data = [[{'NAME': 'Birmingham city, Alabama', 'B19013_001E': 31445.0, 'B01003_001E': 212295.0, 'B01002_001E': 35.9, 'B19301_001E': 19650.0, 'B17001_002E': 62258.0, 'B23025_005E': 15397.0, 'state': '01', 'place': '07000'}], [{'NAME': 'Hoover city, Alabama', 'B19013_001E': 75020.0, 'B01003_001E': 82264.0, 'B01002_001E': 36.7, 'B19301_001E': 38457.0, 'B17001_002E': 5537.0, 'B23025_005E': 2795.0, 'state': '01', 'place': '35896'}], [{'NAME': 'Huntsville city, Alabama', 'B19013_001E': 48881.0, 'B01003_001E': 182317.0, 'B01002_001E': 36.7, 'B19301_001E': 30916.0, 'B17001_002E': 29494.0, 'B23025_005E': 11036.0, 'state': '01', 'place': '37000'}], [{'NAME': 'Mobile city, Alabama', 'B19013_001E': 38644.0, 'B01003_001E': 195116.0, 'B01002_001E': 35.5, 'B19301_001E': 23385.0, 'B17001_002E': 43928.0, 'B23025_005E': 12229.0, 'state': '01', 'place': '50000'}], [{'NAME': 'Montgomery city, Alabama', 'B19013_001E': 43702.0, 'B01003_001E': 204760.0, 'B01002_001E': 34.2, 'B19301_001E': 24365.0, 'B17001_002E': 44774.0, 'B23025_005E': 8940.0, 'state': '01', 'place': '51000'}]]
# Example data, all brackets removed except first and last 
example_data = [{'NAME': 'Birmingham city, Alabama', 'B19013_001E': 31445.0, 'B01003_001E': 212295.0, 'B01002_001E': 35.9, 'B19301_001E': 19650.0, 'B17001_002E': 62258.0, 'B23025_005E': 15397.0, 'state': '01', 'place': '07000'}, {'NAME': 'Hoover city, Alabama', 'B19013_001E': 75020.0, 'B01003_001E': 82264.0, 'B01002_001E': 36.7, 'B19301_001E': 38457.0, 'B17001_002E': 5537.0, 'B23025_005E': 2795.0, 'state': '01', 'place': '35896'}, {'NAME': 'Huntsville city, Alabama', 'B19013_001E': 48881.0, 'B01003_001E': 182317.0, 'B01002_001E': 36.7, 'B19301_001E': 30916.0, 'B17001_002E': 29494.0, 'B23025_005E': 11036.0, 'state': '01', 'place': '37000'}, {'NAME': 'Mobile city, Alabama', 'B19013_001E': 38644.0, 'B01003_001E': 195116.0, 'B01002_001E': 35.5, 'B19301_001E': 23385.0, 'B17001_002E': 43928.0, 'B23025_005E': 12229.0, 'state': '01', 'place': '50000'}, {'NAME': 'Montgomery city, Alabama', 'B19013_001E': 43702.0, 'B01003_001E': 204760.0, 'B01002_001E': 34.2, 'B19301_001E': 24365.0, 'B17001_002E': 44774.0, 'B23025_005E': 8940.0, 'state': '01', 'place': '51000'}, {'NAME': 'Tuscaloosa city, Alabama', 'B19013_001E': 38519.0, 'B01003_001E': 92461.0, 'B01002_001E': 27.6, 'B19301_001E': 21511.0, 'B17001_002E': 21984.0, 'B23025_005E': 3400.0, 'state': '01', 'place': '77256'}, {'NAME': 'Anchorage municipality, Alaska', 'B19013_001E': 77454.0, 'B01003_001E': 295237.0, 'B01002_001E': 32.8, 'B19301_001E': 36214.0, 'B17001_002E': 22874.0, 'B23025_005E': 11785.0, 'state': '02', 'place': '03000'}, {'NAME': 'Avondale city, Arizona', 'B19013_001E': 55506.0, 'B01003_001E': 76872.0, 'B01002_001E': 29.7, 'B19301_001E': 20635.0, 'B17001_002E': 13094.0, 'B23025_005E': 4299.0, 'state': '04', 'place': '04720'}, {'NAME': 'Chandler city, Arizona', 'B19013_001E': 71083.0, 'B01003_001E': 241096.0, 'B01002_001E': 34.0, 'B19301_001E': 32185.0, 'B17001_002E': 21914.0, 'B23025_005E': 10076.0, 'state': '04', 'place': '12000'}, {'NAME': 'Gilbert town, Arizona', 'B19013_001E': 80355.0, 'B01003_001E': 215683.0, 'B01002_001E': 32.4, 'B19301_001E': 31673.0, 'B17001_002E': 14398.0, 'B23025_005E': 7411.0, 'state': '04', 'place': '27400'}, {'NAME': 'Glendale city, Arizona', 'B19013_001E': 47474.0, 'B01003_001E': 230047.0, 'B01002_001E': 32.8, 'B19301_001E': 22071.0, 'B17001_002E': 46571.0, 'B23025_005E': 13982.0, 'state': '04', 'place': '27820'}, {'NAME': 'Mesa city, Arizona', 'B19013_001E': 48547.0, 'B01003_001E': 447002.0, 'B01002_001E': 35.6, 'B19301_001E': 24155.0, 'B17001_002E': 69449.0, 'B23025_005E': 21048.0, 'state': '04', 'place': '46000'}, {'NAME': 'Peoria city, Arizona', 'B19013_001E': 62013.0, 'B01003_001E': 157152.0, 'B01002_001E': 38.5, 'B19301_001E': 28751.0, 'B17001_002E': 15451.0, 'B23025_005E': 6557.0, 'state': '04', 'place': '54050'}, {'NAME': 'Phoenix city, Arizona', 'B19013_001E': 47139.0, 'B01003_001E': 1473639.0, 'B01002_001E': 32.6, 'B19301_001E': 23812.0, 'B17001_002E': 331487.0, 'B23025_005E': 77364.0, 'state': '04', 'place': '55000'}, {'NAME': 'Scottsdale city, Arizona', 'B19013_001E': 72154.0, 'B01003_001E': 221283.0, 'B01002_001E': 45.4, 'B19301_001E': 50531.0, 'B17001_002E': 19235.0, 'B23025_005E': 7770.0, 'state': '04', 'place': '65000'}, {'NAME': 'Surprise city, Arizona', 'B19013_001E': 58455.0, 'B01003_001E': 118784.0, 'B01002_001E': 37.0, 'B19301_001E': 24612.0, 'B17001_002E': 10910.0, 'B23025_005E': 4796.0, 'state': '04', 'place': '71510'}, {'NAME': 'Tempe city, Arizona', 'B19013_001E': 47941.0, 'B01003_001E': 164742.0, 'B01002_001E': 28.3, 'B19301_001E': 26227.0, 'B17001_002E': 34433.0, 'B23025_005E': 9217.0, 'state': '04', 'place': '73000'}, {'NAME': 'Tucson city, Arizona', 'B19013_001E': 37032.0, 'B01003_001E': 523278.0, 'B01002_001E': 33.0, 'B19301_001E': 20314.0, 'B17001_002E': 126367.0, 'B23025_005E': 31441.0, 'state': '04', 'place': '77000'}, {'NAME': 'Yuma city, Arizona', 'B19013_001E': 44220.0, 'B01003_001E': 92492.0, 'B01002_001E': 30.2, 'B19301_001E': 20617.0, 'B17001_002E': 14487.0, 'B23025_005E': 4725.0, 'state': '04', 'place': '85540'}, {'NAME': 'Fayetteville city, Arkansas', 'B19013_001E': 36314.0, 'B01003_001E': 75602.0, 'B01002_001E': 27.6, 'B19301_001E': 25503.0, 'B17001_002E': 17687.0, 'B23025_005E': 3318.0, 'state': '05', 'place': '23290'}, {'NAME': 'Fort Smith city, Arkansas', 'B19013_001E': 36618.0, 'B01003_001E': 86924.0, 'B01002_001E': 35.3, 'B19301_001E': 22704.0, 'B17001_002E': 21323.0, 'B23025_005E': 2727.0, 'state': '05', 'place': '24550'}, {'NAME': 'Jonesboro city, Arkansas', 'B19013_001E': 40046.0, 'B01003_001E': 69049.0, 'B01002_001E': 30.9, 'B19301_001E': 24007.0, 'B17001_002E': 15945.0, 'B23025_005E': 3463.0, 'state': '05', 'place': '35710'}, {'NAME': 'Little Rock city, Arkansas', 'B19013_001E': 44896.0, 'B01003_001E': 195092.0, 'B01002_001E': 35.3, 'B19301_001E': 29294.0, 'B17001_002E': 35766.0, 'B23025_005E': 9914.0, 'state': '05', 'place': '41000'}, {'NAME': 'Springdale city, Arkansas', 'B19013_001E': 41281.0, 'B01003_001E': 72070.0, 'B01002_001E': 29.4, 'B19301_001E': 18390.0, 'B17001_002E': 16901.0, 'B23025_005E': 2642.0, 'state': '05', 'place': '66080'}, {'NAME': 'Alameda city, California', 'B19013_001E': 74606.0, 'B01003_001E': 74818.0, 'B01002_001E': 40.6, 'B19301_001E': 41340.0, 'B17001_002E': 7592.0, 'B23025_005E': 3675.0, 'state': '06', 'place': '00562'}, {'NAME': 'Alhambra city, California', 'B19013_001E': 54148.0, 'B01003_001E': 83799.0, 'B01002_001E': 39.8, 'B19301_001E': 25703.0, 'B17001_002E': 11565.0, 'B23025_005E': 3412.0, 'state': '06', 'place': '00884'}, {'NAME': 'Anaheim city, California', 'B19013_001E': 59165.0, 'B01003_001E': 340081.0, 'B01002_001E': 32.8, 'B19301_001E': 23400.0, 'B17001_002E': 54093.0, 'B23025_005E': 20606.0, 'state': '06', 'place': '02000'}, {'NAME': 'Antioch city, California', 'B19013_001E': 65254.0, 'B01003_001E': 104035.0, 'B01002_001E': 33.8, 'B19301_001E': 24678.0, 'B17001_002E': 15335.0, 'B23025_005E': 7245.0, 'state': '06', 'place': '02252'}, {'NAME': 'Apple Valley town, California', 'B19013_001E': 48432.0, 'B01003_001E': 69785.0, 'B01002_001E': 36.6, 'B19301_001E': 22941.0, 'B17001_002E': 13990.0, 'B23025_005E': 4395.0, 'state': '06', 'place': '02364'}, {'NAME': 'Bakersfield city, California', 'B19013_001E': 56204.0, 'B01003_001E': 352918.0, 'B01002_001E': 30.1, 'B19301_001E': 23316.0, 'B17001_002E': 71445.0, 'B23025_005E': 20254.0, 'state': '06', 'place': '03526'}, {'NAME': 'Baldwin Park city, California', 'B19013_001E': 51153.0, 'B01003_001E': 75933.0, 'B01002_001E': 31.0, 'B19301_001E': 15314.0, 'B17001_002E': 13164.0, 'B23025_005E': 5450.0, 'state': '06', 'place': '03666'}, {'NAME': 'Bellflower city, California', 'B19013_001E': 49637.0, 'B01003_001E': 76989.0, 'B01002_001E': 32.0, 'B19301_001E': 20397.0, 'B17001_002E': 13075.0, 'B23025_005E': 3981.0, 'state': '06', 'place': '04982'}, {'NAME': 'Berkeley city, California', 'B19013_001E': 63312.0, 'B01003_001E': 114037.0, 'B01002_001E': 31.8, 'B19301_001E': 41308.0, 'B17001_002E': 19464.0, 'B23025_005E': 5094.0, 'state': '06', 'place': '06000'}, {'NAME': 'Buena Park city, California', 'B19013_001E': 66371.0, 'B01003_001E': 81522.0, 'B01002_001E': 35.5, 'B19301_001E': 23623.0, 'B17001_002E': 9746.0, 'B23025_005E': 3275.0, 'state': '06', 'place': '08786'}, {'NAME': 'Burbank city, California', 'B19013_001E': 66240.0, 'B01003_001E': 103850.0, 'B01002_001E': 38.6, 'B19301_001E': 33663.0, 'B17001_002E': 9710.0, 'B23025_005E': 5527.0, 'state': '06', 'place': '08954'}, {'NAME': 'Carlsbad city, California', 'B19013_001E': 83908.0, 'B01003_001E': 107307.0, 'B01002_001E': 41.1, 'B19301_001E': 43441.0, 'B17001_002E': 11358.0, 'B23025_005E': 4807.0, 'state': '06', 'place': '11194'}, {'NAME': 'Carson city, California', 'B19013_001E': 72235.0, 'B01003_001E': 91994.0, 'B01002_001E': 37.3, 'B19301_001E': 23762.0, 'B17001_002E': 9142.0, 'B23025_005E': 7021.0, 'state': '06', 'place': '11530'}, {'NAME': 'Chico city, California', 'B19013_001E': 43372.0, 'B01003_001E': 86833.0, 'B01002_001E': 29.3, 'B19301_001E': 24221.0, 'B17001_002E': 19368.0, 'B23025_005E': 5495.0, 'state': '06', 'place': '13014'}, {'NAME': 'Chino city, California', 'B19013_001E': 71466.0, 'B01003_001E': 79342.0, 'B01002_001E': 34.0, 'B19301_001E': 23866.0, 'B17001_002E': 7134.0, 'B23025_005E': 4264.0, 'state': '06', 'place': '13210'}, {'NAME': 'Chino Hills city, California', 'B19013_001E': 96497.0, 'B01003_001E': 75551.0, 'B01002_001E': 36.7, 'B19301_001E': 34955.0, 'B17001_002E': 4603.0, 'B23025_005E': 4486.0, 'state': '06', 'place': '13214'}, {'NAME': 'Chula Vista city, California', 'B19013_001E': 64801.0, 'B01003_001E': 248048.0, 'B01002_001E': 33.7, 'B19301_001E': 25104.0, 'B17001_002E': 29118.0, 'B23025_005E': 14912.0, 'state': '06', 'place': '13392'}, {'NAME': 'Citrus Heights city, California', 'B19013_001E': 52183.0, 'B01003_001E': 84218.0, 'B01002_001E': 37.0, 'B19301_001E': 25023.0, 'B17001_002E': 12322.0, 'B23025_005E': 6487.0, 'state': '06', 'place': '13588'}, {'NAME': 'Clovis city, California', 'B19013_001E': 65260.0, 'B01003_001E': 97100.0, 'B01002_001E': 33.9, 'B19301_001E': 27906.0, 'B17001_002E': 12711.0, 'B23025_005E': 5383.0, 'state': '06', 'place': '14218'}, {'NAME': 'Compton city, California', 'B19013_001E': 42953.0, 'B01003_001E': 97040.0, 'B01002_001E': 27.6, 'B19301_001E': 13548.0, 'B17001_002E': 25343.0, 'B23025_005E': 7250.0, 'state': '06', 'place': '15044'}, {'NAME': 'Concord city, California', 'B19013_001E': 65798.0, 'B01003_001E': 123658.0, 'B01002_001E': 37.1, 'B19301_001E': 31359.0, 'B17001_002E': 14827.0, 'B23025_005E': 7484.0, 'state': '06', 'place': '16000'}, {'NAME': 'Corona city, California', 'B19013_001E': 77123.0, 'B01003_001E': 155227.0, 'B01002_001E': 32.6, 'B19301_001E': 26832.0, 'B17001_002E': 16722.0, 'B23025_005E': 9211.0, 'state': '06', 'place': '16350'}, {'NAME': 'Costa Mesa city, California', 'B19013_001E': 65830.0, 'B01003_001E': 110871.0, 'B01002_001E': 33.8, 'B19301_001E': 34100.0, 'B17001_002E': 16548.0, 'B23025_005E': 6346.0, 'state': '06', 'place': '16532'}, {'NAME': 'Daly City city, California', 'B19013_001E': 74436.0, 'B01003_001E': 102605.0, 'B01002_001E': 38.6, 'B19301_001E': 28827.0, 'B17001_002E': 8777.0, 'B23025_005E': 5812.0, 'state': '06', 'place': '17918'}, {'NAME': 'Downey city, California', 'B19013_001E': 60939.0, 'B01003_001E': 112334.0, 'B01002_001E': 34.0, 'B19301_001E': 23055.0, 'B17001_002E': 13178.0, 'B23025_005E': 5883.0, 'state': '06', 'place': '19766'}, {'NAME': 'El Cajon city, California', 'B19013_001E': 44112.0, 'B01003_001E': 100590.0, 'B01002_001E': 32.4, 'B19301_001E': 19803.0, 'B17001_002E': 26152.0, 'B23025_005E': 6681.0, 'state': '06', 'place': '21712'}, {'NAME': 'Elk Grove city, California', 'B19013_001E': 77791.0, 'B01003_001E': 155350.0, 'B01002_001E': 33.8, 'B19301_001E': 28898.0, 'B17001_002E': 14711.0, 'B23025_005E': 8340.0, 'state': '06', 'place': '22020'}, {'NAME': 'El Monte city, California', 'B19013_001E': 39535.0, 'B01003_001E': 114412.0, 'B01002_001E': 33.5, 'B19301_001E': 14735.0, 'B17001_002E': 27574.0, 'B23025_005E': 7496.0, 'state': '06', 'place': '22230'}, {'NAME': 'Escondido city, California', 'B19013_001E': 49362.0, 'B01003_001E': 145859.0, 'B01002_001E': 32.7, 'B19301_001E': 21653.0, 'B17001_002E': 26931.0, 'B23025_005E': 6947.0, 'state': '06', 'place': '22804'}, {'NAME': 'Fairfield city, California', 'B19013_001E': 64702.0, 'B01003_001E': 106533.0, 'B01002_001E': 33.0, 'B19301_001E': 26611.0, 'B17001_002E': 14048.0, 'B23025_005E': 5607.0, 'state': '06', 'place': '23182'}, {'NAME': 'Folsom city, California', 'B19013_001E': 98359.0, 'B01003_001E': 72424.0, 'B01002_001E': 37.7, 'B19301_001E': 37821.0, 'B17001_002E': 2973.0, 'B23025_005E': 3232.0, 'state': '06', 'place': '24638'}, {'NAME': 'Fontana city, California', 'B19013_001E': 64354.0, 'B01003_001E': 198692.0, 'B01002_001E': 29.1, 'B19301_001E': 19299.0, 'B17001_002E': 30547.0, 'B23025_005E': 15097.0, 'state': '06', 'place': '24680'}, {'NAME': 'Fremont city, California', 'B19013_001E': 101535.0, 'B01003_001E': 218172.0, 'B01002_001E': 37.3, 'B19301_001E': 40190.0, 'B17001_002E': 13088.0, 'B23025_005E': 9327.0, 'state': '06', 'place': '26000'}, {'NAME': 'Fresno city, California', 'B19013_001E': 42015.0, 'B01003_001E': 500819.0, 'B01002_001E': 29.6, 'B19301_001E': 19455.0, 'B17001_002E': 142471.0, 'B23025_005E': 35746.0, 'state': '06', 'place': '27000'}, {'NAME': 'Fullerton city, California', 'B19013_001E': 67384.0, 'B01003_001E': 136702.0, 'B01002_001E': 34.4, 'B19301_001E': 29913.0, 'B17001_002E': 21438.0, 'B23025_005E': 7614.0, 'state': '06', 'place': '28000'}, {'NAME': 'Garden Grove city, California', 'B19013_001E': 59648.0, 'B01003_001E': 172785.0, 'B01002_001E': 35.6, 'B19301_001E': 20849.0, 'B17001_002E': 28535.0, 'B23025_005E': 9941.0, 'state': '06', 'place': '29000'}, {'NAME': 'Glendale city, California', 'B19013_001E': 53020.0, 'B01003_001E': 193381.0, 'B01002_001E': 40.7, 'B19301_001E': 29290.0, 'B17001_002E': 27239.0, 'B23025_005E': 11205.0, 'state': '06', 'place': '30000'}, {'NAME': 'Hawthorne city, California', 'B19013_001E': 44649.0, 'B01003_001E': 85092.0, 'B01002_001E': 31.1, 'B19301_001E': 20162.0, 'B17001_002E': 16196.0, 'B23025_005E': 4522.0, 'state': '06', 'place': '32548'}, {'NAME': 'Hayward city, California', 'B19013_001E': 62013.0, 'B01003_001E': 147163.0, 'B01002_001E': 33.8, 'B19301_001E': 25208.0, 'B17001_002E': 20931.0, 'B23025_005E': 11098.0, 'state': '06', 'place': '33000'}, {'NAME': 'Hemet city, California', 'B19013_001E': 32774.0, 'B01003_001E': 79986.0, 'B01002_001E': 39.6, 'B19301_001E': 17917.0, 'B17001_002E': 18460.0, 'B23025_005E': 5950.0, 'state': '06', 'place': '33182'}, {'NAME': 'Hesperia city, California', 'B19013_001E': 44158.0, 'B01003_001E': 90804.0, 'B01002_001E': 31.1, 'B19301_001E': 16239.0, 'B17001_002E': 22730.0, 'B23025_005E': 7044.0, 'state': '06', 'place': '33434'}, {'NAME': 'Huntington Beach city, California', 'B19013_001E': 81389.0, 'B01003_001E': 193197.0, 'B01002_001E': 40.6, 'B19301_001E': 42196.0, 'B17001_002E': 17045.0, 'B23025_005E': 9788.0, 'state': '06', 'place': '36000'}, {'NAME': 'Indio city, California', 'B19013_001E': 50068.0, 'B01003_001E': 80167.0, 'B01002_001E': 32.2, 'B19301_001E': 20607.0, 'B17001_002E': 17333.0, 'B23025_005E': 5931.0, 'state': '06', 'place': '36448'}, {'NAME': 'Inglewood city, California', 'B19013_001E': 43394.0, 'B01003_001E': 110585.0, 'B01002_001E': 33.0, 'B19301_001E': 20150.0, 'B17001_002E': 24470.0, 'B23025_005E': 8256.0, 'state': '06', 'place': '36546'}, {'NAME': 'Irvine city, California', 'B19013_001E': 90585.0, 'B01003_001E': 221266.0, 'B01002_001E': 34.2, 'B19301_001E': 43096.0, 'B17001_002E': 25971.0, 'B23025_005E': 8306.0, 'state': '06', 'place': '36770'}, {'NAME': 'Lake Forest city, California', 'B19013_001E': 93631.0, 'B01003_001E': 78253.0, 'B01002_001E': 38.4, 'B19301_001E': 39860.0, 'B17001_002E': 4646.0, 'B23025_005E': 3066.0, 'state': '06', 'place': '39496'}, {'NAME': 'Lakewood city, California', 'B19013_001E': 77786.0, 'B01003_001E': 80511.0, 'B01002_001E': 37.7, 'B19301_001E': 29354.0, 'B17001_002E': 6538.0, 'B23025_005E': 3813.0, 'state': '06', 'place': '39892'}, {'NAME': 'Lancaster city, California', 'B19013_001E': 50193.0, 'B01003_001E': 157368.0, 'B01002_001E': 32.3, 'B19301_001E': 20156.0, 'B17001_002E': 32236.0, 'B23025_005E': 8260.0, 'state': '06', 'place': '40130'}, {'NAME': 'Livermore city, California', 'B19013_001E': 99161.0, 'B01003_001E': 82442.0, 'B01002_001E': 38.4, 'B19301_001E': 42213.0, 'B17001_002E': 4694.0, 'B23025_005E': 3223.0, 'state': '06', 'place': '41992'}, {'NAME': 'Long Beach city, California', 'B19013_001E': 52711.0, 'B01003_001E': 465424.0, 'B01002_001E': 33.9, 'B19301_001E': 27040.0, 'B17001_002E': 92847.0, 'B23025_005E': 30427.0, 'state': '06', 'place': '43000'}, {'NAME': 'Los Angeles city, California', 'B19013_001E': 49497.0, 'B01003_001E': 3827261.0, 'B01002_001E': 34.3, 'B19301_001E': 27829.0, 'B17001_002E': 825131.0, 'B23025_005E': 245749.0, 'state': '06', 'place': '44000'}, {'NAME': 'Lynwood city, California', 'B19013_001E': 40740.0, 'B01003_001E': 70257.0, 'B01002_001E': 27.9, 'B19301_001E': 12187.0, 'B17001_002E': 16951.0, 'B23025_005E': 4112.0, 'state': '06', 'place': '44574'}, {'NAME': 'Manteca city, California', 'B19013_001E': 61458.0, 'B01003_001E': 69168.0, 'B01002_001E': 33.0, 'B19301_001E': 23511.0, 'B17001_002E': 7411.0, 'B23025_005E': 5660.0, 'state': '06', 'place': '45484'}, {'NAME': 'Menifee city, California', 'B19013_001E': 54903.0, 'B01003_001E': 79604.0, 'B01002_001E': 37.9, 'B19301_001E': 23478.0, 'B17001_002E': 8108.0, 'B23025_005E': 6151.0, 'state': '06', 'place': '46842'}, {'NAME': 'Merced city, California', 'B19013_001E': 37822.0, 'B01003_001E': 79639.0, 'B01002_001E': 28.4, 'B19301_001E': 16876.0, 'B17001_002E': 23629.0, 'B23025_005E': 5790.0, 'state': '06', 'place': '46898'}, {'NAME': 'Milpitas city, California', 'B19013_001E': 95466.0, 'B01003_001E': 67695.0, 'B01002_001E': 36.8, 'B19301_001E': 33789.0, 'B17001_002E': 4702.0, 'B23025_005E': 3201.0, 'state': '06', 'place': '47766'}, {'NAME': 'Mission Viejo city, California', 'B19013_001E': 96210.0, 'B01003_001E': 94311.0, 'B01002_001E': 43.0, 'B19301_001E': 40909.0, 'B17001_002E': 4964.0, 'B23025_005E': 4451.0, 'state': '06', 'place': '48256'}, {'NAME': 'Modesto city, California', 'B19013_001E': 47060.0, 'B01003_001E': 202629.0, 'B01002_001E': 33.6, 'B19301_001E': 22439.0, 'B17001_002E': 41546.0, 'B23025_005E': 15739.0, 'state': '06', 'place': '48354'}, {'NAME': 'Moreno Valley city, California', 'B19013_001E': 54918.0, 'B01003_001E': 196234.0, 'B01002_001E': 29.2, 'B19301_001E': 18186.0, 'B17001_002E': 38015.0, 'B23025_005E': 14603.0, 'state': '06', 'place': '49270'}, {'NAME': 'Mountain View city, California', 'B19013_001E': 97338.0, 'B01003_001E': 75477.0, 'B01002_001E': 35.8, 'B19301_001E': 54758.0, 'B17001_002E': 6107.0, 'B23025_005E': 3430.0, 'state': '06', 'place': '49670'}, {'NAME': 'Murrieta city, California', 'B19013_001E': 74496.0, 'B01003_001E': 104584.0, 'B01002_001E': 33.1, 'B19301_001E': 28452.0, 'B17001_002E': 7280.0, 'B23025_005E': 6195.0, 'state': '06', 'place': '50076'}, {'NAME': 'Napa city, California', 'B19013_001E': 63274.0, 'B01003_001E': 77698.0, 'B01002_001E': 37.4, 'B19301_001E': 30668.0, 'B17001_002E': 8507.0, 'B23025_005E': 3983.0, 'state': '06', 'place': '50258'}, {'NAME': 'Newport Beach city, California', 'B19013_001E': 106333.0, 'B01003_001E': 86001.0, 'B01002_001E': 43.7, 'B19301_001E': 78494.0, 'B17001_002E': 6799.0, 'B23025_005E': 3611.0, 'state': '06', 'place': '51182'}, {'NAME': 'Norwalk city, California', 'B19013_001E': 60770.0, 'B01003_001E': 105940.0, 'B01002_001E': 33.6, 'B19301_001E': 19449.0, 'B17001_002E': 13469.0, 'B23025_005E': 6048.0, 'state': '06', 'place': '52526'}, {'NAME': 'Oakland city, California', 'B19013_001E': 52583.0, 'B01003_001E': 397011.0, 'B01002_001E': 36.2, 'B19301_001E': 31971.0, 'B17001_002E': 80274.0, 'B23025_005E': 26912.0, 'state': '06', 'place': '53000'}, {'NAME': 'Oceanside city, California', 'B19013_001E': 58153.0, 'B01003_001E': 169407.0, 'B01002_001E': 35.4, 'B19301_001E': 26863.0, 'B17001_002E': 22398.0, 'B23025_005E': 8461.0, 'state': '06', 'place': '53322'}, {'NAME': 'Ontario city, California', 'B19013_001E': 54249.0, 'B01003_001E': 165702.0, 'B01002_001E': 31.0, 'B19301_001E': 18522.0, 'B17001_002E': 29801.0, 'B23025_005E': 12195.0, 'state': '06', 'place': '53896'}, {'NAME': 'Orange city, California', 'B19013_001E': 78838.0, 'B01003_001E': 137999.0, 'B01002_001E': 35.4, 'B19301_001E': 31535.0, 'B17001_002E': 15623.0, 'B23025_005E': 6522.0, 'state': '06', 'place': '53980'}, {'NAME': 'Oxnard city, California', 'B19013_001E': 60784.0, 'B01003_001E': 199574.0, 'B01002_001E': 30.5, 'B19301_001E': 20605.0, 'B17001_002E': 33038.0, 'B23025_005E': 10373.0, 'state': '06', 'place': '54652'}, {'NAME': 'Palmdale city, California', 'B19013_001E': 53922.0, 'B01003_001E': 153885.0, 'B01002_001E': 29.1, 'B19301_001E': 18797.0, 'B17001_002E': 32318.0, 'B23025_005E': 9923.0, 'state': '06', 'place': '55156'}, {'NAME': 'Pasadena city, California', 'B19013_001E': 69302.0, 'B01003_001E': 138004.0, 'B01002_001E': 37.3, 'B19301_001E': 41152.0, 'B17001_002E': 17904.0, 'B23025_005E': 7956.0, 'state': '06', 'place': '56000'}, {'NAME': 'Perris city, California', 'B19013_001E': 48311.0, 'B01003_001E': 69743.0, 'B01002_001E': 27.0, 'B19301_001E': 13666.0, 'B17001_002E': 17860.0, 'B23025_005E': 6231.0, 'state': '06', 'place': '56700'}, {'NAME': 'Pleasanton city, California', 'B19013_001E': 118317.0, 'B01003_001E': 71488.0, 'B01002_001E': 40.1, 'B19301_001E': 50540.0, 'B17001_002E': 3450.0, 'B23025_005E': 2979.0, 'state': '06', 'place': '57792'}, {'NAME': 'Pomona city, California', 'B19013_001E': 49474.0, 'B01003_001E': 150006.0, 'B01002_001E': 29.9, 'B19301_001E': 17035.0, 'B17001_002E': 31533.0, 'B23025_005E': 8742.0, 'state': '06', 'place': '58072'}, {'NAME': 'Rancho Cucamonga city, California', 'B19013_001E': 77835.0, 'B01003_001E': 167743.0, 'B01002_001E': 35.2, 'B19301_001E': 32209.0, 'B17001_002E': 11296.0, 'B23025_005E': 9994.0, 'state': '06', 'place': '59451'}, {'NAME': 'Redding city, California', 'B19013_001E': 44236.0, 'B01003_001E': 90370.0, 'B01002_001E': 38.0, 'B19301_001E': 23443.0, 'B17001_002E': 16070.0, 'B23025_005E': 5114.0, 'state': '06', 'place': '59920'}, {'NAME': 'Redlands city, California', 'B19013_001E': 66835.0, 'B01003_001E': 69277.0, 'B01002_001E': 36.2, 'B19301_001E': 32389.0, 'B17001_002E': 8352.0, 'B23025_005E': 2914.0, 'state': '06', 'place': '59962'}, {'NAME': 'Redondo Beach city, California', 'B19013_001E': 99496.0, 'B01003_001E': 67094.0, 'B01002_001E': 40.0, 'B19301_001E': 53689.0, 'B17001_002E': 3634.0, 'B23025_005E': 2888.0, 'state': '06', 'place': '60018'}, {'NAME': 'Redwood City city, California', 'B19013_001E': 79419.0, 'B01003_001E': 78241.0, 'B01002_001E': 36.6, 'B19301_001E': 40562.0, 'B17001_002E': 6890.0, 'B23025_005E': 3186.0, 'state': '06', 'place': '60102'}, {'NAME': 'Rialto city, California', 'B19013_001E': 49593.0, 'B01003_001E': 100479.0, 'B01002_001E': 28.4, 'B19301_001E': 15948.0, 'B17001_002E': 19048.0, 'B23025_005E': 7777.0, 'state': '06', 'place': '60466'}, {'NAME': 'Richmond city, California', 'B19013_001E': 54589.0, 'B01003_001E': 105280.0, 'B01002_001E': 34.8, 'B19301_001E': 25722.0, 'B17001_002E': 19266.0, 'B23025_005E': 6387.0, 'state': '06', 'place': '60620'}, {'NAME': 'Riverside city, California', 'B19013_001E': 55636.0, 'B01003_001E': 309150.0, 'B01002_001E': 30.4, 'B19301_001E': 22182.0, 'B17001_002E': 57144.0, 'B23025_005E': 21210.0, 'state': '06', 'place': '62000'}, {'NAME': 'Roseville city, California', 'B19013_001E': 74114.0, 'B01003_001E': 122039.0, 'B01002_001E': 37.1, 'B19301_001E': 33622.0, 'B17001_002E': 10018.0, 'B23025_005E': 5904.0, 'state': '06', 'place': '62938'}, {'NAME': 'Sacramento city, California', 'B19013_001E': 49753.0, 'B01003_001E': 471477.0, 'B01002_001E': 33.7, 'B19301_001E': 25508.0, 'B17001_002E': 101466.0, 'B23025_005E': 34164.0, 'state': '06', 'place': '64000'}, {'NAME': 'Salinas city, California', 'B19013_001E': 49264.0, 'B01003_001E': 152340.0, 'B01002_001E': 28.8, 'B19301_001E': 17396.0, 'B17001_002E': 31514.0, 'B23025_005E': 8205.0, 'state': '06', 'place': '64224'}, {'NAME': 'San Bernardino city, California', 'B19013_001E': 38385.0, 'B01003_001E': 211528.0, 'B01002_001E': 29.2, 'B19301_001E': 14879.0, 'B17001_002E': 66825.0, 'B23025_005E': 15840.0, 'state': '06', 'place': '65000'}, {'NAME': 'San Buenaventura (Ventura) city, California', 'B19013_001E': 65137.0, 'B01003_001E': 107551.0, 'B01002_001E': 39.3, 'B19301_001E': 32311.0, 'B17001_002E': 11290.0, 'B23025_005E': 5535.0, 'state': '06', 'place': '65042'}, {'NAME': 'San Diego city, California', 'B19013_001E': 64058.0, 'B01003_001E': 1322838.0, 'B01002_001E': 33.7, 'B19301_001E': 33152.0, 'B17001_002E': 200777.0, 'B23025_005E': 65948.0, 'state': '06', 'place': '66000'}, {'NAME': 'San Francisco city, California', 'B19013_001E': 75604.0, 'B01003_001E': 817501.0, 'B01002_001E': 38.5, 'B19301_001E': 48486.0, 'B17001_002E': 108306.0, 'B23025_005E': 41148.0, 'state': '06', 'place': '67000'}, {'NAME': 'San Jose city, California', 'B19013_001E': 81829.0, 'B01003_001E': 968903.0, 'B01002_001E': 35.6, 'B19301_001E': 34025.0, 'B17001_002E': 117443.0, 'B23025_005E': 55267.0, 'state': '06', 'place': '68000'}, {'NAME': 'San Leandro city, California', 'B19013_001E': 63055.0, 'B01003_001E': 86038.0, 'B01002_001E': 39.9, 'B19301_001E': 28801.0, 'B17001_002E': 8555.0, 'B23025_005E': 5232.0, 'state': '06', 'place': '68084'}, {'NAME': 'San Marcos city, California', 'B19013_001E': 53657.0, 'B01003_001E': 85322.0, 'B01002_001E': 34.5, 'B19301_001E': 24484.0, 'B17001_002E': 12342.0, 'B23025_005E': 3025.0, 'state': '06', 'place': '68196'}, {'NAME': 'San Mateo city, California', 'B19013_001E': 85669.0, 'B01003_001E': 98601.0, 'B01002_001E': 39.2, 'B19301_001E': 45202.0, 'B17001_002E': 6899.0, 'B23025_005E': 4442.0, 'state': '06', 'place': '68252'}, {'NAME': 'San Ramon city, California', 'B19013_001E': 127313.0, 'B01003_001E': 72707.0, 'B01002_001E': 37.4, 'B19301_001E': 51091.0, 'B17001_002E': 2767.0, 'B23025_005E': 2741.0, 'state': '06', 'place': '68378'}, {'NAME': 'Santa Ana city, California', 'B19013_001E': 53335.0, 'B01003_001E': 328719.0, 'B01002_001E': 29.2, 'B19301_001E': 16374.0, 'B17001_002E': 68903.0, 'B23025_005E': 17512.0, 'state': '06', 'place': '69000'}, {'NAME': 'Santa Barbara city, California', 'B19013_001E': 65034.0, 'B01003_001E': 89062.0, 'B01002_001E': 36.1, 'B19301_001E': 37225.0, 'B17001_002E': 12343.0, 'B23025_005E': 3843.0, 'state': '06', 'place': '69070'}, {'NAME': 'Santa Clara city, California', 'B19013_001E': 91583.0, 'B01003_001E': 117817.0, 'B01002_001E': 34.4, 'B19301_001E': 39966.0, 'B17001_002E': 10319.0, 'B23025_005E': 5529.0, 'state': '06', 'place': '69084'}, {'NAME': 'Santa Clarita city, California', 'B19013_001E': 82607.0, 'B01003_001E': 177366.0, 'B01002_001E': 36.4, 'B19301_001E': 33818.0, 'B17001_002E': 16538.0, 'B23025_005E': 10113.0, 'state': '06', 'place': '69088'}, {'NAME': 'Santa Maria city, California', 'B19013_001E': 50563.0, 'B01003_001E': 100152.0, 'B01002_001E': 28.9, 'B19301_001E': 18560.0, 'B17001_002E': 20448.0, 'B23025_005E': 5419.0, 'state': '06', 'place': '69196'}, {'NAME': 'Santa Monica city, California', 'B19013_001E': 73649.0, 'B01003_001E': 90752.0, 'B01002_001E': 40.2, 'B19301_001E': 57390.0, 'B17001_002E': 10026.0, 'B23025_005E': 5474.0, 'state': '06', 'place': '70000'}, {'NAME': 'Santa Rosa city, California', 'B19013_001E': 60354.0, 'B01003_001E': 169005.0, 'B01002_001E': 36.7, 'B19301_001E': 29688.0, 'B17001_002E': 22423.0, 'B23025_005E': 10060.0, 'state': '06', 'place': '70098'}, {'NAME': 'Simi Valley city, California', 'B19013_001E': 87269.0, 'B01003_001E': 124803.0, 'B01002_001E': 38.1, 'B19301_001E': 36516.0, 'B17001_002E': 8205.0, 'B23025_005E': 5876.0, 'state': '06', 'place': '72016'}, {'NAME': 'South Gate city, California', 'B19013_001E': 42776.0, 'B01003_001E': 95000.0, 'B01002_001E': 30.3, 'B19301_001E': 14259.0, 'B17001_002E': 19954.0, 'B23025_005E': 6647.0, 'state': '06', 'place': '73080'}, {'NAME': 'Stockton city, California', 'B19013_001E': 46831.0, 'B01003_001E': 294406.0, 'B01002_001E': 31.0, 'B19301_001E': 19896.0, 'B17001_002E': 70269.0, 'B23025_005E': 23063.0, 'state': '06', 'place': '75000'}, {'NAME': 'Sunnyvale city, California', 'B19013_001E': 100043.0, 'B01003_001E': 143315.0, 'B01002_001E': 35.2, 'B19301_001E': 45977.0, 'B17001_002E': 11586.0, 'B23025_005E': 6956.0, 'state': '06', 'place': '77000'}, {'NAME': 'Temecula city, California', 'B19013_001E': 78356.0, 'B01003_001E': 102605.0, 'B01002_001E': 33.3, 'B19301_001E': 28018.0, 'B17001_002E': 8697.0, 'B23025_005E': 5393.0, 'state': '06', 'place': '78120'}, {'NAME': 'Thousand Oaks city, California', 'B19013_001E': 100476.0, 'B01003_001E': 127356.0, 'B01002_001E': 41.7, 'B19301_001E': 45522.0, 'B17001_002E': 8586.0, 'B23025_005E': 6313.0, 'state': '06', 'place': '78582'}, {'NAME': 'Torrance city, California', 'B19013_001E': 77061.0, 'B01003_001E': 146187.0, 'B01002_001E': 41.8, 'B19301_001E': 36234.0, 'B17001_002E': 10711.0, 'B23025_005E': 6295.0, 'state': '06', 'place': '80000'}, {'NAME': 'Tracy city, California', 'B19013_001E': 76098.0, 'B01003_001E': 83452.0, 'B01002_001E': 32.7, 'B19301_001E': 26652.0, 'B17001_002E': 6770.0, 'B23025_005E': 5848.0, 'state': '06', 'place': '80238'}, {'NAME': 'Turlock city, California', 'B19013_001E': 53270.0, 'B01003_001E': 69185.0, 'B01002_001E': 33.3, 'B19301_001E': 23199.0, 'B17001_002E': 11764.0, 'B23025_005E': 5113.0, 'state': '06', 'place': '80812'}, {'NAME': 'Tustin city, California', 'B19013_001E': 73194.0, 'B01003_001E': 76497.0, 'B01002_001E': 33.3, 'B19301_001E': 31524.0, 'B17001_002E': 9312.0, 'B23025_005E': 3694.0, 'state': '06', 'place': '80854'}, {'NAME': 'Union City city, California', 'B19013_001E': 82083.0, 'B01003_001E': 70687.0, 'B01002_001E': 36.5, 'B19301_001E': 29685.0, 'B17001_002E': 5905.0, 'B23025_005E': 3416.0, 'state': '06', 'place': '81204'}, {'NAME': 'Upland city, California', 'B19013_001E': 62667.0, 'B01003_001E': 74487.0, 'B01002_001E': 36.5, 'B19301_001E': 28604.0, 'B17001_002E': 9962.0, 'B23025_005E': 4155.0, 'state': '06', 'place': '81344'}, {'NAME': 'Vacaville city, California', 'B19013_001E': 73582.0, 'B01003_001E': 93137.0, 'B01002_001E': 37.5, 'B19301_001E': 29681.0, 'B17001_002E': 8382.0, 'B23025_005E': 4344.0, 'state': '06', 'place': '81554'}, {'NAME': 'Vallejo city, California', 'B19013_001E': 58371.0, 'B01003_001E': 117079.0, 'B01002_001E': 38.5, 'B19301_001E': 25996.0, 'B17001_002E': 20242.0, 'B23025_005E': 9664.0, 'state': '06', 'place': '81666'}, {'NAME': 'Victorville city, California', 'B19013_001E': 50034.0, 'B01003_001E': 117551.0, 'B01002_001E': 29.0, 'B19301_001E': 16477.0, 'B17001_002E': 28417.0, 'B23025_005E': 6979.0, 'state': '06', 'place': '82590'}, {'NAME': 'Visalia city, California', 'B19013_001E': 52899.0, 'B01003_001E': 125502.0, 'B01002_001E': 31.2, 'B19301_001E': 23144.0, 'B17001_002E': 23784.0, 'B23025_005E': 7021.0, 'state': '06', 'place': '82954'}, {'NAME': 'Vista city, California', 'B19013_001E': 47346.0, 'B01003_001E': 95066.0, 'B01002_001E': 33.9, 'B19301_001E': 21114.0, 'B17001_002E': 14917.0, 'B23025_005E': 3878.0, 'state': '06', 'place': '82996'}, {'NAME': 'West Covina city, California', 'B19013_001E': 67088.0, 'B01003_001E': 106731.0, 'B01002_001E': 35.7, 'B19301_001E': 24859.0, 'B17001_002E': 10590.0, 'B23025_005E': 7663.0, 'state': '06', 'place': '84200'}, {'NAME': 'Westminster city, California', 'B19013_001E': 52633.0, 'B01003_001E': 90625.0, 'B01002_001E': 39.0, 'B19301_001E': 22950.0, 'B17001_002E': 15083.0, 'B23025_005E': 5662.0, 'state': '06', 'place': '84550'}, {'NAME': 'Whittier city, California', 'B19013_001E': 68522.0, 'B01003_001E': 85832.0, 'B01002_001E': 34.9, 'B19301_001E': 28149.0, 'B17001_002E': 10466.0, 'B23025_005E': 3940.0, 'state': '06', 'place': '85292'}, {'NAME': 'Arvada city, Colorado', 'B19013_001E': 68210.0, 'B01003_001E': 108300.0, 'B01002_001E': 40.0, 'B19301_001E': 33204.0, 'B17001_002E': 9167.0, 'B23025_005E': 4691.0, 'state': '08', 'place': '03455'}, {'NAME': 'Aurora city, Colorado', 'B19013_001E': 50987.0, 'B01003_001E': 332820.0, 'B01002_001E': 33.3, 'B19301_001E': 24173.0, 'B17001_002E': 55124.0, 'B23025_005E': 19205.0, 'state': '08', 'place': '04000'}, {'NAME': 'Boulder city, Colorado', 'B19013_001E': 56312.0, 'B01003_001E': 100363.0, 'B01002_001E': 28.1, 'B19301_001E': 37286.0, 'B17001_002E': 20908.0, 'B23025_005E': 4616.0, 'state': '08', 'place': '07850'}, {'NAME': 'Centennial city, Colorado', 'B19013_001E': 89214.0, 'B01003_001E': 102625.0, 'B01002_001E': 41.1, 'B19301_001E': 41323.0, 'B17001_002E': 5287.0, 'B23025_005E': 3796.0, 'state': '08', 'place': '12815'}, {'NAME': 'Colorado Springs city, Colorado', 'B19013_001E': 53962.0, 'B01003_001E': 425805.0, 'B01002_001E': 34.6, 'B19301_001E': 29062.0, 'B17001_002E': 57453.0, 'B23025_005E': 21240.0, 'state': '08', 'place': '16000'}, {'NAME': 'Denver city, Colorado', 'B19013_001E': 50313.0, 'B01003_001E': 619297.0, 'B01002_001E': 33.8, 'B19301_001E': 33251.0, 'B17001_002E': 116284.0, 'B23025_005E': 30834.0, 'state': '08', 'place': '20000'}, {'NAME': 'Fort Collins city, Colorado', 'B19013_001E': 53780.0, 'B01003_001E': 146822.0, 'B01002_001E': 29.5, 'B19301_001E': 28729.0, 'B17001_002E': 25921.0, 'B23025_005E': 6902.0, 'state': '08', 'place': '27425'}, {'NAME': 'Greeley city, Colorado', 'B19013_001E': 46272.0, 'B01003_001E': 94194.0, 'B01002_001E': 30.5, 'B19301_001E': 21845.0, 'B17001_002E': 20314.0, 'B23025_005E': 4873.0, 'state': '08', 'place': '32155'}, {'NAME': 'Lakewood city, Colorado', 'B19013_001E': 56492.0, 'B01003_001E': 144530.0, 'B01002_001E': 38.8, 'B19301_001E': 31094.0, 'B17001_002E': 17969.0, 'B23025_005E': 7334.0, 'state': '08', 'place': '43000'}, {'NAME': 'Longmont city, Colorado', 'B19013_001E': 58698.0, 'B01003_001E': 87607.0, 'B01002_001E': 36.0, 'B19301_001E': 29209.0, 'B17001_002E': 12811.0, 'B23025_005E': 4019.0, 'state': '08', 'place': '45970'}, {'NAME': 'Loveland city, Colorado', 'B19013_001E': 54977.0, 'B01003_001E': 68712.0, 'B01002_001E': 37.7, 'B19301_001E': 27878.0, 'B17001_002E': 7135.0, 'B23025_005E': 3194.0, 'state': '08', 'place': '46465'}, {'NAME': 'Pueblo city, Colorado', 'B19013_001E': 34663.0, 'B01003_001E': 107429.0, 'B01002_001E': 37.7, 'B19301_001E': 20042.0, 'B17001_002E': 24612.0, 'B23025_005E': 6332.0, 'state': '08', 'place': '62000'}, {'NAME': 'Thornton city, Colorado', 'B19013_001E': 64525.0, 'B01003_001E': 121814.0, 'B01002_001E': 32.0, 'B19301_001E': 26228.0, 'B17001_002E': 11369.0, 'B23025_005E': 5172.0, 'state': '08', 'place': '77290'}, {'NAME': 'Westminster city, Colorado', 'B19013_001E': 64884.0, 'B01003_001E': 108042.0, 'B01002_001E': 35.3, 'B19301_001E': 31145.0, 'B17001_002E': 11360.0, 'B23025_005E': 5399.0, 'state': '08', 'place': '83835'}, {'NAME': 'Bridgeport city, Connecticut', 'B19013_001E': 41050.0, 'B01003_001E': 145587.0, 'B01002_001E': 32.3, 'B19301_001E': 20132.0, 'B17001_002E': 33015.0, 'B23025_005E': 12014.0, 'state': '09', 'place': '08000'}, {'NAME': 'Danbury city, Connecticut', 'B19013_001E': 64969.0, 'B01003_001E': 81967.0, 'B01002_001E': 36.3, 'B19301_001E': 30770.0, 'B17001_002E': 8293.0, 'B23025_005E': 4391.0, 'state': '09', 'place': '18430'}, {'NAME': 'Hartford city, Connecticut', 'B19013_001E': 29430.0, 'B01003_001E': 125130.0, 'B01002_001E': 30.1, 'B19301_001E': 16619.0, 'B17001_002E': 39452.0, 'B23025_005E': 12080.0, 'state': '09', 'place': '37000'}, {'NAME': 'New Britain city, Connecticut', 'B19013_001E': 40294.0, 'B01003_001E': 73112.0, 'B01002_001E': 33.8, 'B19301_001E': 20655.0, 'B17001_002E': 15658.0, 'B23025_005E': 5625.0, 'state': '09', 'place': '50370'}, {'NAME': 'New Haven city, Connecticut', 'B19013_001E': 37428.0, 'B01003_001E': 130338.0, 'B01002_001E': 30.4, 'B19301_001E': 23339.0, 'B17001_002E': 32135.0, 'B23025_005E': 9661.0, 'state': '09', 'place': '52000'}, {'NAME': 'Norwalk city, Connecticut', 'B19013_001E': 74728.0, 'B01003_001E': 86499.0, 'B01002_001E': 41.3, 'B19301_001E': 43767.0, 'B17001_002E': 8343.0, 'B23025_005E': 5041.0, 'state': '09', 'place': '55990'}, {'NAME': 'Stamford city, Connecticut', 'B19013_001E': 76779.0, 'B01003_001E': 123995.0, 'B01002_001E': 36.3, 'B19301_001E': 43647.0, 'B17001_002E': 13695.0, 'B23025_005E': 8118.0, 'state': '09', 'place': '73000'}, {'NAME': 'Waterbury city, Connecticut', 'B19013_001E': 40639.0, 'B01003_001E': 110052.0, 'B01002_001E': 35.1, 'B19301_001E': 21120.0, 'B17001_002E': 25247.0, 'B23025_005E': 7450.0, 'state': '09', 'place': '80000'}, {'NAME': 'Wilmington city, Delaware', 'B19013_001E': 38727.0, 'B01003_001E': 71143.0, 'B01002_001E': 34.4, 'B19301_001E': 25191.0, 'B17001_002E': 16381.0, 'B23025_005E': 4826.0, 'state': '10', 'place': '77580'}, {'NAME': 'Washington city, District of Columbia', 'B19013_001E': 65830.0, 'B01003_001E': 619371.0, 'B01002_001E': 33.8, 'B19301_001E': 45290.0, 'B17001_002E': 109200.0, 'B23025_005E': 38994.0, 'state': '11', 'place': '50000'}, {'NAME': 'Boca Raton city, Florida', 'B19013_001E': 70699.0, 'B01003_001E': 86671.0, 'B01002_001E': 45.8, 'B19301_001E': 47521.0, 'B17001_002E': 9304.0, 'B23025_005E': 4420.0, 'state': '12', 'place': '07300'}, {'NAME': 'Boynton Beach city, Florida', 'B19013_001E': 44390.0, 'B01003_001E': 69257.0, 'B01002_001E': 43.3, 'B19301_001E': 26145.0, 'B17001_002E': 12176.0, 'B23025_005E': 5341.0, 'state': '12', 'place': '07875'}, {'NAME': 'Cape Coral city, Florida', 'B19013_001E': 49170.0, 'B01003_001E': 158415.0, 'B01002_001E': 42.6, 'B19301_001E': 23270.0, 'B17001_002E': 22129.0, 'B23025_005E': 11315.0, 'state': '12', 'place': '10275'}, {'NAME': 'Clearwater city, Florida', 'B19013_001E': 42158.0, 'B01003_001E': 108551.0, 'B01002_001E': 44.5, 'B19301_001E': 28180.0, 'B17001_002E': 17507.0, 'B23025_005E': 5200.0, 'state': '12', 'place': '12875'}, {'NAME': 'Coral Springs city, Florida', 'B19013_001E': 64753.0, 'B01003_001E': 123476.0, 'B01002_001E': 36.5, 'B19301_001E': 29743.0, 'B17001_002E': 11984.0, 'B23025_005E': 8452.0, 'state': '12', 'place': '14400'}, {'NAME': 'Davie town, Florida', 'B19013_001E': 59345.0, 'B01003_001E': 93842.0, 'B01002_001E': 37.9, 'B19301_001E': 30790.0, 'B17001_002E': 11341.0, 'B23025_005E': 5020.0, 'state': '12', 'place': '16475'}, {'NAME': 'Deerfield Beach city, Florida', 'B19013_001E': 38353.0, 'B01003_001E': 76330.0, 'B01002_001E': 43.6, 'B19301_001E': 23510.0, 'B17001_002E': 14381.0, 'B23025_005E': 4303.0, 'state': '12', 'place': '16725'}, {'NAME': 'Deltona city, Florida', 'B19013_001E': 47049.0, 'B01003_001E': 85415.0, 'B01002_001E': 38.0, 'B19301_001E': 19893.0, 'B17001_002E': 12159.0, 'B23025_005E': 4781.0, 'state': '12', 'place': '17200'}, {'NAME': 'Fort Lauderdale city, Florida', 'B19013_001E': 49119.0, 'B01003_001E': 168603.0, 'B01002_001E': 42.3, 'B19301_001E': 35605.0, 'B17001_002E': 34269.0, 'B23025_005E': 11532.0, 'state': '12', 'place': '24000'}, {'NAME': 'Gainesville city, Florida', 'B19013_001E': 32492.0, 'B01003_001E': 125845.0, 'B01002_001E': 25.0, 'B19301_001E': 19616.0, 'B17001_002E': 38991.0, 'B23025_005E': 6092.0, 'state': '12', 'place': '25175'}, {'NAME': 'Hialeah city, Florida', 'B19013_001E': 29961.0, 'B01003_001E': 228943.0, 'B01002_001E': 42.6, 'B19301_001E': 14321.0, 'B17001_002E': 55681.0, 'B23025_005E': 15233.0, 'state': '12', 'place': '30000'}, {'NAME': 'Hollywood city, Florida', 'B19013_001E': 45585.0, 'B01003_001E': 143273.0, 'B01002_001E': 41.7, 'B19301_001E': 26069.0, 'B17001_002E': 21942.0, 'B23025_005E': 10295.0, 'state': '12', 'place': '32000'}, {'NAME': 'Jacksonville city, Florida', 'B19013_001E': 47557.0, 'B01003_001E': 829721.0, 'B01002_001E': 35.5, 'B19301_001E': 25374.0, 'B17001_002E': 140150.0, 'B23025_005E': 51141.0, 'state': '12', 'place': '35000'}, {'NAME': 'Lakeland city, Florida', 'B19013_001E': 39513.0, 'B01003_001E': 98970.0, 'B01002_001E': 40.3, 'B19301_001E': 22921.0, 'B17001_002E': 18223.0, 'B23025_005E': 6093.0, 'state': '12', 'place': '38250'}, {'NAME': 'Largo city, Florida', 'B19013_001E': 39735.0, 'B01003_001E': 77898.0, 'B01002_001E': 47.7, 'B19301_001E': 26364.0, 'B17001_002E': 11516.0, 'B23025_005E': 4933.0, 'state': '12', 'place': '39425'}, {'NAME': 'Lauderhill city, Florida', 'B19013_001E': 37074.0, 'B01003_001E': 68216.0, 'B01002_001E': 35.3, 'B19301_001E': 18557.0, 'B17001_002E': 15552.0, 'B23025_005E': 5965.0, 'state': '12', 'place': '39550'}, {'NAME': 'Melbourne city, Florida', 'B19013_001E': 40662.0, 'B01003_001E': 76768.0, 'B01002_001E': 44.8, 'B19301_001E': 24502.0, 'B17001_002E': 11548.0, 'B23025_005E': 5119.0, 'state': '12', 'place': '43975'}, {'NAME': 'Miami city, Florida', 'B19013_001E': 30375.0, 'B01003_001E': 407526.0, 'B01002_001E': 39.0, 'B19301_001E': 21120.0, 'B17001_002E': 119610.0, 'B23025_005E': 27530.0, 'state': '12', 'place': '45000'}, {'NAME': 'Miami Beach city, Florida', 'B19013_001E': 43316.0, 'B01003_001E': 89412.0, 'B01002_001E': 39.3, 'B19301_001E': 42085.0, 'B17001_002E': 14944.0, 'B23025_005E': 3056.0, 'state': '12', 'place': '45025'}, {'NAME': 'Miami Gardens city, Florida', 'B19013_001E': 42040.0, 'B01003_001E': 109150.0, 'B01002_001E': 33.6, 'B19301_001E': 16627.0, 'B17001_002E': 22878.0, 'B23025_005E': 8832.0, 'state': '12', 'place': '45060'}, {'NAME': 'Miramar city, Florida', 'B19013_001E': 62649.0, 'B01003_001E': 124900.0, 'B01002_001E': 33.9, 'B19301_001E': 24901.0, 'B17001_002E': 11903.0, 'B23025_005E': 8113.0, 'state': '12', 'place': '45975'}, {'NAME': 'Orlando city, Florida', 'B19013_001E': 42147.0, 'B01003_001E': 244931.0, 'B01002_001E': 32.8, 'B19301_001E': 25805.0, 'B17001_002E': 46177.0, 'B23025_005E': 16575.0, 'state': '12', 'place': '53000'}, {'NAME': 'Palm Bay city, Florida', 'B19013_001E': 43076.0, 'B01003_001E': 103602.0, 'B01002_001E': 40.2, 'B19301_001E': 20467.0, 'B17001_002E': 18989.0, 'B23025_005E': 6574.0, 'state': '12', 'place': '54000'}, {'NAME': 'Palm Coast city, Florida', 'B19013_001E': 47099.0, 'B01003_001E': 76455.0, 'B01002_001E': 46.1, 'B19301_001E': 22651.0, 'B17001_002E': 13363.0, 'B23025_005E': 3754.0, 'state': '12', 'place': '54200'}, {'NAME': 'Pembroke Pines city, Florida', 'B19013_001E': 62116.0, 'B01003_001E': 157324.0, 'B01002_001E': 39.9, 'B19301_001E': 28539.0, 'B17001_002E': 12884.0, 'B23025_005E': 8683.0, 'state': '12', 'place': '55775'}, {'NAME': 'Plantation city, Florida', 'B19013_001E': 65567.0, 'B01003_001E': 86999.0, 'B01002_001E': 40.8, 'B19301_001E': 35163.0, 'B17001_002E': 7866.0, 'B23025_005E': 4109.0, 'state': '12', 'place': '57425'}, {'NAME': 'Pompano Beach city, Florida', 'B19013_001E': 40221.0, 'B01003_001E': 101749.0, 'B01002_001E': 42.4, 'B19301_001E': 25559.0, 'B17001_002E': 22105.0, 'B23025_005E': 7172.0, 'state': '12', 'place': '58050'}, {'NAME': 'Port St. Lucie city, Florida', 'B19013_001E': 48962.0, 'B01003_001E': 166641.0, 'B01002_001E': 39.7, 'B19301_001E': 22810.0, 'B17001_002E': 26759.0, 'B23025_005E': 12607.0, 'state': '12', 'place': '58715'}, {'NAME': 'St. Petersburg city, Florida', 'B19013_001E': 45044.0, 'B01003_001E': 246642.0, 'B01002_001E': 41.8, 'B19301_001E': 27972.0, 'B17001_002E': 40714.0, 'B23025_005E': 15066.0, 'state': '12', 'place': '63000'}, {'NAME': 'Sunrise city, Florida', 'B19013_001E': 48642.0, 'B01003_001E': 86834.0, 'B01002_001E': 38.7, 'B19301_001E': 23524.0, 'B17001_002E': 10937.0, 'B23025_005E': 4959.0, 'state': '12', 'place': '69700'}, {'NAME': 'Tallahassee city, Florida', 'B19013_001E': 39524.0, 'B01003_001E': 183638.0, 'B01002_001E': 26.1, 'B19301_001E': 23778.0, 'B17001_002E': 51478.0, 'B23025_005E': 13292.0, 'state': '12', 'place': '70600'}, {'NAME': 'Tampa city, Florida', 'B19013_001E': 43242.0, 'B01003_001E': 343768.0, 'B01002_001E': 34.8, 'B19301_001E': 29009.0, 'B17001_002E': 71191.0, 'B23025_005E': 22413.0, 'state': '12', 'place': '71000'}, {'NAME': 'West Palm Beach city, Florida', 'B19013_001E': 44897.0, 'B01003_001E': 100778.0, 'B01002_001E': 39.9, 'B19301_001E': 29955.0, 'B17001_002E': 19025.0, 'B23025_005E': 5982.0, 'state': '12', 'place': '76600'}, {'NAME': 'Albany city, Georgia', 'B19013_001E': 28717.0, 'B01003_001E': 77196.0, 'B01002_001E': 31.6, 'B19301_001E': 16731.0, 'B17001_002E': 25305.0, 'B23025_005E': 6160.0, 'state': '13', 'place': '01052'}, {'NAME': 'Athens-Clarke County unified government (balance), Georgia', 'B19013_001E': 32853.0, 'B01003_001E': 117749.0, 'B01002_001E': 26.1, 'B19301_001E': 19199.0, 'B17001_002E': 39552.0, 'B23025_005E': 5193.0, 'state': '13', 'place': '03440'}, {'NAME': 'Atlanta city, Georgia', 'B19013_001E': 46631.0, 'B01003_001E': 432589.0, 'B01002_001E': 33.2, 'B19301_001E': 35890.0, 'B17001_002E': 101369.0, 'B23025_005E': 31054.0, 'state': '13', 'place': '04000'}, {'NAME': 'Augusta-Richmond County consolidated government (balance), Georgia', 'B19013_001E': 37560.0, 'B01003_001E': 196395.0, 'B01002_001E': 33.1, 'B19301_001E': 20555.0, 'B17001_002E': 47815.0, 'B23025_005E': 11442.0, 'state': '13', 'place': '04204'}, {'NAME': 'Columbus city, Georgia', 'B19013_001E': 41339.0, 'B01003_001E': 194949.0, 'B01002_001E': 33.3, 'B19301_001E': 22856.0, 'B17001_002E': 35819.0, 'B23025_005E': 10050.0, 'state': '13', 'place': '19000'}, {'NAME': 'Johns Creek city, Georgia', 'B19013_001E': 109224.0, 'B01003_001E': 79352.0, 'B01002_001E': 37.9, 'B19301_001E': 43790.0, 'B17001_002E': 3925.0, 'B23025_005E': 3021.0, 'state': '13', 'place': '42425'}, {'NAME': 'Macon city, Georgia', 'B19013_001E': 25773.0, 'B01003_001E': 91316.0, 'B01002_001E': 33.2, 'B19301_001E': 16051.0, 'B17001_002E': 30230.0, 'B23025_005E': 6171.0, 'state': '13', 'place': '49000'}, {'NAME': 'Roswell city, Georgia', 'B19013_001E': 79579.0, 'B01003_001E': 90959.0, 'B01002_001E': 38.9, 'B19301_001E': 41875.0, 'B17001_002E': 8170.0, 'B23025_005E': 3861.0, 'state': '13', 'place': '67284'}, {'NAME': 'Sandy Springs city, Georgia', 'B19013_001E': 63134.0, 'B01003_001E': 96584.0, 'B01002_001E': 35.2, 'B19301_001E': 49964.0, 'B17001_002E': 11935.0, 'B23025_005E': 4251.0, 'state': '13', 'place': '68516'}, {'NAME': 'Savannah city, Georgia', 'B19013_001E': 35838.0, 'B01003_001E': 139620.0, 'B01002_001E': 31.6, 'B19301_001E': 19900.0, 'B17001_002E': 34417.0, 'B23025_005E': 8039.0, 'state': '13', 'place': '69000'}, {'NAME': 'Warner Robins city, Georgia', 'B19013_001E': 44964.0, 'B01003_001E': 69695.0, 'B01002_001E': 31.1, 'B19301_001E': 21194.0, 'B17001_002E': 14112.0, 'B23025_005E': 4028.0, 'state': '13', 'place': '80508'}, {'NAME': 'Warner Robins city, Georgia', 'B19013_001E': 44964.0, 'B01003_001E': 69695.0, 'B01002_001E': 31.1, 'B19301_001E': 21194.0, 'B17001_002E': 14112.0, 'B23025_005E': 4028.0, 'state': '13', 'place': '80508'}, {'NAME': 'Boise City city, Idaho', 'B19013_001E': 48524.0, 'B01003_001E': 209726.0, 'B01002_001E': 35.8, 'B19301_001E': 27978.0, 'B17001_002E': 32129.0, 'B23025_005E': 10134.0, 'state': '16', 'place': '08830'}, {'NAME': 'Meridian city, Idaho', 'B19013_001E': 63571.0, 'B01003_001E': 78061.0, 'B01002_001E': 33.4, 'B19301_001E': 26377.0, 'B17001_002E': 6492.0, 'B23025_005E': 3445.0, 'state': '16', 'place': '52120'}, {'NAME': 'Nampa city, Idaho', 'B19013_001E': 40244.0, 'B01003_001E': 83140.0, 'B01002_001E': 30.3, 'B19301_001E': 16813.0, 'B17001_002E': 19398.0, 'B23025_005E': 4640.0, 'state': '16', 'place': '56260'}, {'NAME': 'Arlington Heights village, Illinois', 'B19013_001E': 77195.0, 'B01003_001E': 75492.0, 'B01002_001E': 41.9, 'B19301_001E': 40189.0, 'B17001_002E': 3143.0, 'B23025_005E': 2875.0, 'state': '17', 'place': '02154'}, {'NAME': 'Aurora city, Illinois', 'B19013_001E': 62493.0, 'B01003_001E': 198726.0, 'B01002_001E': 31.5, 'B19301_001E': 26221.0, 'B17001_002E': 27731.0, 'B23025_005E': 11164.0, 'state': '17', 'place': '03012'}, {'NAME': 'Bloomington city, Illinois', 'B19013_001E': 61664.0, 'B01003_001E': 77293.0, 'B01002_001E': 33.8, 'B19301_001E': 33267.0, 'B17001_002E': 8923.0, 'B23025_005E': 2962.0, 'state': '17', 'place': '06613'}, {'NAME': 'Bolingbrook village, Illinois', 'B19013_001E': 80421.0, 'B01003_001E': 73799.0, 'B01002_001E': 33.5, 'B19301_001E': 27746.0, 'B17001_002E': 6192.0, 'B23025_005E': 3673.0, 'state': '17', 'place': '07133'}, {'NAME': 'Champaign city, Illinois', 'B19013_001E': 40884.0, 'B01003_001E': 81925.0, 'B01002_001E': 26.7, 'B19301_001E': 24733.0, 'B17001_002E': 19555.0, 'B23025_005E': 3418.0, 'state': '17', 'place': '12385'}, {'NAME': 'Chicago city, Illinois', 'B19013_001E': 47270.0, 'B01003_001E': 2706101.0, 'B01002_001E': 33.3, 'B19301_001E': 28436.0, 'B17001_002E': 601378.0, 'B23025_005E': 194493.0, 'state': '17', 'place': '14000'}, {'NAME': 'Cicero town, Illinois', 'B19013_001E': 44177.0, 'B01003_001E': 83930.0, 'B01002_001E': 28.1, 'B19301_001E': 14745.0, 'B17001_002E': 16422.0, 'B23025_005E': 5543.0, 'state': '17', 'place': '14351'}, {'NAME': 'Decatur city, Illinois', 'B19013_001E': 39514.0, 'B01003_001E': 75982.0, 'B01002_001E': 38.9, 'B19301_001E': 23130.0, 'B17001_002E': 16737.0, 'B23025_005E': 4969.0, 'state': '17', 'place': '18823'}, {'NAME': 'Elgin city, Illinois', 'B19013_001E': 58675.0, 'B01003_001E': 109825.0, 'B01002_001E': 32.7, 'B19301_001E': 23453.0, 'B17001_002E': 14833.0, 'B23025_005E': 6137.0, 'state': '17', 'place': '23074'}, {'NAME': 'Evanston city, Illinois', 'B19013_001E': 67038.0, 'B01003_001E': 74937.0, 'B01002_001E': 34.6, 'B19301_001E': 41284.0, 'B17001_002E': 8829.0, 'B23025_005E': 3387.0, 'state': '17', 'place': '24582'}, {'NAME': 'Joliet city, Illinois', 'B19013_001E': 61744.0, 'B01003_001E': 147459.0, 'B01002_001E': 32.4, 'B19301_001E': 24118.0, 'B17001_002E': 17490.0, 'B23025_005E': 9151.0, 'state': '17', 'place': '38570'}, {'NAME': 'Naperville city, Illinois', 'B19013_001E': 108302.0, 'B01003_001E': 143223.0, 'B01002_001E': 38.2, 'B19301_001E': 46064.0, 'B17001_002E': 5790.0, 'B23025_005E': 5518.0, 'state': '17', 'place': '51622'}, {'NAME': 'Palatine village, Illinois', 'B19013_001E': 72818.0, 'B01003_001E': 68738.0, 'B01002_001E': 36.5, 'B19301_001E': 35407.0, 'B17001_002E': 6568.0, 'B23025_005E': 2993.0, 'state': '17', 'place': '57225'}, {'NAME': 'Peoria city, Illinois', 'B19013_001E': 45270.0, 'B01003_001E': 115466.0, 'B01002_001E': 33.3, 'B19301_001E': 27781.0, 'B17001_002E': 24975.0, 'B23025_005E': 5776.0, 'state': '17', 'place': '59000'}, {'NAME': 'Rockford city, Illinois', 'B19013_001E': 38067.0, 'B01003_001E': 152138.0, 'B01002_001E': 35.8, 'B19301_001E': 21570.0, 'B17001_002E': 37857.0, 'B23025_005E': 11256.0, 'state': '17', 'place': '65000'}, {'NAME': 'Schaumburg village, Illinois', 'B19013_001E': 70798.0, 'B01003_001E': 74292.0, 'B01002_001E': 37.3, 'B19301_001E': 35433.0, 'B17001_002E': 4492.0, 'B23025_005E': 3275.0, 'state': '17', 'place': '68003'}, {'NAME': 'Springfield city, Illinois', 'B19013_001E': 49317.0, 'B01003_001E': 116495.0, 'B01002_001E': 38.4, 'B19301_001E': 29016.0, 'B17001_002E': 19972.0, 'B23025_005E': 5748.0, 'state': '17', 'place': '72000'}, {'NAME': 'Waukegan city, Illinois', 'B19013_001E': 46469.0, 'B01003_001E': 88560.0, 'B01002_001E': 30.8, 'B19301_001E': 20226.0, 'B17001_002E': 16637.0, 'B23025_005E': 5465.0, 'state': '17', 'place': '79293'}, {'NAME': 'Bloomington city, Indiana', 'B19013_001E': 27395.0, 'B01003_001E': 81115.0, 'B01002_001E': 23.3, 'B19301_001E': 18987.0, 'B17001_002E': 26237.0, 'B23025_005E': 3242.0, 'state': '18', 'place': '05860'}, {'NAME': 'Carmel city, Indiana', 'B19013_001E': 106121.0, 'B01003_001E': 81756.0, 'B01002_001E': 38.7, 'B19301_001E': 51767.0, 'B17001_002E': 2904.0, 'B23025_005E': 2325.0, 'state': '18', 'place': '10342'}, {'NAME': 'Evansville city, Indiana', 'B19013_001E': 35839.0, 'B01003_001E': 119677.0, 'B01002_001E': 36.3, 'B19301_001E': 20984.0, 'B17001_002E': 23230.0, 'B23025_005E': 5046.0, 'state': '18', 'place': '22000'}, {'NAME': 'Fishers town, Indiana', 'B19013_001E': 90437.0, 'B01003_001E': 78927.0, 'B01002_001E': 33.8, 'B19301_001E': 38577.0, 'B17001_002E': 2617.0, 'B23025_005E': 2147.0, 'state': '18', 'place': '23278'}, {'NAME': 'Fort Wayne city, Indiana', 'B19013_001E': 43969.0, 'B01003_001E': 254435.0, 'B01002_001E': 34.7, 'B19301_001E': 23400.0, 'B17001_002E': 46591.0, 'B23025_005E': 14097.0, 'state': '18', 'place': '25000'}, {'NAME': 'Gary city, Indiana', 'B19013_001E': 26885.0, 'B01003_001E': 79922.0, 'B01002_001E': 37.9, 'B19301_001E': 15931.0, 'B17001_002E': 30163.0, 'B23025_005E': 6359.0, 'state': '18', 'place': '27000'}, {'NAME': 'Hammond city, Indiana', 'B19013_001E': 38365.0, 'B01003_001E': 80122.0, 'B01002_001E': 33.2, 'B19301_001E': 17920.0, 'B17001_002E': 18143.0, 'B23025_005E': 5137.0, 'state': '18', 'place': '31000'}, {'NAME': 'Indianapolis city (balance), Indiana', 'B19013_001E': 41962.0, 'B01003_001E': 828841.0, 'B01002_001E': 33.8, 'B19301_001E': 24012.0, 'B17001_002E': 169696.0, 'B23025_005E': 52063.0, 'state': '18', 'place': '36003'}, {'NAME': 'Lafayette city, Indiana', 'B19013_001E': 39345.0, 'B01003_001E': 69181.0, 'B01002_001E': 31.3, 'B19301_001E': 21646.0, 'B17001_002E': 13341.0, 'B23025_005E': 3792.0, 'state': '18', 'place': '40788'}, {'NAME': 'Muncie city, Indiana', 'B19013_001E': 29287.0, 'B01003_001E': 69989.0, 'B01002_001E': 27.7, 'B19301_001E': 17066.0, 'B17001_002E': 20847.0, 'B23025_005E': 5173.0, 'state': '18', 'place': '51876'}, {'NAME': 'South Bend city, Indiana', 'B19013_001E': 34502.0, 'B01003_001E': 100863.0, 'B01002_001E': 33.9, 'B19301_001E': 19181.0, 'B17001_002E': 27504.0, 'B23025_005E': 7612.0, 'state': '18', 'place': '71000'}, {'NAME': 'Cedar Rapids city, Iowa', 'B19013_001E': 52216.0, 'B01003_001E': 127420.0, 'B01002_001E': 35.6, 'B19301_001E': 28458.0, 'B17001_002E': 14688.0, 'B23025_005E': 4447.0, 'state': '19', 'place': '12000'}, {'NAME': 'Davenport city, Iowa', 'B19013_001E': 44817.0, 'B01003_001E': 100564.0, 'B01002_001E': 34.9, 'B19301_001E': 24499.0, 'B17001_002E': 17629.0, 'B23025_005E': 3521.0, 'state': '19', 'place': '19000'}, {'NAME': 'Des Moines city, Iowa', 'B19013_001E': 45836.0, 'B01003_001E': 205415.0, 'B01002_001E': 33.5, 'B19301_001E': 23928.0, 'B17001_002E': 36942.0, 'B23025_005E': 9636.0, 'state': '19', 'place': '21000'}, {'NAME': 'Iowa City city, Iowa', 'B19013_001E': 41410.0, 'B01003_001E': 69314.0, 'B01002_001E': 25.6, 'B19301_001E': 25671.0, 'B17001_002E': 17618.0, 'B23025_005E': 2209.0, 'state': '19', 'place': '38595'}, {'NAME': 'Sioux City city, Iowa', 'B19013_001E': 43449.0, 'B01003_001E': 82602.0, 'B01002_001E': 34.4, 'B19301_001E': 22143.0, 'B17001_002E': 13512.0, 'B23025_005E': 2652.0, 'state': '19', 'place': '73335'}, {'NAME': 'Waterloo city, Iowa', 'B19013_001E': 40498.0, 'B01003_001E': 68327.0, 'B01002_001E': 35.5, 'B19301_001E': 22010.0, 'B17001_002E': 13155.0, 'B23025_005E': 3488.0, 'state': '19', 'place': '82425'}, {'NAME': 'Kansas City city, Kansas', 'B19013_001E': 38293.0, 'B01003_001E': 146581.0, 'B01002_001E': 33.0, 'B19301_001E': 18574.0, 'B17001_002E': 36466.0, 'B23025_005E': 9821.0, 'state': '20', 'place': '36000'}, {'NAME': 'Lawrence city, Kansas', 'B19013_001E': 45574.0, 'B01003_001E': 88921.0, 'B01002_001E': 26.2, 'B19301_001E': 25322.0, 'B17001_002E': 17947.0, 'B23025_005E': 3776.0, 'state': '20', 'place': '38900'}, {'NAME': 'Olathe city, Kansas', 'B19013_001E': 76379.0, 'B01003_001E': 128050.0, 'B01002_001E': 33.6, 'B19301_001E': 31557.0, 'B17001_002E': 9146.0, 'B23025_005E': 4221.0, 'state': '20', 'place': '52575'}, {'NAME': 'Overland Park city, Kansas', 'B19013_001E': 71094.0, 'B01003_001E': 176520.0, 'B01002_001E': 37.8, 'B19301_001E': 39701.0, 'B17001_002E': 10184.0, 'B23025_005E': 5151.0, 'state': '20', 'place': '53775'}, {'NAME': 'Topeka city, Kansas', 'B19013_001E': 40826.0, 'B01003_001E': 127625.0, 'B01002_001E': 35.9, 'B19301_001E': 23641.0, 'B17001_002E': 26217.0, 'B23025_005E': 5964.0, 'state': '20', 'place': '71000'}, {'NAME': 'Wichita city, Kansas', 'B19013_001E': 46011.0, 'B01003_001E': 383703.0, 'B01002_001E': 34.0, 'B19301_001E': 24766.0, 'B17001_002E': 66412.0, 'B23025_005E': 18822.0, 'state': '20', 'place': '79000'}, {'NAME': 'Lexington-Fayette urban county, Kentucky', 'B19013_001E': 48398.0, 'B01003_001E': 300843.0, 'B01002_001E': 33.9, 'B19301_001E': 29251.0, 'B17001_002E': 54459.0, 'B23025_005E': 13662.0, 'state': '21', 'place': '46027'}, {'NAME': 'Louisville/Jefferson County metro government (balance), Kentucky', 'B19013_001E': 44159.0, 'B01003_001E': 601611.0, 'B01002_001E': 37.4, 'B19301_001E': 26098.0, 'B17001_002E': 108300.0, 'B23025_005E': 34583.0, 'state': '21', 'place': '48006'}, {'NAME': 'Baton Rouge city, Louisiana', 'B19013_001E': 38593.0, 'B01003_001E': 229400.0, 'B01002_001E': 30.6, 'B19301_001E': 23949.0, 'B17001_002E': 55941.0, 'B23025_005E': 11974.0, 'state': '22', 'place': '05000'}, {'NAME': 'Kenner city, Louisiana', 'B19013_001E': 48750.0, 'B01003_001E': 66820.0, 'B01002_001E': 38.6, 'B19301_001E': 26074.0, 'B17001_002E': 9809.0, 'B23025_005E': 3195.0, 'state': '22', 'place': '39475'}, {'NAME': 'Lafayette city, Louisiana', 'B19013_001E': 46288.0, 'B01003_001E': 122009.0, 'B01002_001E': 34.2, 'B19301_001E': 28451.0, 'B17001_002E': 23045.0, 'B23025_005E': 4226.0, 'state': '22', 'place': '40735'}, {'NAME': 'Lake Charles city, Louisiana', 'B19013_001E': 35981.0, 'B01003_001E': 72826.0, 'B01002_001E': 35.1, 'B19301_001E': 23447.0, 'B17001_002E': 15073.0, 'B23025_005E': 4037.0, 'state': '22', 'place': '41155'}, {'NAME': 'New Orleans city, Louisiana', 'B19013_001E': 37146.0, 'B01003_001E': 357013.0, 'B01002_001E': 35.0, 'B19301_001E': 26500.0, 'B17001_002E': 94602.0, 'B23025_005E': 21671.0, 'state': '22', 'place': '55000'}, {'NAME': 'Shreveport city, Louisiana', 'B19013_001E': 38633.0, 'B01003_001E': 200715.0, 'B01002_001E': 34.6, 'B19301_001E': 23995.0, 'B17001_002E': 42203.0, 'B23025_005E': 8473.0, 'state': '22', 'place': '70000'}, {'NAME': 'Portland city, Maine', 'B19013_001E': 44458.0, 'B01003_001E': 66227.0, 'B01002_001E': 37.0, 'B19301_001E': 28913.0, 'B17001_002E': 13350.0, 'B23025_005E': 2996.0, 'state': '23', 'place': '60545'}, {'NAME': 'Baltimore city, Maryland', 'B19013_001E': 41385.0, 'B01003_001E': 621445.0, 'B01002_001E': 34.5, 'B19301_001E': 24750.0, 'B17001_002E': 142162.0, 'B23025_005E': 43471.0, 'state': '24', 'place': '04000'}, {'NAME': 'Boston city, Massachusetts', 'B19013_001E': 53601.0, 'B01003_001E': 629182.0, 'B01002_001E': 31.1, 'B19301_001E': 33964.0, 'B17001_002E': 126226.0, 'B23025_005E': 39142.0, 'state': '25', 'place': '07000'}, {'NAME': 'Brockton city, Massachusetts', 'B19013_001E': 49025.0, 'B01003_001E': 93911.0, 'B01002_001E': 35.6, 'B19301_001E': 21942.0, 'B17001_002E': 16559.0, 'B23025_005E': 7487.0, 'state': '25', 'place': '09000'}, {'NAME': 'Cambridge city, Massachusetts', 'B19013_001E': 72529.0, 'B01003_001E': 105737.0, 'B01002_001E': 30.8, 'B19301_001E': 47448.0, 'B17001_002E': 13430.0, 'B23025_005E': 3874.0, 'state': '25', 'place': '11000'}, {'NAME': 'Fall River city, Massachusetts', 'B19013_001E': 33211.0, 'B01003_001E': 88811.0, 'B01002_001E': 38.7, 'B19301_001E': 21257.0, 'B17001_002E': 20397.0, 'B23025_005E': 7191.0, 'state': '25', 'place': '23000'}, {'NAME': 'Lawrence city, Massachusetts', 'B19013_001E': 32851.0, 'B01003_001E': 76820.0, 'B01002_001E': 30.9, 'B19301_001E': 16987.0, 'B17001_002E': 22150.0, 'B23025_005E': 4605.0, 'state': '25', 'place': '34550'}, {'NAME': 'Lowell city, Massachusetts', 'B19013_001E': 49452.0, 'B01003_001E': 107466.0, 'B01002_001E': 32.9, 'B19301_001E': 23136.0, 'B17001_002E': 19670.0, 'B23025_005E': 6638.0, 'state': '25', 'place': '37000'}, {'NAME': 'Lynn city, Massachusetts', 'B19013_001E': 44849.0, 'B01003_001E': 90788.0, 'B01002_001E': 34.2, 'B19301_001E': 22982.0, 'B17001_002E': 18914.0, 'B23025_005E': 5079.0, 'state': '25', 'place': '37490'}, {'NAME': 'New Bedford city, Massachusetts', 'B19013_001E': 35999.0, 'B01003_001E': 94927.0, 'B01002_001E': 36.9, 'B19301_001E': 21056.0, 'B17001_002E': 21828.0, 'B23025_005E': 6268.0, 'state': '25', 'place': '45000'}, {'NAME': 'Newton city, Massachusetts', 'B19013_001E': 119148.0, 'B01003_001E': 86241.0, 'B01002_001E': 40.1, 'B19301_001E': 63872.0, 'B17001_002E': 4504.0, 'B23025_005E': 2732.0, 'state': '25', 'place': '45560'}, {'NAME': 'Quincy city, Massachusetts', 'B19013_001E': 61328.0, 'B01003_001E': 92595.0, 'B01002_001E': 38.4, 'B19301_001E': 33131.0, 'B17001_002E': 9626.0, 'B23025_005E': 5649.0, 'state': '25', 'place': '55745'}, {'NAME': 'Somerville city, Massachusetts', 'B19013_001E': 67118.0, 'B01003_001E': 76945.0, 'B01002_001E': 31.3, 'B19301_001E': 34781.0, 'B17001_002E': 10989.0, 'B23025_005E': 3576.0, 'state': '25', 'place': '62535'}, {'NAME': 'Springfield city, Massachusetts', 'B19013_001E': 34311.0, 'B01003_001E': 153428.0, 'B01002_001E': 32.2, 'B19301_001E': 18133.0, 'B17001_002E': 43397.0, 'B23025_005E': 10082.0, 'state': '25', 'place': '67000'}, {'NAME': 'Worcester city, Massachusetts', 'B19013_001E': 45932.0, 'B01003_001E': 181901.0, 'B01002_001E': 33.6, 'B19301_001E': 24330.0, 'B17001_002E': 36635.0, 'B23025_005E': 10278.0, 'state': '25', 'place': '82000'}, {'NAME': 'Ann Arbor city, Michigan', 'B19013_001E': 55003.0, 'B01003_001E': 115331.0, 'B01002_001E': 27.5, 'B19301_001E': 34247.0, 'B17001_002E': 22914.0, 'B23025_005E': 4718.0, 'state': '26', 'place': '03000'}, {'NAME': 'Dearborn city, Michigan', 'B19013_001E': 46739.0, 'B01003_001E': 97140.0, 'B01002_001E': 33.2, 'B19301_001E': 21262.0, 'B17001_002E': 26611.0, 'B23025_005E': 4802.0, 'state': '26', 'place': '21000'}, {'NAME': 'Detroit city, Michigan', 'B19013_001E': 26325.0, 'B01003_001E': 706663.0, 'B01002_001E': 34.9, 'B19301_001E': 14870.0, 'B17001_002E': 273850.0, 'B23025_005E': 83031.0, 'state': '26', 'place': '22000'}, {'NAME': 'Farmington Hills city, Michigan', 'B19013_001E': 69700.0, 'B01003_001E': 80376.0, 'B01002_001E': 42.7, 'B19301_001E': 40604.0, 'B17001_002E': 5927.0, 'B23025_005E': 2884.0, 'state': '26', 'place': '27440'}, {'NAME': 'Flint city, Michigan', 'B19013_001E': 24834.0, 'B01003_001E': 101649.0, 'B01002_001E': 34.3, 'B19301_001E': 14360.0, 'B17001_002E': 41286.0, 'B23025_005E': 10477.0, 'state': '26', 'place': '29000'}, {'NAME': 'Troy city, Michigan', 'B19013_001E': 85685.0, 'B01003_001E': 81700.0, 'B01002_001E': 41.1, 'B19301_001E': 40022.0, 'B17001_002E': 5841.0, 'B23025_005E': 3580.0, 'state': '26', 'place': '80700'}, {'NAME': 'Grand Rapids city, Michigan', 'B19013_001E': 39227.0, 'B01003_001E': 189735.0, 'B01002_001E': 31.0, 'B19301_001E': 20214.0, 'B17001_002E': 49016.0, 'B23025_005E': 12920.0, 'state': '26', 'place': '34000'}, {'NAME': 'Kalamazoo city, Michigan', 'B19013_001E': 31893.0, 'B01003_001E': 74812.0, 'B01002_001E': 25.9, 'B19301_001E': 18468.0, 'B17001_002E': 23205.0, 'B23025_005E': 5628.0, 'state': '26', 'place': '42160'}, {'NAME': 'Lansing city, Michigan', 'B19013_001E': 36054.0, 'B01003_001E': 114274.0, 'B01002_001E': 32.0, 'B19301_001E': 19440.0, 'B17001_002E': 32642.0, 'B23025_005E': 8937.0, 'state': '26', 'place': '46000'}, {'NAME': 'Livonia city, Michigan', 'B19013_001E': 68973.0, 'B01003_001E': 96233.0, 'B01002_001E': 44.2, 'B19301_001E': 32249.0, 'B17001_002E': 5780.0, 'B23025_005E': 4360.0, 'state': '26', 'place': '49000'}, {'NAME': 'Rochester Hills city, Michigan', 'B19013_001E': 78160.0, 'B01003_001E': 71737.0, 'B01002_001E': 41.3, 'B19301_001E': 38892.0, 'B17001_002E': 4715.0, 'B23025_005E': 3248.0, 'state': '26', 'place': '69035'}, {'NAME': 'Southfield city, Michigan', 'B19013_001E': 49841.0, 'B01003_001E': 72331.0, 'B01002_001E': 42.3, 'B19301_001E': 28635.0, 'B17001_002E': 11379.0, 'B23025_005E': 5091.0, 'state': '26', 'place': '74900'}, {'NAME': 'Sterling Heights city, Michigan', 'B19013_001E': 57075.0, 'B01003_001E': 130209.0, 'B01002_001E': 40.8, 'B19301_001E': 26691.0, 'B17001_002E': 16784.0, 'B23025_005E': 8017.0, 'state': '26', 'place': '76460'}, {'NAME': 'Warren city, Michigan', 'B19013_001E': 43962.0, 'B01003_001E': 134376.0, 'B01002_001E': 39.4, 'B19301_001E': 21744.0, 'B17001_002E': 24228.0, 'B23025_005E': 9739.0, 'state': '26', 'place': '84000'}, {'NAME': 'Westland city, Michigan', 'B19013_001E': 43993.0, 'B01003_001E': 83476.0, 'B01002_001E': 38.4, 'B19301_001E': 23993.0, 'B17001_002E': 12822.0, 'B23025_005E': 5778.0, 'state': '26', 'place': '86000'}, {'NAME': 'Wyoming city, Michigan', 'B19013_001E': 45477.0, 'B01003_001E': 72864.0, 'B01002_001E': 32.8, 'B19301_001E': 21246.0, 'B17001_002E': 12106.0, 'B23025_005E': 4549.0, 'state': '26', 'place': '88940'}, {'NAME': 'Bloomington city, Minnesota', 'B19013_001E': 61820.0, 'B01003_001E': 84451.0, 'B01002_001E': 42.3, 'B19301_001E': 35874.0, 'B17001_002E': 8529.0, 'B23025_005E': 3742.0, 'state': '27', 'place': '06616'}, {'NAME': 'Brooklyn Park city, Minnesota', 'B19013_001E': 64113.0, 'B01003_001E': 76781.0, 'B01002_001E': 32.7, 'B19301_001E': 26917.0, 'B17001_002E': 9427.0, 'B23025_005E': 3891.0, 'state': '27', 'place': '07966'}, {'NAME': 'Duluth city, Minnesota', 'B19013_001E': 43064.0, 'B01003_001E': 86234.0, 'B01002_001E': 32.8, 'B19301_001E': 24926.0, 'B17001_002E': 17773.0, 'B23025_005E': 3941.0, 'state': '27', 'place': '17000'}, {'NAME': 'Minneapolis city, Minnesota', 'B19013_001E': 49885.0, 'B01003_001E': 389112.0, 'B01002_001E': 31.6, 'B19301_001E': 31281.0, 'B17001_002E': 84076.0, 'B23025_005E': 22342.0, 'state': '27', 'place': '43000'}, {'NAME': 'Plymouth city, Minnesota', 'B19013_001E': 84392.0, 'B01003_001E': 71852.0, 'B01002_001E': 40.0, 'B19301_001E': 46948.0, 'B17001_002E': 3855.0, 'B23025_005E': 2231.0, 'state': '27', 'place': '51730'}, {'NAME': 'Rochester city, Minnesota', 'B19013_001E': 62575.0, 'B01003_001E': 108179.0, 'B01002_001E': 35.2, 'B19301_001E': 32887.0, 'B17001_002E': 9796.0, 'B23025_005E': 2645.0, 'state': '27', 'place': '54880'}, {'NAME': 'St. Paul city, Minnesota', 'B19013_001E': 47010.0, 'B01003_001E': 288802.0, 'B01002_001E': 31.0, 'B19301_001E': 25695.0, 'B17001_002E': 64676.0, 'B23025_005E': 15702.0, 'state': '27', 'place': '58000'}, {'NAME': 'Gulfport city, Mississippi', 'B19013_001E': 37610.0, 'B01003_001E': 69004.0, 'B01002_001E': 34.3, 'B19301_001E': 20863.0, 'B17001_002E': 16480.0, 'B23025_005E': 3818.0, 'state': '28', 'place': '29700'}, {'NAME': 'Jackson city, Mississippi', 'B19013_001E': 32708.0, 'B01003_001E': 173997.0, 'B01002_001E': 31.6, 'B19301_001E': 18623.0, 'B17001_002E': 50577.0, 'B23025_005E': 10547.0, 'state': '28', 'place': '36000'}, {'NAME': 'Columbia city, Missouri', 'B19013_001E': 43262.0, 'B01003_001E': 111145.0, 'B01002_001E': 26.6, 'B19301_001E': 26110.0, 'B17001_002E': 24946.0, 'B23025_005E': 3648.0, 'state': '29', 'place': '15670'}, {'NAME': 'Independence city, Missouri', 'B19013_001E': 44261.0, 'B01003_001E': 116881.0, 'B01002_001E': 39.4, 'B19301_001E': 23408.0, 'B17001_002E': 20022.0, 'B23025_005E': 5921.0, 'state': '29', 'place': '35000'}, {'NAME': 'Kansas City city, Missouri', 'B19013_001E': 45275.0, 'B01003_001E': 462378.0, 'B01002_001E': 35.0, 'B19301_001E': 26889.0, 'B17001_002E': 86683.0, 'B23025_005E': 23936.0, 'state': '29', 'place': '38000'}, {'NAME': "Lee's Summit city, Missouri", 'B19013_001E': 77285.0, 'B01003_001E': 91758.0, 'B01002_001E': 36.9, 'B19301_001E': 34353.0, 'B17001_002E': 6113.0, 'B23025_005E': 2778.0, 'state': '29', 'place': '41348'}, {'NAME': "O'Fallon city, Missouri", 'B19013_001E': 76763.0, 'B01003_001E': 80617.0, 'B01002_001E': 34.3, 'B19301_001E': 30650.0, 'B17001_002E': 3390.0, 'B23025_005E': 2541.0, 'state': '29', 'place': '54074'}, {'NAME': 'St. Joseph city, Missouri', 'B19013_001E': 41969.0, 'B01003_001E': 76984.0, 'B01002_001E': 35.7, 'B19301_001E': 21127.0, 'B17001_002E': 13800.0, 'B23025_005E': 3403.0, 'state': '29', 'place': '64550'}, {'NAME': 'St. Louis city, Missouri', 'B19013_001E': 34582.0, 'B01003_001E': 318955.0, 'B01002_001E': 34.2, 'B19301_001E': 23048.0, 'B17001_002E': 84785.0, 'B23025_005E': 24367.0, 'state': '29', 'place': '65000'}, {'NAME': 'Springfield city, Missouri', 'B19013_001E': 32333.0, 'B01003_001E': 161189.0, 'B01002_001E': 32.9, 'B19301_001E': 20634.0, 'B17001_002E': 38395.0, 'B23025_005E': 8650.0, 'state': '29', 'place': '70000'}, {'NAME': 'Billings city, Montana', 'B19013_001E': 48908.0, 'B01003_001E': 105864.0, 'B01002_001E': 37.4, 'B19301_001E': 27544.0, 'B17001_002E': 14441.0, 'B23025_005E': 3022.0, 'state': '30', 'place': '06550'}, {'NAME': 'Missoula city, Montana', 'B19013_001E': 40682.0, 'B01003_001E': 67710.0, 'B01002_001E': 31.5, 'B19301_001E': 24884.0, 'B17001_002E': 13428.0, 'B23025_005E': 3805.0, 'state': '30', 'place': '50200'}, {'NAME': 'Lincoln city, Nebraska', 'B19013_001E': 49113.0, 'B01003_001E': 262365.0, 'B01002_001E': 31.9, 'B19301_001E': 26188.0, 'B17001_002E': 40973.0, 'B23025_005E': 10171.0, 'state': '31', 'place': '28000'}, {'NAME': 'Omaha city, Nebraska', 'B19013_001E': 48052.0, 'B01003_001E': 422499.0, 'B01002_001E': 33.9, 'B19301_001E': 27165.0, 'B17001_002E': 68464.0, 'B23025_005E': 17575.0, 'state': '31', 'place': '37000'}, {'NAME': 'Henderson city, Nevada', 'B19013_001E': 64489.0, 'B01003_001E': 261953.0, 'B01002_001E': 40.9, 'B19301_001E': 33448.0, 'B17001_002E': 25532.0, 'B23025_005E': 14774.0, 'state': '32', 'place': '31900'}, {'NAME': 'Las Vegas city, Nevada', 'B19013_001E': 51143.0, 'B01003_001E': 591496.0, 'B01002_001E': 36.3, 'B19301_001E': 25607.0, 'B17001_002E': 100024.0, 'B23025_005E': 41525.0, 'state': '32', 'place': '40000'}, {'NAME': 'North Las Vegas city, Nevada', 'B19013_001E': 53751.0, 'B01003_001E': 219725.0, 'B01002_001E': 30.5, 'B19301_001E': 20895.0, 'B17001_002E': 34586.0, 'B23025_005E': 13654.0, 'state': '32', 'place': '51800'}, {'NAME': 'Reno city, Nevada', 'B19013_001E': 46770.0, 'B01003_001E': 228442.0, 'B01002_001E': 34.4, 'B19301_001E': 26472.0, 'B17001_002E': 41572.0, 'B23025_005E': 13783.0, 'state': '32', 'place': '60600'}, {'NAME': 'Sparks city, Nevada', 'B19013_001E': 52581.0, 'B01003_001E': 91168.0, 'B01002_001E': 37.1, 'B19301_001E': 25540.0, 'B17001_002E': 11837.0, 'B23025_005E': 5571.0, 'state': '32', 'place': '68400'}, {'NAME': 'Manchester city, New Hampshire', 'B19013_001E': 54496.0, 'B01003_001E': 109942.0, 'B01002_001E': 36.1, 'B19301_001E': 28055.0, 'B17001_002E': 15281.0, 'B23025_005E': 5246.0, 'state': '33', 'place': '45140'}, {'NAME': 'Nashua city, New Hampshire', 'B19013_001E': 64661.0, 'B01003_001E': 86766.0, 'B01002_001E': 38.2, 'B19301_001E': 32874.0, 'B17001_002E': 9165.0, 'B23025_005E': 4352.0, 'state': '33', 'place': '50260'}, {'NAME': 'Camden city, New Jersey', 'B19013_001E': 26202.0, 'B01003_001E': 77356.0, 'B01002_001E': 29.1, 'B19301_001E': 13385.0, 'B17001_002E': 29728.0, 'B23025_005E': 7762.0, 'state': '34', 'place': '10000'}, {'NAME': 'Clifton city, New Jersey', 'B19013_001E': 66382.0, 'B01003_001E': 84591.0, 'B01002_001E': 37.5, 'B19301_001E': 30803.0, 'B17001_002E': 7479.0, 'B23025_005E': 3823.0, 'state': '34', 'place': '13690'}, {'NAME': 'Elizabeth city, New Jersey', 'B19013_001E': 44110.0, 'B01003_001E': 125888.0, 'B01002_001E': 32.3, 'B19301_001E': 19061.0, 'B17001_002E': 22680.0, 'B23025_005E': 8252.0, 'state': '34', 'place': '21000'}, {'NAME': 'Jersey City city, New Jersey', 'B19013_001E': 58206.0, 'B01003_001E': 251717.0, 'B01002_001E': 33.3, 'B19301_001E': 32751.0, 'B17001_002E': 45824.0, 'B23025_005E': 15409.0, 'state': '34', 'place': '36000'}, {'NAME': 'Newark city, New Jersey', 'B19013_001E': 33960.0, 'B01003_001E': 277357.0, 'B01002_001E': 32.3, 'B19301_001E': 16972.0, 'B17001_002E': 77198.0, 'B23025_005E': 26099.0, 'state': '34', 'place': '51000'}, {'NAME': 'Passaic city, New Jersey', 'B19013_001E': 32159.0, 'B01003_001E': 70172.0, 'B01002_001E': 28.8, 'B19301_001E': 14881.0, 'B17001_002E': 21078.0, 'B23025_005E': 3225.0, 'state': '34', 'place': '56550'}, {'NAME': 'Paterson city, New Jersey', 'B19013_001E': 32707.0, 'B01003_001E': 145920.0, 'B01002_001E': 32.3, 'B19301_001E': 15876.0, 'B17001_002E': 41975.0, 'B23025_005E': 7702.0, 'state': '34', 'place': '57000'}, {'NAME': 'Trenton city, New Jersey', 'B19013_001E': 36662.0, 'B01003_001E': 84609.0, 'B01002_001E': 33.2, 'B19301_001E': 17532.0, 'B17001_002E': 21288.0, 'B23025_005E': 7495.0, 'state': '34', 'place': '74000'}, {'NAME': 'Union City city, New Jersey', 'B19013_001E': 40763.0, 'B01003_001E': 67233.0, 'B01002_001E': 34.0, 'B19301_001E': 19475.0, 'B17001_002E': 16307.0, 'B23025_005E': 5057.0, 'state': '34', 'place': '74630'}, {'NAME': 'Albuquerque city, New Mexico', 'B19013_001E': 47989.0, 'B01003_001E': 549812.0, 'B01002_001E': 35.4, 'B19301_001E': 26769.0, 'B17001_002E': 97304.0, 'B23025_005E': 23757.0, 'state': '35', 'place': '02000'}, {'NAME': 'Rio Rancho city, New Mexico', 'B19013_001E': 59883.0, 'B01003_001E': 89098.0, 'B01002_001E': 36.4, 'B19301_001E': 27311.0, 'B17001_002E': 10082.0, 'B23025_005E': 3386.0, 'state': '35', 'place': '63460'}, {'NAME': 'Las Cruces city, New Mexico', 'B19013_001E': 40040.0, 'B01003_001E': 99186.0, 'B01002_001E': 31.7, 'B19301_001E': 21460.0, 'B17001_002E': 22265.0, 'B23025_005E': 5374.0, 'state': '35', 'place': '39380'}, {'NAME': 'Santa Fe city, New Mexico', 'B19013_001E': 50283.0, 'B01003_001E': 68800.0, 'B01002_001E': 44.2, 'B19301_001E': 33887.0, 'B17001_002E': 12090.0, 'B23025_005E': 3691.0, 'state': '35', 'place': '70500'}, {'NAME': 'Albany city, New York', 'B19013_001E': 40287.0, 'B01003_001E': 98142.0, 'B01002_001E': 30.7, 'B19301_001E': 23860.0, 'B17001_002E': 22337.0, 'B23025_005E': 5093.0, 'state': '36', 'place': '01000'}, {'NAME': 'Buffalo city, New York', 'B19013_001E': 30942.0, 'B01003_001E': 260568.0, 'B01002_001E': 33.5, 'B19301_001E': 20392.0, 'B17001_002E': 77299.0, 'B23025_005E': 17100.0, 'state': '36', 'place': '11000'}, {'NAME': 'Mount Vernon city, New York', 'B19013_001E': 49328.0, 'B01003_001E': 67653.0, 'B01002_001E': 37.7, 'B19301_001E': 27454.0, 'B17001_002E': 10672.0, 'B23025_005E': 5302.0, 'state': '36', 'place': '49121'}, {'NAME': 'New Rochelle city, New York', 'B19013_001E': 67094.0, 'B01003_001E': 77820.0, 'B01002_001E': 38.4, 'B19301_001E': 40705.0, 'B17001_002E': 9299.0, 'B23025_005E': 3457.0, 'state': '36', 'place': '50617'}, {'NAME': 'New York city, New York', 'B19013_001E': 52259.0, 'B01003_001E': 8268999.0, 'B01002_001E': 35.6, 'B19301_001E': 32010.0, 'B17001_002E': 1653857.0, 'B23025_005E': 450989.0, 'state': '36', 'place': '51000'}, {'NAME': 'Rochester city, New York', 'B19013_001E': 30875.0, 'B01003_001E': 210624.0, 'B01002_001E': 31.1, 'B19301_001E': 18847.0, 'B17001_002E': 66312.0, 'B23025_005E': 13812.0, 'state': '36', 'place': '63000'}, {'NAME': 'Schenectady city, New York', 'B19013_001E': 38381.0, 'B01003_001E': 65990.0, 'B01002_001E': 34.6, 'B19301_001E': 20467.0, 'B17001_002E': 14994.0, 'B23025_005E': 3795.0, 'state': '36', 'place': '65508'}, {'NAME': 'Syracuse city, New York', 'B19013_001E': 31365.0, 'B01003_001E': 144742.0, 'B01002_001E': 29.4, 'B19301_001E': 19121.0, 'B17001_002E': 45605.0, 'B23025_005E': 8145.0, 'state': '36', 'place': '73000'}, {'NAME': 'Yonkers city, New York', 'B19013_001E': 59195.0, 'B01003_001E': 197493.0, 'B01002_001E': 37.6, 'B19301_001E': 29679.0, 'B17001_002E': 30362.0, 'B23025_005E': 9185.0, 'state': '36', 'place': '84000'}, {'NAME': 'Asheville city, North Carolina', 'B19013_001E': 42016.0, 'B01003_001E': 84883.0, 'B01002_001E': 38.0, 'B19301_001E': 26912.0, 'B17001_002E': 16398.0, 'B23025_005E': 4037.0, 'state': '37', 'place': '02140'}, {'NAME': 'Cary town, North Carolina', 'B19013_001E': 90250.0, 'B01003_001E': 141292.0, 'B01002_001E': 36.4, 'B19301_001E': 41554.0, 'B17001_002E': 8663.0, 'B23025_005E': 4138.0, 'state': '37', 'place': '10740'}, {'NAME': 'Charlotte city, North Carolina', 'B19013_001E': 52375.0, 'B01003_001E': 757278.0, 'B01002_001E': 33.5, 'B19301_001E': 31556.0, 'B17001_002E': 127166.0, 'B23025_005E': 47673.0, 'state': '37', 'place': '12000'}, {'NAME': 'Concord city, North Carolina', 'B19013_001E': 53337.0, 'B01003_001E': 80715.0, 'B01002_001E': 35.5, 'B19301_001E': 25897.0, 'B17001_002E': 10045.0, 'B23025_005E': 5217.0, 'state': '37', 'place': '14100'}, {'NAME': 'Durham city, North Carolina', 'B19013_001E': 49160.0, 'B01003_001E': 234922.0, 'B01002_001E': 32.4, 'B19301_001E': 28565.0, 'B17001_002E': 45149.0, 'B23025_005E': 11169.0, 'state': '37', 'place': '19000'}, {'NAME': 'Fayetteville city, North Carolina', 'B19013_001E': 44900.0, 'B01003_001E': 201755.0, 'B01002_001E': 30.0, 'B19301_001E': 23409.0, 'B17001_002E': 33559.0, 'B23025_005E': 11832.0, 'state': '37', 'place': '22920'}, {'NAME': 'Gastonia city, North Carolina', 'B19013_001E': 40053.0, 'B01003_001E': 72300.0, 'B01002_001E': 36.6, 'B19301_001E': 21531.0, 'B17001_002E': 15807.0, 'B23025_005E': 4895.0, 'state': '37', 'place': '25580'}, {'NAME': 'Greensboro city, North Carolina', 'B19013_001E': 41120.0, 'B01003_001E': 273228.0, 'B01002_001E': 34.2, 'B19301_001E': 25861.0, 'B17001_002E': 53329.0, 'B23025_005E': 15342.0, 'state': '37', 'place': '28000'}, {'NAME': 'Greenville city, North Carolina', 'B19013_001E': 35137.0, 'B01003_001E': 86249.0, 'B01002_001E': 26.1, 'B19301_001E': 22836.0, 'B17001_002E': 24229.0, 'B23025_005E': 5931.0, 'state': '37', 'place': '28080'}, {'NAME': 'High Point city, North Carolina', 'B19013_001E': 43083.0, 'B01003_001E': 105723.0, 'B01002_001E': 35.7, 'B19301_001E': 22940.0, 'B17001_002E': 22048.0, 'B23025_005E': 6928.0, 'state': '37', 'place': '31400'}, {'NAME': 'Jacksonville city, North Carolina', 'B19013_001E': 42459.0, 'B01003_001E': 69415.0, 'B01002_001E': 23.3, 'B19301_001E': 21210.0, 'B17001_002E': 8242.0, 'B23025_005E': 2307.0, 'state': '37', 'place': '34200'}, {'NAME': 'Raleigh city, North Carolina', 'B19013_001E': 54448.0, 'B01003_001E': 414530.0, 'B01002_001E': 32.2, 'B19301_001E': 30470.0, 'B17001_002E': 64072.0, 'B23025_005E': 20389.0, 'state': '37', 'place': '55000'}, {'NAME': 'Wilmington city, North Carolina', 'B19013_001E': 41573.0, 'B01003_001E': 108530.0, 'B01002_001E': 34.6, 'B19301_001E': 29017.0, 'B17001_002E': 24291.0, 'B23025_005E': 6985.0, 'state': '37', 'place': '74440'}, {'NAME': 'Winston-Salem city, North Carolina', 'B19013_001E': 40148.0, 'B01003_001E': 232219.0, 'B01002_001E': 34.6, 'B19301_001E': 24858.0, 'B17001_002E': 51700.0, 'B23025_005E': 13479.0, 'state': '37', 'place': '75000'}, {'NAME': 'Fargo city, North Dakota', 'B19013_001E': 45458.0, 'B01003_001E': 108371.0, 'B01002_001E': 30.2, 'B19301_001E': 29261.0, 'B17001_002E': 16977.0, 'B23025_005E': 3240.0, 'state': '38', 'place': '25700'}, {'NAME': 'Akron city, Ohio', 'B19013_001E': 33909.0, 'B01003_001E': 199038.0, 'B01002_001E': 36.0, 'B19301_001E': 19968.0, 'B17001_002E': 53304.0, 'B23025_005E': 15517.0, 'state': '39', 'place': '01000'}, {'NAME': 'Canton city, Ohio', 'B19013_001E': 30209.0, 'B01003_001E': 73027.0, 'B01002_001E': 35.0, 'B19301_001E': 16669.0, 'B17001_002E': 22340.0, 'B23025_005E': 5346.0, 'state': '39', 'place': '12000'}, {'NAME': 'Cincinnati city, Ohio', 'B19013_001E': 34116.0, 'B01003_001E': 297150.0, 'B01002_001E': 32.3, 'B19301_001E': 24779.0, 'B17001_002E': 86686.0, 'B23025_005E': 19791.0, 'state': '39', 'place': '15000'}, {'NAME': 'Cleveland city, Ohio', 'B19013_001E': 26217.0, 'B01003_001E': 394335.0, 'B01002_001E': 36.0, 'B19301_001E': 16992.0, 'B17001_002E': 135926.0, 'B23025_005E': 36420.0, 'state': '39', 'place': '16000'}, {'NAME': 'Columbus city, Ohio', 'B19013_001E': 44072.0, 'B01003_001E': 800594.0, 'B01002_001E': 31.8, 'B19301_001E': 24351.0, 'B17001_002E': 174607.0, 'B23025_005E': 42450.0, 'state': '39', 'place': '18000'}, {'NAME': 'Dayton city, Ohio', 'B19013_001E': 28456.0, 'B01003_001E': 143446.0, 'B01002_001E': 33.2, 'B19301_001E': 16494.0, 'B17001_002E': 44929.0, 'B23025_005E': 11971.0, 'state': '39', 'place': '21000'}, {'NAME': 'Parma city, Ohio', 'B19013_001E': 49654.0, 'B01003_001E': 81055.0, 'B01002_001E': 42.0, 'B19301_001E': 24713.0, 'B17001_002E': 8667.0, 'B23025_005E': 4029.0, 'state': '39', 'place': '61000'}, {'NAME': 'Toledo city, Ohio', 'B19013_001E': 33317.0, 'B01003_001E': 285459.0, 'B01002_001E': 34.8, 'B19301_001E': 18760.0, 'B17001_002E': 75657.0, 'B23025_005E': 24090.0, 'state': '39', 'place': '77000'}, {'NAME': 'Youngstown city, Ohio', 'B19013_001E': 24454.0, 'B01003_001E': 66511.0, 'B01002_001E': 38.9, 'B19301_001E': 14876.0, 'B17001_002E': 22271.0, 'B23025_005E': 5327.0, 'state': '39', 'place': '88000'}, {'NAME': 'Broken Arrow city, Oklahoma', 'B19013_001E': 65484.0, 'B01003_001E': 100464.0, 'B01002_001E': 36.0, 'B19301_001E': 29103.0, 'B17001_002E': 7685.0, 'B23025_005E': 3155.0, 'state': '40', 'place': '09050'}, {'NAME': 'Edmond city, Oklahoma', 'B19013_001E': 71215.0, 'B01003_001E': 83390.0, 'B01002_001E': 35.7, 'B19301_001E': 38011.0, 'B17001_002E': 7974.0, 'B23025_005E': 2148.0, 'state': '40', 'place': '23200'}, {'NAME': 'Lawton city, Oklahoma', 'B19013_001E': 43269.0, 'B01003_001E': 97147.0, 'B01002_001E': 30.1, 'B19301_001E': 21146.0, 'B17001_002E': 16381.0, 'B23025_005E': 4009.0, 'state': '40', 'place': '41850'}, {'NAME': 'Norman city, Oklahoma', 'B19013_001E': 49038.0, 'B01003_001E': 113743.0, 'B01002_001E': 30.2, 'B19301_001E': 27749.0, 'B17001_002E': 18879.0, 'B23025_005E': 3648.0, 'state': '40', 'place': '52500'}, {'NAME': 'Oklahoma City city, Oklahoma', 'B19013_001E': 45824.0, 'B01003_001E': 590995.0, 'B01002_001E': 33.6, 'B19301_001E': 25640.0, 'B17001_002E': 105777.0, 'B23025_005E': 20562.0, 'state': '40', 'place': '55000'}, {'NAME': 'Tulsa city, Oklahoma', 'B19013_001E': 41241.0, 'B01003_001E': 393709.0, 'B01002_001E': 34.9, 'B19301_001E': 27089.0, 'B17001_002E': 77516.0, 'B23025_005E': 16001.0, 'state': '40', 'place': '75000'}, {'NAME': 'Beaverton city, Oregon', 'B19013_001E': 56107.0, 'B01003_001E': 91383.0, 'B01002_001E': 35.2, 'B19301_001E': 30250.0, 'B17001_002E': 12499.0, 'B23025_005E': 5250.0, 'state': '41', 'place': '05350'}, {'NAME': 'Bend city, Oregon', 'B19013_001E': 53027.0, 'B01003_001E': 78128.0, 'B01002_001E': 37.8, 'B19301_001E': 29650.0, 'B17001_002E': 9953.0, 'B23025_005E': 3996.0, 'state': '41', 'place': '05800'}, {'NAME': 'Eugene city, Oregon', 'B19013_001E': 42167.0, 'B01003_001E': 157318.0, 'B01002_001E': 34.2, 'B19301_001E': 26017.0, 'B17001_002E': 36511.0, 'B23025_005E': 9169.0, 'state': '41', 'place': '23850'}, {'NAME': 'Gresham city, Oregon', 'B19013_001E': 47417.0, 'B01003_001E': 107196.0, 'B01002_001E': 34.2, 'B19301_001E': 21553.0, 'B17001_002E': 20835.0, 'B23025_005E': 6773.0, 'state': '41', 'place': '31250'}, {'NAME': 'Hillsboro city, Oregon', 'B19013_001E': 65158.0, 'B01003_001E': 93880.0, 'B01002_001E': 32.2, 'B19301_001E': 27502.0, 'B17001_002E': 12600.0, 'B23025_005E': 5083.0, 'state': '41', 'place': '34100'}, {'NAME': 'Medford city, Oregon', 'B19013_001E': 41513.0, 'B01003_001E': 75902.0, 'B01002_001E': 37.8, 'B19301_001E': 22963.0, 'B17001_002E': 15432.0, 'B23025_005E': 4505.0, 'state': '41', 'place': '47000'}, {'NAME': 'Portland city, Oregon', 'B19013_001E': 52657.0, 'B01003_001E': 594687.0, 'B01002_001E': 36.3, 'B19301_001E': 31839.0, 'B17001_002E': 103514.0, 'B23025_005E': 35323.0, 'state': '41', 'place': '59000'}, {'NAME': 'Salem city, Oregon', 'B19013_001E': 45971.0, 'B01003_001E': 156937.0, 'B01002_001E': 35.0, 'B19301_001E': 23316.0, 'B17001_002E': 27772.0, 'B23025_005E': 9928.0, 'state': '41', 'place': '64900'}, {'NAME': 'Allentown city, Pennsylvania', 'B19013_001E': 35560.0, 'B01003_001E': 118285.0, 'B01002_001E': 32.4, 'B19301_001E': 17235.0, 'B17001_002E': 31479.0, 'B23025_005E': 8636.0, 'state': '42', 'place': '02000'}, {'NAME': 'Bethlehem city, Pennsylvania', 'B19013_001E': 46292.0, 'B01003_001E': 75030.0, 'B01002_001E': 35.3, 'B19301_001E': 23827.0, 'B17001_002E': 13604.0, 'B23025_005E': 3626.0, 'state': '42', 'place': '06088'}, {'NAME': 'Erie city, Pennsylvania', 'B19013_001E': 33049.0, 'B01003_001E': 101324.0, 'B01002_001E': 33.7, 'B19301_001E': 18907.0, 'B17001_002E': 26827.0, 'B23025_005E': 5701.0, 'state': '42', 'place': '24000'}, {'NAME': 'Philadelphia city, Pennsylvania', 'B19013_001E': 37192.0, 'B01003_001E': 1536704.0, 'B01002_001E': 33.6, 'B19301_001E': 22279.0, 'B17001_002E': 395789.0, 'B23025_005E': 110019.0, 'state': '42', 'place': '60000'}, {'NAME': 'Pittsburgh city, Pennsylvania', 'B19013_001E': 39195.0, 'B01003_001E': 306062.0, 'B01002_001E': 33.4, 'B19301_001E': 26892.0, 'B17001_002E': 63807.0, 'B23025_005E': 15535.0, 'state': '42', 'place': '61000'}, {'NAME': 'Reading city, Pennsylvania', 'B19013_001E': 26777.0, 'B01003_001E': 87978.0, 'B01002_001E': 29.4, 'B19301_001E': 13306.0, 'B17001_002E': 33151.0, 'B23025_005E': 7968.0, 'state': '42', 'place': '63624'}, {'NAME': 'Scranton city, Pennsylvania', 'B19013_001E': 38463.0, 'B01003_001E': 75982.0, 'B01002_001E': 37.8, 'B19301_001E': 20244.0, 'B17001_002E': 14492.0, 'B23025_005E': 3390.0, 'state': '42', 'place': '69000'}, {'NAME': 'Cranston city, Rhode Island', 'B19013_001E': 60283.0, 'B01003_001E': 80470.0, 'B01002_001E': 41.1, 'B19301_001E': 29267.0, 'B17001_002E': 7740.0, 'B23025_005E': 4433.0, 'state': '44', 'place': '19180'}, {'NAME': 'Pawtucket city, Rhode Island', 'B19013_001E': 40379.0, 'B01003_001E': 71163.0, 'B01002_001E': 37.3, 'B19301_001E': 21637.0, 'B17001_002E': 13599.0, 'B23025_005E': 5193.0, 'state': '44', 'place': '54640'}, {'NAME': 'Providence city, Rhode Island', 'B19013_001E': 37632.0, 'B01003_001E': 178056.0, 'B01002_001E': 28.8, 'B19301_001E': 21676.0, 'B17001_002E': 47500.0, 'B23025_005E': 13509.0, 'state': '44', 'place': '59000'}, {'NAME': 'Warwick city, Rhode Island', 'B19013_001E': 62295.0, 'B01003_001E': 82378.0, 'B01002_001E': 44.2, 'B19301_001E': 33474.0, 'B17001_002E': 5899.0, 'B23025_005E': 4334.0, 'state': '44', 'place': '74300'}, {'NAME': 'Charleston city, South Carolina', 'B19013_001E': 51737.0, 'B01003_001E': 123267.0, 'B01002_001E': 32.8, 'B19301_001E': 32131.0, 'B17001_002E': 22919.0, 'B23025_005E': 5579.0, 'state': '45', 'place': '13330'}, {'NAME': 'Columbia city, South Carolina', 'B19013_001E': 41344.0, 'B01003_001E': 131004.0, 'B01002_001E': 28.5, 'B19301_001E': 24779.0, 'B17001_002E': 24612.0, 'B23025_005E': 7580.0, 'state': '45', 'place': '16000'}, {'NAME': 'Mount Pleasant town, South Carolina', 'B19013_001E': 76085.0, 'B01003_001E': 70131.0, 'B01002_001E': 38.1, 'B19301_001E': 40870.0, 'B17001_002E': 5628.0, 'B23025_005E': 2507.0, 'state': '45', 'place': '48535'}, {'NAME': 'North Charleston city, South Carolina', 'B19013_001E': 39322.0, 'B01003_001E': 100018.0, 'B01002_001E': 30.8, 'B19301_001E': 19717.0, 'B17001_002E': 22201.0, 'B23025_005E': 6409.0, 'state': '45', 'place': '50875'}, {'NAME': 'Rock Hill city, South Carolina', 'B19013_001E': 42550.0, 'B01003_001E': 67390.0, 'B01002_001E': 31.9, 'B19301_001E': 22416.0, 'B17001_002E': 12010.0, 'B23025_005E': 4450.0, 'state': '45', 'place': '61405'}, {'NAME': 'Rapid City city, South Dakota', 'B19013_001E': 46370.0, 'B01003_001E': 69000.0, 'B01002_001E': 36.2, 'B19301_001E': 26412.0, 'B17001_002E': 10652.0, 'B23025_005E': 2395.0, 'state': '46', 'place': '52980'}, {'NAME': 'Sioux Falls city, South Dakota', 'B19013_001E': 51672.0, 'B01003_001E': 157675.0, 'B01002_001E': 33.7, 'B19301_001E': 27559.0, 'B17001_002E': 17088.0, 'B23025_005E': 4172.0, 'state': '46', 'place': '59020'}, {'NAME': 'Chattanooga city, Tennessee', 'B19013_001E': 38064.0, 'B01003_001E': 170246.0, 'B01002_001E': 37.3, 'B19301_001E': 23847.0, 'B17001_002E': 39146.0, 'B23025_005E': 10138.0, 'state': '47', 'place': '14000'}, {'NAME': 'Clarksville city, Tennessee', 'B19013_001E': 47092.0, 'B01003_001E': 137145.0, 'B01002_001E': 28.5, 'B19301_001E': 21079.0, 'B17001_002E': 24168.0, 'B23025_005E': 6840.0, 'state': '47', 'place': '15160'}, {'NAME': 'Knoxville city, Tennessee', 'B19013_001E': 33595.0, 'B01003_001E': 180830.0, 'B01002_001E': 34.1, 'B19301_001E': 23336.0, 'B17001_002E': 39583.0, 'B23025_005E': 7666.0, 'state': '47', 'place': '40000'}, {'NAME': 'Memphis city, Tennessee', 'B19013_001E': 36912.0, 'B01003_001E': 650932.0, 'B01002_001E': 33.2, 'B19301_001E': 21454.0, 'B17001_002E': 170736.0, 'B23025_005E': 46168.0, 'state': '47', 'place': '48000'}, {'NAME': 'Murfreesboro city, Tennessee', 'B19013_001E': 49358.0, 'B01003_001E': 111814.0, 'B01002_001E': 29.9, 'B19301_001E': 25443.0, 'B17001_002E': 18766.0, 'B23025_005E': 5732.0, 'state': '47', 'place': '51560'}, {'NAME': 'Nashville-Davidson metropolitan government (balance), Tennessee', 'B19013_001E': 46686.0, 'B01003_001E': 614908.0, 'B01002_001E': 33.8, 'B19301_001E': 27356.0, 'B17001_002E': 111947.0, 'B23025_005E': 30411.0, 'state': '47', 'place': '52006'}, {'NAME': 'Abilene city, Texas', 'B19013_001E': 42559.0, 'B01003_001E': 119721.0, 'B01002_001E': 31.2, 'B19301_001E': 20762.0, 'B17001_002E': 20778.0, 'B23025_005E': 3802.0, 'state': '48', 'place': '01000'}, {'NAME': 'Allen city, Texas', 'B19013_001E': 101636.0, 'B01003_001E': 87213.0, 'B01002_001E': 35.1, 'B19301_001E': 39077.0, 'B17001_002E': 4622.0, 'B23025_005E': 2733.0, 'state': '48', 'place': '01924'}, {'NAME': 'Amarillo city, Texas', 'B19013_001E': 45984.0, 'B01003_001E': 193153.0, 'B01002_001E': 33.5, 'B19301_001E': 24156.0, 'B17001_002E': 33304.0, 'B23025_005E': 5423.0, 'state': '48', 'place': '03000'}, {'NAME': 'Arlington city, Texas', 'B19013_001E': 52933.0, 'B01003_001E': 371267.0, 'B01002_001E': 32.0, 'B19301_001E': 25456.0, 'B17001_002E': 61097.0, 'B23025_005E': 18690.0, 'state': '48', 'place': '04000'}, {'NAME': 'Austin city, Texas', 'B19013_001E': 53946.0, 'B01003_001E': 836800.0, 'B01002_001E': 31.5, 'B19301_001E': 31990.0, 'B17001_002E': 155996.0, 'B23025_005E': 36457.0, 'state': '48', 'place': '05000'}, {'NAME': 'Baytown city, Texas', 'B19013_001E': 46939.0, 'B01003_001E': 73043.0, 'B01002_001E': 31.8, 'B19301_001E': 21262.0, 'B17001_002E': 14707.0, 'B23025_005E': 3960.0, 'state': '48', 'place': '06128'}, {'NAME': 'Beaumont city, Texas', 'B19013_001E': 39526.0, 'B01003_001E': 117478.0, 'B01002_001E': 34.3, 'B19301_001E': 23579.0, 'B17001_002E': 25884.0, 'B23025_005E': 6040.0, 'state': '48', 'place': '07000'}, {'NAME': 'Brownsville city, Texas', 'B19013_001E': 32105.0, 'B01003_001E': 177795.0, 'B01002_001E': 29.2, 'B19301_001E': 13947.0, 'B17001_002E': 62048.0, 'B23025_005E': 8183.0, 'state': '48', 'place': '10768'}, {'NAME': 'Bryan city, Texas', 'B19013_001E': 38356.0, 'B01003_001E': 77139.0, 'B01002_001E': 28.7, 'B19301_001E': 19816.0, 'B17001_002E': 20948.0, 'B23025_005E': 3804.0, 'state': '48', 'place': '10912'}, {'NAME': 'Carrollton city, Texas', 'B19013_001E': 68811.0, 'B01003_001E': 122613.0, 'B01002_001E': 36.2, 'B19301_001E': 31709.0, 'B17001_002E': 11645.0, 'B23025_005E': 4869.0, 'state': '48', 'place': '13024'}, {'NAME': 'College Station city, Texas', 'B19013_001E': 31596.0, 'B01003_001E': 96000.0, 'B01002_001E': 22.6, 'B19301_001E': 20799.0, 'B17001_002E': 30481.0, 'B23025_005E': 3835.0, 'state': '48', 'place': '15976'}, {'NAME': 'Corpus Christi city, Texas', 'B19013_001E': 47481.0, 'B01003_001E': 308993.0, 'B01002_001E': 34.4, 'B19301_001E': 24002.0, 'B17001_002E': 55002.0, 'B23025_005E': 12206.0, 'state': '48', 'place': '17000'}, {'NAME': 'Dallas city, Texas', 'B19013_001E': 42846.0, 'B01003_001E': 1222167.0, 'B01002_001E': 32.0, 'B19301_001E': 27426.0, 'B17001_002E': 286669.0, 'B23025_005E': 59275.0, 'state': '48', 'place': '19000'}, {'NAME': 'Denton city, Texas', 'B19013_001E': 48182.0, 'B01003_001E': 117895.0, 'B01002_001E': 27.5, 'B19301_001E': 24089.0, 'B17001_002E': 22089.0, 'B23025_005E': 6595.0, 'state': '48', 'place': '19972'}, {'NAME': 'Edinburg city, Texas', 'B19013_001E': 41891.0, 'B01003_001E': 77415.0, 'B01002_001E': 27.9, 'B19301_001E': 17103.0, 'B17001_002E': 19727.0, 'B23025_005E': 3797.0, 'state': '48', 'place': '22660'}, {'NAME': 'El Paso city, Texas', 'B19013_001E': 41406.0, 'B01003_001E': 660795.0, 'B01002_001E': 32.3, 'B19301_001E': 19669.0, 'B17001_002E': 140275.0, 'B23025_005E': 24943.0, 'state': '48', 'place': '24000'}, {'NAME': 'Fort Worth city, Texas', 'B19013_001E': 51315.0, 'B01003_001E': 761092.0, 'B01002_001E': 31.5, 'B19301_001E': 24489.0, 'B17001_002E': 144181.0, 'B23025_005E': 34846.0, 'state': '48', 'place': '27000'}, {'NAME': 'Frisco city, Texas', 'B19013_001E': 108284.0, 'B01003_001E': 123663.0, 'B01002_001E': 34.5, 'B19301_001E': 42307.0, 'B17001_002E': 5409.0, 'B23025_005E': 3370.0, 'state': '48', 'place': '27684'}, {'NAME': 'Garland city, Texas', 'B19013_001E': 51842.0, 'B01003_001E': 230177.0, 'B01002_001E': 33.5, 'B19301_001E': 21633.0, 'B17001_002E': 37085.0, 'B23025_005E': 12399.0, 'state': '48', 'place': '29000'}, {'NAME': 'Grand Prairie city, Texas', 'B19013_001E': 53927.0, 'B01003_001E': 178195.0, 'B01002_001E': 31.5, 'B19301_001E': 22452.0, 'B17001_002E': 27655.0, 'B23025_005E': 8768.0, 'state': '48', 'place': '30464'}, {'NAME': 'Houston city, Texas', 'B19013_001E': 45010.0, 'B01003_001E': 2134707.0, 'B01002_001E': 32.4, 'B19301_001E': 27305.0, 'B17001_002E': 480971.0, 'B23025_005E': 104520.0, 'state': '48', 'place': '35000'}, {'NAME': 'Irving city, Texas', 'B19013_001E': 50778.0, 'B01003_001E': 220856.0, 'B01002_001E': 31.6, 'B19301_001E': 27040.0, 'B17001_002E': 35421.0, 'B23025_005E': 10491.0, 'state': '48', 'place': '37000'}, {'NAME': 'Killeen city, Texas', 'B19013_001E': 45895.0, 'B01003_001E': 131237.0, 'B01002_001E': 27.7, 'B19301_001E': 19986.0, 'B17001_002E': 21624.0, 'B23025_005E': 6925.0, 'state': '48', 'place': '39148'}, {'NAME': 'Laredo city, Texas', 'B19013_001E': 40041.0, 'B01003_001E': 240524.0, 'B01002_001E': 28.2, 'B19301_001E': 14797.0, 'B17001_002E': 73013.0, 'B23025_005E': 6695.0, 'state': '48', 'place': '41464'}, {'NAME': 'League City city, Texas', 'B19013_001E': 89339.0, 'B01003_001E': 86136.0, 'B01002_001E': 35.1, 'B19301_001E': 38460.0, 'B17001_002E': 4298.0, 'B23025_005E': 2621.0, 'state': '48', 'place': '41980'}, {'NAME': 'Lewisville city, Texas', 'B19013_001E': 58580.0, 'B01003_001E': 97462.0, 'B01002_001E': 31.6, 'B19301_001E': 28524.0, 'B17001_002E': 9495.0, 'B23025_005E': 3434.0, 'state': '48', 'place': '42508'}, {'NAME': 'Longview city, Texas', 'B19013_001E': 43466.0, 'B01003_001E': 81435.0, 'B01002_001E': 34.3, 'B19301_001E': 23375.0, 'B17001_002E': 13485.0, 'B23025_005E': 2902.0, 'state': '48', 'place': '43888'}, {'NAME': 'Lubbock city, Texas', 'B19013_001E': 42986.0, 'B01003_001E': 233162.0, 'B01002_001E': 29.3, 'B19301_001E': 23521.0, 'B17001_002E': 48318.0, 'B23025_005E': 8653.0, 'state': '48', 'place': '45000'}, {'NAME': 'McAllen city, Texas', 'B19013_001E': 41163.0, 'B01003_001E': 132796.0, 'B01002_001E': 32.6, 'B19301_001E': 20926.0, 'B17001_002E': 35049.0, 'B23025_005E': 4457.0, 'state': '48', 'place': '45384'}, {'NAME': 'McKinney city, Texas', 'B19013_001E': 81118.0, 'B01003_001E': 137643.0, 'B01002_001E': 33.0, 'B19301_001E': 32849.0, 'B17001_002E': 12080.0, 'B23025_005E': 2933.0, 'state': '48', 'place': '45744'}, {'NAME': 'Mesquite city, Texas', 'B19013_001E': 50525.0, 'B01003_001E': 141201.0, 'B01002_001E': 32.3, 'B19301_001E': 21774.0, 'B17001_002E': 20386.0, 'B23025_005E': 5754.0, 'state': '48', 'place': '47892'}, {'NAME': 'Midland city, Texas', 'B19013_001E': 62665.0, 'B01003_001E': 115903.0, 'B01002_001E': 32.4, 'B19301_001E': 34301.0, 'B17001_002E': 12937.0, 'B23025_005E': 2745.0, 'state': '48', 'place': '48072'}, {'NAME': 'Mission city, Texas', 'B19013_001E': 41895.0, 'B01003_001E': 78707.0, 'B01002_001E': 30.2, 'B19301_001E': 17485.0, 'B17001_002E': 20558.0, 'B23025_005E': 2394.0, 'state': '48', 'place': '48768'}, {'NAME': 'Missouri City city, Texas', 'B19013_001E': 83524.0, 'B01003_001E': 68244.0, 'B01002_001E': 37.2, 'B19301_001E': 33070.0, 'B17001_002E': 4721.0, 'B23025_005E': 2622.0, 'state': '48', 'place': '48804'}, {'NAME': 'Odessa city, Texas', 'B19013_001E': 52158.0, 'B01003_001E': 104223.0, 'B01002_001E': 30.9, 'B19301_001E': 25567.0, 'B17001_002E': 15364.0, 'B23025_005E': 2875.0, 'state': '48', 'place': '53388'}, {'NAME': 'Pasadena city, Texas', 'B19013_001E': 46058.0, 'B01003_001E': 150785.0, 'B01002_001E': 30.6, 'B19301_001E': 20146.0, 'B17001_002E': 32598.0, 'B23025_005E': 7578.0, 'state': '48', 'place': '56000'}, {'NAME': 'Pearland city, Texas', 'B19013_001E': 92346.0, 'B01003_001E': 94098.0, 'B01002_001E': 34.3, 'B19301_001E': 36808.0, 'B17001_002E': 4247.0, 'B23025_005E': 2497.0, 'state': '48', 'place': '56348'}, {'NAME': 'Pharr city, Texas', 'B19013_001E': 32087.0, 'B01003_001E': 71634.0, 'B01002_001E': 28.7, 'B19301_001E': 12964.0, 'B17001_002E': 25599.0, 'B23025_005E': 3516.0, 'state': '48', 'place': '57200'}, {'NAME': 'Plano city, Texas', 'B19013_001E': 82484.0, 'B01003_001E': 266740.0, 'B01002_001E': 37.5, 'B19301_001E': 40938.0, 'B17001_002E': 20494.0, 'B23025_005E': 8939.0, 'state': '48', 'place': '58016'}, {'NAME': 'Richardson city, Texas', 'B19013_001E': 69323.0, 'B01003_001E': 101528.0, 'B01002_001E': 36.5, 'B19301_001E': 34637.0, 'B17001_002E': 11845.0, 'B23025_005E': 4449.0, 'state': '48', 'place': '61796'}, {'NAME': 'Round Rock city, Texas', 'B19013_001E': 69533.0, 'B01003_001E': 104070.0, 'B01002_001E': 31.6, 'B19301_001E': 29704.0, 'B17001_002E': 8918.0, 'B23025_005E': 4562.0, 'state': '48', 'place': '63500'}, {'NAME': 'San Angelo city, Texas', 'B19013_001E': 42385.0, 'B01003_001E': 94812.0, 'B01002_001E': 32.5, 'B19301_001E': 23157.0, 'B17001_002E': 15625.0, 'B23025_005E': 3438.0, 'state': '48', 'place': '64472'}, {'NAME': 'San Antonio city, Texas', 'B19013_001E': 45722.0, 'B01003_001E': 1359033.0, 'B01002_001E': 32.7, 'B19301_001E': 22619.0, 'B17001_002E': 265645.0, 'B23025_005E': 57401.0, 'state': '48', 'place': '65000'}, {'NAME': 'Sugar Land city, Texas', 'B19013_001E': 104702.0, 'B01003_001E': 80755.0, 'B01002_001E': 41.4, 'B19301_001E': 45093.0, 'B17001_002E': 3340.0, 'B23025_005E': 2397.0, 'state': '48', 'place': '70808'}, {'NAME': 'Tyler city, Texas', 'B19013_001E': 43289.0, 'B01003_001E': 98335.0, 'B01002_001E': 33.5, 'B19301_001E': 27361.0, 'B17001_002E': 18922.0, 'B23025_005E': 3612.0, 'state': '48', 'place': '74144'}, {'NAME': 'Waco city, Texas', 'B19013_001E': 32650.0, 'B01003_001E': 126406.0, 'B01002_001E': 28.5, 'B19301_001E': 18361.0, 'B17001_002E': 36314.0, 'B23025_005E': 5263.0, 'state': '48', 'place': '76000'}, {'NAME': 'Wichita Falls city, Texas', 'B19013_001E': 44028.0, 'B01003_001E': 104402.0, 'B01002_001E': 32.7, 'B19301_001E': 22635.0, 'B17001_002E': 16395.0, 'B23025_005E': 3479.0, 'state': '48', 'place': '79000'}, {'NAME': 'Layton city, Utah', 'B19013_001E': 65439.0, 'B01003_001E': 68386.0, 'B01002_001E': 29.6, 'B19301_001E': 25424.0, 'B17001_002E': 6388.0, 'B23025_005E': 1766.0, 'state': '49', 'place': '43660'}, {'NAME': 'Ogden city, Utah', 'B19013_001E': 41031.0, 'B01003_001E': 83363.0, 'B01002_001E': 30.2, 'B19301_001E': 19349.0, 'B17001_002E': 18917.0, 'B23025_005E': 4297.0, 'state': '49', 'place': '55980'}, {'NAME': 'Orem city, Utah', 'B19013_001E': 52960.0, 'B01003_001E': 89724.0, 'B01002_001E': 26.4, 'B19301_001E': 20471.0, 'B17001_002E': 14660.0, 'B23025_005E': 3465.0, 'state': '49', 'place': '57300'}, {'NAME': 'Provo city, Utah', 'B19013_001E': 39688.0, 'B01003_001E': 114179.0, 'B01002_001E': 23.5, 'B19301_001E': 16977.0, 'B17001_002E': 33808.0, 'B23025_005E': 4985.0, 'state': '49', 'place': '62470'}, {'NAME': 'St. George city, Utah', 'B19013_001E': 47986.0, 'B01003_001E': 74301.0, 'B01002_001E': 33.9, 'B19301_001E': 22167.0, 'B17001_002E': 11350.0, 'B23025_005E': 3477.0, 'state': '49', 'place': '65330'}, {'NAME': 'Salt Lake City city, Utah', 'B19013_001E': 45862.0, 'B01003_001E': 188141.0, 'B01002_001E': 31.4, 'B19301_001E': 28137.0, 'B17001_002E': 36752.0, 'B23025_005E': 8959.0, 'state': '49', 'place': '67000'}, {'NAME': 'Sandy city, Utah', 'B19013_001E': 76904.0, 'B01003_001E': 88672.0, 'B01002_001E': 34.0, 'B19301_001E': 30952.0, 'B17001_002E': 6899.0, 'B23025_005E': 2944.0, 'state': '49', 'place': '67440'}, {'NAME': 'West Jordan city, Utah', 'B19013_001E': 67308.0, 'B01003_001E': 106118.0, 'B01002_001E': 28.7, 'B19301_001E': 22303.0, 'B17001_002E': 9421.0, 'B23025_005E': 4403.0, 'state': '49', 'place': '82950'}, {'NAME': 'West Valley City city, Utah', 'B19013_001E': 52389.0, 'B01003_001E': 130843.0, 'B01002_001E': 29.7, 'B19301_001E': 17934.0, 'B17001_002E': 24819.0, 'B23025_005E': 6582.0, 'state': '49', 'place': '83470'}, {'NAME': 'Burlington city, Vermont', 'B19013_001E': 42677.0, 'B01003_001E': 42331.0, 'B01002_001E': 27.5, 'B19301_001E': 25441.0, 'B17001_002E': 9036.0, 'B23025_005E': 2228.0, 'state': '50', 'place': '10675'}, {'NAME': 'Alexandria city, Virginia', 'B19013_001E': 85706.0, 'B01003_001E': 143684.0, 'B01002_001E': 35.7, 'B19301_001E': 54608.0, 'B17001_002E': 11980.0, 'B23025_005E': 4642.0, 'state': '51', 'place': '01000'}, {'NAME': 'Chesapeake city, Virginia', 'B19013_001E': 69743.0, 'B01003_001E': 225597.0, 'B01002_001E': 36.6, 'B19301_001E': 29905.0, 'B17001_002E': 18714.0, 'B23025_005E': 8510.0, 'state': '51', 'place': '16000'}, {'NAME': 'Hampton city, Virginia', 'B19013_001E': 50705.0, 'B01003_001E': 136957.0, 'B01002_001E': 35.5, 'B19301_001E': 25247.0, 'B17001_002E': 19618.0, 'B23025_005E': 7196.0, 'state': '51', 'place': '35000'}, {'NAME': 'Lynchburg city, Virginia', 'B19013_001E': 38138.0, 'B01003_001E': 76467.0, 'B01002_001E': 29.5, 'B19301_001E': 21440.0, 'B17001_002E': 16550.0, 'B23025_005E': 4319.0, 'state': '51', 'place': '47672'}, {'NAME': 'Newport News city, Virginia', 'B19013_001E': 51027.0, 'B01003_001E': 181025.0, 'B01002_001E': 32.5, 'B19301_001E': 25310.0, 'B17001_002E': 26163.0, 'B23025_005E': 8923.0, 'state': '51', 'place': '56000'}, {'NAME': 'Norfolk city, Virginia', 'B19013_001E': 44747.0, 'B01003_001E': 244090.0, 'B01002_001E': 29.8, 'B19301_001E': 24659.0, 'B17001_002E': 42580.0, 'B23025_005E': 13885.0, 'state': '51', 'place': '57000'}, {'NAME': 'Portsmouth city, Virginia', 'B19013_001E': 46166.0, 'B01003_001E': 95901.0, 'B01002_001E': 35.2, 'B19301_001E': 23138.0, 'B17001_002E': 16988.0, 'B23025_005E': 4849.0, 'state': '51', 'place': '64000'}, {'NAME': 'Richmond city, Virginia', 'B19013_001E': 40496.0, 'B01003_001E': 207878.0, 'B01002_001E': 32.6, 'B19301_001E': 27184.0, 'B17001_002E': 50681.0, 'B23025_005E': 12509.0, 'state': '51', 'place': '67000'}, {'NAME': 'Roanoke city, Virginia', 'B19013_001E': 38145.0, 'B01003_001E': 97355.0, 'B01002_001E': 38.2, 'B19301_001E': 23295.0, 'B17001_002E': 21360.0, 'B23025_005E': 4170.0, 'state': '51', 'place': '68000'}, {'NAME': 'Suffolk city, Virginia', 'B19013_001E': 66085.0, 'B01003_001E': 84842.0, 'B01002_001E': 38.1, 'B19301_001E': 29135.0, 'B17001_002E': 9528.0, 'B23025_005E': 3612.0, 'state': '51', 'place': '76432'}, {'NAME': 'Virginia Beach city, Virginia', 'B19013_001E': 65219.0, 'B01003_001E': 442151.0, 'B01002_001E': 34.9, 'B19301_001E': 31934.0, 'B17001_002E': 33928.0, 'B23025_005E': 14647.0, 'state': '51', 'place': '82000'}, {'NAME': 'Auburn city, Washington', 'B19013_001E': 55483.0, 'B01003_001E': 71846.0, 'B01002_001E': 35.9, 'B19301_001E': 26807.0, 'B17001_002E': 11397.0, 'B23025_005E': 4106.0, 'state': '53', 'place': '03180'}, {'NAME': 'Bellevue city, Washington', 'B19013_001E': 90333.0, 'B01003_001E': 129209.0, 'B01002_001E': 37.8, 'B19301_001E': 48620.0, 'B17001_002E': 9826.0, 'B23025_005E': 5211.0, 'state': '53', 'place': '05210'}, {'NAME': 'Bellingham city, Washington', 'B19013_001E': 40648.0, 'B01003_001E': 81576.0, 'B01002_001E': 30.9, 'B19301_001E': 24266.0, 'B17001_002E': 18574.0, 'B23025_005E': 4677.0, 'state': '53', 'place': '05280'}, {'NAME': 'Everett city, Washington', 'B19013_001E': 47482.0, 'B01003_001E': 103918.0, 'B01002_001E': 34.6, 'B19301_001E': 25478.0, 'B17001_002E': 17073.0, 'B23025_005E': 6298.0, 'state': '53', 'place': '22640'}, {'NAME': 'Federal Way city, Washington', 'B19013_001E': 55872.0, 'B01003_001E': 90720.0, 'B01002_001E': 35.1, 'B19301_001E': 26508.0, 'B17001_002E': 14523.0, 'B23025_005E': 4775.0, 'state': '53', 'place': '23515'}, {'NAME': 'Kennewick city, Washington', 'B19013_001E': 51510.0, 'B01003_001E': 74969.0, 'B01002_001E': 32.6, 'B19301_001E': 24669.0, 'B17001_002E': 12644.0, 'B23025_005E': 2649.0, 'state': '53', 'place': '35275'}, {'NAME': 'Kent city, Washington', 'B19013_001E': 57553.0, 'B01003_001E': 115703.0, 'B01002_001E': 33.2, 'B19301_001E': 25137.0, 'B17001_002E': 19660.0, 'B23025_005E': 5693.0, 'state': '53', 'place': '35415'}, {'NAME': 'Renton city, Washington', 'B19013_001E': 64141.0, 'B01003_001E': 93601.0, 'B01002_001E': 35.5, 'B19301_001E': 31124.0, 'B17001_002E': 11601.0, 'B23025_005E': 4617.0, 'state': '53', 'place': '57745'}, {'NAME': 'Seattle city, Washington', 'B19013_001E': 65277.0, 'B01003_001E': 624681.0, 'B01002_001E': 36.1, 'B19301_001E': 43237.0, 'B17001_002E': 82513.0, 'B23025_005E': 27019.0, 'state': '53', 'place': '63000'}, {'NAME': 'Spokane city, Washington', 'B19013_001E': 42092.0, 'B01003_001E': 209478.0, 'B01002_001E': 35.2, 'B19301_001E': 23965.0, 'B17001_002E': 39067.0, 'B23025_005E': 11333.0, 'state': '53', 'place': '67000'}, {'NAME': 'Spokane Valley city, Washington', 'B19013_001E': 47897.0, 'B01003_001E': 90385.0, 'B01002_001E': 38.3, 'B19301_001E': 23886.0, 'B17001_002E': 13032.0, 'B23025_005E': 4759.0, 'state': '53', 'place': '67167'}, {'NAME': 'Tacoma city, Washington', 'B19013_001E': 50503.0, 'B01003_001E': 200890.0, 'B01002_001E': 35.3, 'B19301_001E': 26147.0, 'B17001_002E': 35120.0, 'B23025_005E': 12045.0, 'state': '53', 'place': '70000'}, {'NAME': 'Vancouver city, Washington', 'B19013_001E': 48979.0, 'B01003_001E': 164111.0, 'B01002_001E': 36.6, 'B19301_001E': 25871.0, 'B17001_002E': 26758.0, 'B23025_005E': 10315.0, 'state': '53', 'place': '74060'}, {'NAME': 'Yakima city, Washington', 'B19013_001E': 39462.0, 'B01003_001E': 92082.0, 'B01002_001E': 33.0, 'B19301_001E': 19908.0, 'B17001_002E': 21835.0, 'B23025_005E': 4987.0, 'state': '53', 'place': '80010'}, {'NAME': 'Charleston city, West Virginia', 'B19013_001E': 48527.0, 'B01003_001E': 51135.0, 'B01002_001E': 41.5, 'B19301_001E': 36334.0, 'B17001_002E': 9154.0, 'B23025_005E': 1984.0, 'state': '54', 'place': '14600'}, {'NAME': 'Appleton city, Wisconsin', 'B19013_001E': 53183.0, 'B01003_001E': 72923.0, 'B01002_001E': 35.8, 'B19301_001E': 27246.0, 'B17001_002E': 7996.0, 'B23025_005E': 2121.0, 'state': '55', 'place': '02375'}, {'NAME': 'Green Bay city, Wisconsin', 'B19013_001E': 42427.0, 'B01003_001E': 104393.0, 'B01002_001E': 34.0, 'B19301_001E': 23897.0, 'B17001_002E': 17922.0, 'B23025_005E': 5058.0, 'state': '55', 'place': '31000'}, {'NAME': 'Kenosha city, Wisconsin', 'B19013_001E': 48643.0, 'B01003_001E': 99535.0, 'B01002_001E': 34.1, 'B19301_001E': 23179.0, 'B17001_002E': 17804.0, 'B23025_005E': 6447.0, 'state': '55', 'place': '39225'}, {'NAME': 'Madison city, Wisconsin', 'B19013_001E': 53464.0, 'B01003_001E': 237395.0, 'B01002_001E': 30.8, 'B19301_001E': 31322.0, 'B17001_002E': 43981.0, 'B23025_005E': 9256.0, 'state': '55', 'place': '48000'}, {'NAME': 'Milwaukee city, Wisconsin', 'B19013_001E': 35467.0, 'B01003_001E': 596459.0, 'B01002_001E': 30.6, 'B19301_001E': 19229.0, 'B17001_002E': 168664.0, 'B23025_005E': 41045.0, 'state': '55', 'place': '53000'}, {'NAME': 'Racine city, Wisconsin', 'B19013_001E': 38072.0, 'B01003_001E': 78548.0, 'B01002_001E': 33.6, 'B19301_001E': 20000.0, 'B17001_002E': 17621.0, 'B23025_005E': 5375.0, 'state': '55', 'place': '66000'}, {'NAME': 'Waukesha city, Wisconsin', 'B19013_001E': 57802.0, 'B01003_001E': 70775.0, 'B01002_001E': 34.0, 'B19301_001E': 28920.0, 'B17001_002E': 7912.0, 'B23025_005E': 2710.0, 'state': '55', 'place': '84250'}, {'NAME': 'Cheyenne city, Wyoming', 'B19013_001E': 52848.0, 'B01003_001E': 60528.0, 'B01002_001E': 35.0, 'B19301_001E': 27717.0, 'B17001_002E': 7255.0, 'B23025_005E': 1892.0, 'state': '56', 'place': '13900'}]

# print("This is the example data")
# print(example_data)
# print("")
# print("Pretty print of example data")
# pprint(example_data)
print("")

# # Convert to DataFrame
# census_data_test_fromrecords = pd.DataFrame.from_records(example_data)
# census_data_test_fromdict = pd.DataFrame.from_dict(example_data)
census_data_test_regular = pd.DataFrame(example_data)

census_data_test_regular.head()


# ## Restore CityFIPS to Census Data

# In[188]:


# Restore CityFIPS
for index, row in census_data_test_regular.iterrows():
    state = row['state']
    state = str(state)
    place = row['place']
    place = str(place)
    # Make CityFIPS again
    census_data_test_regular.loc[index, "CityFIPS"] = state+place
census_data_test_regular.head()


# In[189]:


# Final Census DataFrame
# Column Reordering
census_pd = census_data_test_regular.rename(columns={
                                    "B01003_001E": "Population",
                                    "B01002_001E": "Median Age",
                                    "B19013_001E": "Household Income",
                                    "B19301_001E": "Per Capita Income",
                                    "B17001_002E": "Poverty Count",
                                    "B23025_005E": "Unemployment Count",
                                    "NAME": "Name", 
                                    "state": "State",
                                    "place": "Place",
                                    "CityFIPS": "CityFIPS"
                                })

# Add in Poverty Rate (Poverty Count / Population)
census_pd["Poverty Rate"] = 100 *     census_pd["Poverty Count"].astype(
        int) / census_pd["Population"].astype(int)

# Add in Employment Rate (Employment Count / Population)
census_pd["Unemployment Rate"] = 100 *     census_pd["Unemployment Count"].astype(
        int) / census_pd["Population"].astype(int)

# Final DataFrame
census_pd = census_pd[["State", 
                       "Place",
                       "CityFIPS",
                       "Name", 
                       "Population", 
                       "Median Age", 
                       "Household Income",
                       "Per Capita Income", 
                       "Poverty Count", 
                       "Poverty Rate", 
                       "Unemployment Rate"
                      ]]

census_pd.head()


# In[ ]:


# census dataframe to CSV
census_pd.to_csv("output/census_pd.csv")


# # Manipulate and Merge DataFrames

# ## 500 Cities Dataframe

# In[221]:


cities_df.head(2)


# In[ ]:


cities_df.count()


# In[222]:


# Modified Cities Dataframe
cities_df_modified = cities_df

# Add in Individuals Affected = (Data_Value/100) * PopulationCount
cities_df_modified["Count_of_Individuals"] = (cities_df["Data_Value"] / 100) * cities_df["PopulationCount"]
cities_df_modified.head(2)


# ## Just the Cities DataFrame

# In[191]:


just_cities.head()


# In[ ]:


just_cities.count()


# ## Change CityFIPS to 7 digits, no decimal

# In[215]:


# Make a copy of dataframe for modifications
just_cities_modified = just_cities
just_cities_modified.head()

# Convert CityFIPS to string
just_cities_modified = just_cities_modified.astype({"CityFIPS": str})
just_cities_modified.head()

# Remove CityFIPS decimal place
just_cities_modified["CityFIPS"] = just_cities_modified["CityFIPS"].replace(".0","")
just_cities_modified.head()

# Convert CityFIPS to integer
just_cities_modified["CityFIPS"] = pd.to_numeric(just_cities_modified["CityFIPS"])
just_cities_modified.head()


# ## Weather Dataframe

# In[209]:


weather_df.head()


# In[ ]:


weather_df.count()


# In[210]:


# Make a copy of Weather dataframe for modifications
weather_df_modified = weather_df
weather_df_modified.head()

# Convert CityFIPS to integer
weather_df_modified["CityFIPS"] = pd.to_numeric(weather_df_modified["CityFIPS"])
weather_df_modified.head()

# Remove CityFIPS decimal place
weather_df_modified["CityFIPS"] = weather_df_modified["CityFIPS"].replace(".0","")
weather_df_modified.head()


# In[205]:


weather_unfound_df.head()


# In[ ]:


weather_unfound_df.count()


# In[206]:


# Make a copy of Weather dataframe for modifications
weather_unfound_df_modified = weather_unfound_df
weather_unfound_df_modified.head()

# Convert CityFIPS to integer
weather_unfound_df_modified["CityFIPS"] = pd.to_numeric(weather_unfound_df_modified["CityFIPS"])
weather_unfound_df_modified.head()


# ## Census Dataframe

# In[272]:


census_pd.head()


# In[ ]:


census_pd.count()


# In[357]:


# Make a copy of Weather dataframe for modifications
census_pd_modified = census_pd
census_pd_modified.head()

# Convert CityFIPS to integer
census_pd_modified["CityFIPS"] = pd.to_numeric(census_pd_modified["CityFIPS"])
census_pd_modified.head()

# Remove duplicate CityFIPS
census_pd_modified.drop_duplicates(subset ="CityFIPS")
census_pd_modified.count()

# only_georgia = census_pd_modified.loc[census_pd_modified["State"] == "13",:]


# # Merge DataFrames

# ```Python
# # Merging
# # Merge two dataframes using an inner join
# # inner (is the default) it only brings together things in both tables
# merged_table = pd.merge(one_df, two_df, on="column_to_merge")
# 
# #can also take different methods of merging
# # outer - brings everything together
# merged_table = pd.merge(one_df, two_df, on="column_to_merge", how="outer")
# # left and right - right join will cause it to bring in all the data for the right table, but only brings in left data if it matches
# merged_table = pd.merge(one_df, two_df, on="column_to_merge", how="left")
# merged_table = pd.merge(one_df, two_df, on="column_to_merge", how="right")
# 
# # Rename columns so that they are differentiated
# merge_table = merge_table.rename(columns=
#     {'Open_x': 'Bitcoin Open', 'Open_y': 'Dash Open'})
# ```

# ## Weather & Census Merge

# In[217]:


merged_wc = pd.merge(weather_df_modified, census_pd_modified, on="CityFIPS", how="outer")
merged_wc.head()


# In[ ]:


merged_wc.count()


# ## (Weather & Census) + 500 cities Merge

# In[219]:


merged_wc5 = pd.merge(merged_wc, cities_df_modified, on="CityFIPS", how="outer")
merged_wc5.head()


# In[ ]:


merged_wc5.count()


# ## Merged DataFrame to CSV

# In[220]:


# Merged dataframe to CSV
merged_wc5.to_csv("output/merged_wc5.csv")

