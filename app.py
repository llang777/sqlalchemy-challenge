# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
app = Flask(__name__)
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        all()

    # Close the session
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the stations
    results = session.query(Station.station).all()

    session.close()

    # Convert the query results to a list
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.id).desc())\
        .first()[0]

    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(Measurement.date)\
        .filter(Measurement.station == most_active_station)\
        .order_by(Measurement.date.desc())\
        .first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most-active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    session.close()

    # Convert the query results to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query to calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .all()

    session.close()

    # Convert query results to a list of dictionaries
    temp_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query to calculate TMIN, TAVG, and TMAX from start to end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .all()

    session.close()

    # Convert query results to a list of dictionaries
    temp_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run()