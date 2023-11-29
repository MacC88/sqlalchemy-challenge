# Import the dependencies.
from flask import Flask, jsonify

import warnings
warnings.filterwarnings('ignore')


# create the connection to Flask
app = Flask(__name__)

# List all available api routes
# Define the routes
@app.route('/')
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():

    # Convert the query results from your precipitation analysis to a dictionary
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    all()

    # Defining dataframes
    df = pd.DataFrame(prcp, columns = ['Date', "Precipitation"])
    precip_dict =df.set_index('Date').T.to_dict('list')
    session.close()
    return jsonify(
    precip_dict
 )


@app.route('/api/v1.0/stations')
def stations():
    
    #Return a JSON list of stations from the dataset
    session = Session(engine)
    station_list = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).\
    all()

    # Defining dataframes
    df = pd.DataFrame(station_list, columns = ['Station ID', "Number of Records"])
    station_list_dict =df.set_index('Station ID').T.to_dict('list')
    session.close()
    return jsonify(
    station_list_dict
    )


@app.route('/api/v1.0/tobs')
def tobs():

    #Query the dates and temperature observations of the most-active station for the previous year of data
    session = Session(engine)
    low = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').all()
    high = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').all()
    average = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').all()

    # Defining dataframes
    low_df = pd.DataFrame(low, columns = ["Low Temperature"])
    low_df = low_df.to_json()
    high_df = pd.DataFrame(high, columns = ["High Temperature"])
    high_df = high_df.to_json()
    avg_df = pd.DataFrame(average, columns = ["Average Temperature"])
    avg_df = avg_df.to_json()
    session.close()
    return jsonify(
    low_df,
    high_df,
    avg_df
    )


@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def start_and_stop(start, stop = None):

    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date    
    session = Session(engine)
    standardized = start
    sel = [(func.min(Measurement.tobs)),(func.max(Measurement.tobs)),(func.avg(Measurement.tobs))]
    if not stop:
        start_without_stop = session.query(*sel).filter(func.strftime('%m-%d', Measurement.date) == standardized).all()
        return jsonify (start_without_stop)
    start_with_stop = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()
    return jsonify (start_with_stop)


# Run the app
if __name__ == '__main__':
    app.run(debug=False)