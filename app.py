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

# references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# session link
session = Session(engine)

#################################################
# Flask Setup
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to climate analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

## route for precip
@app.route("/api/v1.0/precipitation")
def precipitation():
    # session link
    session = Session(engine)

    # calc date one year ago from last data point in database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # query to retrieve data and precip scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        all()

    # close
    session.close()

    # convert the query results to dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

## route for stations
@app.route("/api/v1.0/stations")
def stations():
    # session link
    session = Session(engine)

    # query to retrieve stations
    results = session.query(Station.station).all()

    session.close()

    # convert query results to list
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)

## route for tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # session link
    session = Session(engine)

    # most active station
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.id).desc())\
        .first()[0]

    # calc date one year ago from last data point in database
    last_date = session.query(Measurement.date)\
        .filter(Measurement.station == most_active_station)\
        .order_by(Measurement.date.desc())\
        .first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    one_year_ago = last_date - dt.timedelta(days=365)

    # query dates and temp observations of the most active station for previous year of data
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    session.close()

    # convert query results to list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(tobs_list)

## route for start date
@app.route("/api/v1.0/<start>")
def temp_start(start):
    # session link
    session = Session(engine)

    try:
        # validate and convert start date
        valid_start = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # calculate TMIN, TAVG, and TMAX for dates greater than or equal to start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= valid_start)\
        .all()

    session.close()

    # check if results are empty
    if not results or not all(results[0]):
        return jsonify({"error": "No data found for the given start date."}), 404

    # convert query to list of dictionaries
    temp_data = [{"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}]

    return jsonify(temp_data)


## Route for start and end date
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    # session link
    session = Session(engine)

    # calculate TMIN, TAVG, and TMAX from start to end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .all()

    session.close()

    # convert query results to list of dictionaries
    temp_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run()