# Import the dependencies.
import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
        return(
            f"Welcome to the Hawaii Climate Analysis API<br/>"
            f"<p>Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start<br/>"
            f"/api/v1.0/start/end<br/>"
            f"<p>'start' and 'end' date format: MMDDYYYY</p>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
        last_twelve = dt.date(2017,8,23) - dt.timedelta(days=365)
        precipitation = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= last_twelve).all()
        session.close()
        prec = {date: prcp for date, prcp in precipitation}
        return jsonify(prec)    

@app.route("/api/v1.0/stations")
def stations():
        results = session.query(Station.station).all()
        session.close()
        stations = list(np.ravel(results))
        return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
        last_twelve = dt.date(2017,8,23) - dt.timedelta(days=365)
        results = session.query(Measurement.tobs).\
                  filter(Measurement.station == 'USC00519281').\
                  filter(Measurement.date >= last_twelve).all()
        session.close()
        print()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
       sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
       if not end:
               start = dt.datetime.strptime(start, "%m%d%Y")
               results = session.query(*sel).\
                         filter(Measurement.date >= start).all()
               session.close()
               temps = list(np.ravel(results))
               return jsonify(temps)
       start = dt.datetime.strptime(start, "%m%d%Y")
       end = dt.datetime.strptime(end, "%m%d%Y")

       results = session.query(*sel).\
                 filter(Measurement.date >= start).\
                 filter(Measurement.date <= end).all()
       session.close()
       temps = list(np.ravel(results))
       return jsonify(temps=temps)

if __name__ == "__main__":
        app.run(debug=True)