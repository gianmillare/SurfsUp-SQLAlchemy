# Dependencies
import sqlalchemy
import numpy as np
import pandas as pd
import datetime as dt

from datetime import datetime, timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect,func

from flask import Flask, jsonify

# App Set-Up
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# APP: Using Flask and JSONIFY to create routes
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return ("Welcome!! Please Choose one of the Options Below:<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Build the query for precipitation and JSON it"""
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    all_prcp = []
    
    for date, prcp in results:
        dictprcp = {}
        dictprcp["date"] = date
        dictprcp["prcp"] = prcp
        all_prcp.append(dictprcp)
    
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    results = session.query(Station.station).all()
    
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    one_year_ago = dt.date(2017,8,23) - timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > one_year_ago).all()
    session.close()
    # Return a JSON list of Temperature Observations (tobs) for the previous year
    temp = list(np.ravel(results))
    
    return jsonify(temp)
    
@app.route("/api/v1.0/<start>")
def startdate(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    # https://www.programcreek.com/python/example/54621/datetime.datetime.strptime
    Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
    
    minmaxavg = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
                              func.avg(Measurement.tobs)).filter(Measurement.date >= Start_Date).all()
    
    session.close()
    
    minmaxavg_start = list(np.ravel(minmaxavg))
    
    return jsonify(minmaxavg_start)

@app.route("/api/v1.0/<start>/<end>")
def starttoend(start, end):
    
    Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
    End_Date = dt.datetime.strptime(end,"%Y-%m-%d")
    
    minmaxavg = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
                              func.avg(Measurement.tobs)).filter(Measurement.date.between(Start_Date, End_Date)).all()
    
    session.close()
    
    minmaxavg_starttoend = list(np.ravel(minmaxavg))
    
    return jsonify(minmaxavg_starttoend)

if __name__ == '__main__':
    app.run(debug=True)