#!/usr/bin/env python
# coding: utf-8

# In[138]:


# Dependencies
import sqlalchemy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

from datetime import datetime, timedelta
from pandas import DataFrame
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect,func
from matplotlib import style
style.use('fivethirtyeight')

from flask import Flask, jsonify


# # Reflect Tables into SQLAlchemy ORM

# In[139]:


engine = create_engine("sqlite:///../Resources/hawaii.sqlite")


# In[140]:


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# In[141]:


# We can view all of the classes that automap found
Base.classes.keys()


# In[142]:


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[143]:


# Create our session (link) from Python to the DB
session = Session(engine)


# In[144]:


# view the datasets you will be working with
inspector = inspect(engine)
inspector.get_table_names()


# In[145]:


columns_m = inspector.get_columns('measurement')
for row in columns_m:
    print(row['name'], row['type'])


# In[146]:


measurement_df = engine.execute('SELECT * FROM measurement LIMIT 10').fetchall()
measurement_masterdf = pd.DataFrame(measurement_df)
measurement_masterdf.head()


# In[147]:


columns_s = inspector.get_columns('station')
for row in columns_s:
    print(row['name'], row['type'])


# In[148]:


station_df = engine.execute('SELECT * FROM station LIMIT 10').fetchall()
station_masterdf = pd.DataFrame(station_df)
station_masterdf.head()


# # Exploratory Climate Analysis

# In[149]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results
last_12m = session.query(Measurement.date).order_by(Measurement.date.desc()).all()
last12_dataframe = pd.DataFrame(last_12m)
last12_dataframe.head()


# In[150]:


# Calculate the date 1 year ago from the last data point in the database
# https://www.saltycrane.com/blog/2010/10/how-get-date-n-days-ago-python/
one_year_ago = dt.date(2017,8,23) - timedelta(days=365)
one_year_ago


# In[151]:


# Perform a query to retrieve the data and precipitation scores
# Save the query results as a Pandas DataFrame and set the index to the date column
# Sort the dataframe by date
prec_scores = session.query(Measurement.date, Measurement.prcp).            filter(Measurement.date >= '2016-08-23', Measurement.date <= '2017-08-23').            order_by(Measurement.date).all()
df = pd.DataFrame(prec_scores)
master_df = df.sort_values('date')
master_df.head()


# In[152]:


# Use Pandas Plotting with Matplotlib to plot the data
master_df.set_index(master_df["date"],inplace=True)

f, ax = plt.subplots(figsize=(100,25))
plt.bar(master_df["date"], master_df["prcp"])
plt.title("Precipitation by Date")
plt.ylabel("Precipitation Levels")
plt.xlabel("Date")
plt.xticks(rotation = 45)
#plt.tight_layout()
plt.grid(True)

plt.savefig("../Figures/precvsdate.png")

plt.show()


# ![precipitation](Images/precipitation.png)

# In[153]:


# Use Pandas to calcualte the summary statistics for the precipitation data
master_df.describe()


# ![describe](Images/describe.png)

# In[154]:


# Design a query to show how many stations are available in this dataset?
number_of_stations = session.query(Station.station).count()
number_of_stations


# In[155]:


# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).                order_by(func.count(Measurement.station).desc()).all()


# In[156]:


# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?
USC00519281_low = session.query(func.min(Measurement.tobs)).filter(Measurement.station=='USC00519281').all()
USC00519281_low


# In[157]:


USC00519281_high = session.query(func.max(Measurement.tobs)).filter(Measurement.station=='USC00519281').all()
USC00519281_high


# In[158]:


USC00519281_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.station=='USC00519281').all()
USC00519281_avg


# In[159]:


# Just for fun: Here is the lowest, highest, and average of all stations
all_stations = [func.min(Measurement.tobs),
               func.max(Measurement.tobs),
               func.avg(Measurement.tobs)]

session.query(*all_stations).all()


# In[160]:


# Choose the station with the highest number of temperature observations. ---> USC00519281
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
query2 = session.query(Measurement.station, Measurement.date, Measurement.tobs).                                         filter(Measurement.station=='USC00519281').                                         filter(Measurement.date >= one_year_ago).                                         order_by(Measurement.date.desc()).all()
df = pd.DataFrame(query2)
df.head(10)


# In[161]:


# Remaking the query to better fit the histogram
revised = session.query(Measurement.tobs).                            filter(Measurement.station=='USC00519281').                            filter(Measurement.date >= one_year_ago).                            order_by(Measurement.date.desc()).all()

tobs_df = pd.DataFrame(revised)

plt.hist(tobs_df["tobs"], bins=12)
plt.title("USC00519281 Temperature Frequency")
plt.ylabel("Frequency")
plt.xlabel("Temperature")

plt.savefig("../Figures/tempfrequency.png")

plt.show()


# In[162]:


# APP: Using Flask and JSONIFY to create routes
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/names<br/>"
        f"/api/v1.0/passengers"
    )


# In[163]:


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))


# In[164]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.
vacation = calc_temps('2017-07-01', '2017-07-08')
vacation


# In[165]:


# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)


# In[166]:


# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation


# ## Optional Challenge Assignment

# In[167]:


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("01-01")


# In[168]:


# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

# Set the start and end date of the trip

# Use the start and end date to create a range of dates

# Stip off the year and save a list of %m-%d strings

# Loop through the list of %m-%d strings and calculate the normals for each date


# In[169]:


# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index


# In[170]:


# Plot the daily normals as an area plot with `stacked=False`

