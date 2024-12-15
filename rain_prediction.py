from ossaudiodev import openmixer
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Load the trained LSTM model
model = load_model('UK_model.h5')

def run_predictionpage():

    city = st.text_input("Enter the Name of the City")   
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    weather_api_key = "556105f4f5f06239d40c226b2f11b769"
    
    # button to fetch and display weather data
    submit = st.button("Get Weather")
    if submit:
        # st.title("Prediction for " + city + " is:")
        with st.spinner('Getting details ...'):
            weather_data = get_weather_data(city, weather_api_key)
            
            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']
            
            if city == 'london' or 'manchester' or 'birmingham' :      
                UK = get_current_weather_data(lat,lon,openmeteo)
                st.info('Data collected from the API')
                st.write(UK)
                
                # past weather data
                y = get_past_weather_data(lat,lon,openmeteo)    
                df = pd.DataFrame(y)            
                df['date'] = pd.to_datetime(df['date'])            
                df = df.set_index('date')
                
                st.title("Past 15 days Precipitation")
                st.line_chart(df)
                st.info('Line chart')
                st.area_chart(df)
                st.info('Line chart')
                
                # Preprocess data and make predictions
                data = get_current_weather_data(lat,lon,openmeteo)
                X = preprocess_data(data)
                
                predictions = make_predictions(X)
                
                # Display results
                st.title("Predictions for next 10 days")
                visualize_predicted(predictions.flatten())
            else:
                # past weather data
                y = get_past_weather_data(lat,lon,openmeteo)    
                df = pd.DataFrame(y)            
                df['date'] = pd.to_datetime(df['date'])            
                df = df.set_index('date')
                
                st.title("Past 15 days Precipitation")
                st.line_chart(df)
                st.info('Line Chart')
                st.area_chart(df)
                st.info('Area chart')
                
                f = get_forecast_weather_data(lat,lon,openmeteo)    
                df = pd.DataFrame(f)            
                df['date'] = pd.to_datetime(df['date'])            
                df = df.set_index('date')
                
                st.title("Prediction for next 10 days Precipitation")
                st.line_chart(df)
                st.info('Line chart')
                st.area_chart(df)
                st.info('Area chart')
                st.info('Predicted through model')


# Function to preprocess input data
def preprocess_data(data):
    # Convert the data dictionary to a pandas DataFrame
    data_df = pd.DataFrame(data)

    data_df['date'] = pd.to_datetime(data_df['date'])
    
    # Extract year, month, day, and hour from the 'date' column
    data_df['year'] = data_df['date'].dt.year
    data_df['month'] = data_df['date'].dt.month
    data_df['day'] = data_df['date'].dt.day
    data_df['hour'] = data_df['date'].dt.hour
    
    # Define the features to use for model input
    features = [
        'year', 'month', 'day', 'hour',
        'temperature_2m', 'relative_humidity_2m',
        'apparent_temperature', 'pressure_msl',
        'surface_pressure', 'cloud_cover',
        'wind_speed_10m', 'wind_direction_10m',
        'wind_gusts_10m', 'latitude', 'longitude'
    ]
    
    # Extract the features from the data DataFrame
    X = data_df[features].values
    
    # Normalize the feature data using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    X = scaler.fit_transform(X)
    
    # Reshape the data to be in the required 3D format for LSTM model input
    X = np.reshape(X, (X.shape[0], 1, X.shape[1]))
    
    return X

            
            
# Function to make predictions
def make_predictions(X):
    predictions = model.predict(X)
    return predictions



# Function to display predicted values in a line chart
def visualize_predicted(predicted):
    df_predicted = pd.DataFrame({
        'Date': pd.date_range(start=pd.Timestamp.now(), periods=10, freq='D'),
        'Predicted': predicted[:10]  # Only take the first 10 predictions
    })
    # Set the 'Date' column as the index
    df_predicted.set_index('Date', inplace=True)
    st.line_chart(df_predicted)
    st.info('Line Chart')
    st.area_chart(df_predicted)
    st.info('Area Chart')
    st.info('Predicted through model')


            
def get_current_weather_data(lat,lon,openmeteo):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "rain", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
        "past_days": 15,
        "forecast_days": 0
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(4).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(5).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(6).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(8).ValuesAsNumpy()
    hourly_wind_gusts_10m = hourly.Variables(9).ValuesAsNumpy()
    
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["rain"] = hourly_rain
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["surface_pressure"] = hourly_surface_pressure
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
    hourly_data["latitude"] = lat
    hourly_data["longitude"] = lon
    
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    
    return hourly_dataframe
    
    
    
def get_past_weather_data(lat,lon,openmeteo):
 # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "rain",
        "past_days": 15,
        "forecast_days": 0
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    hourly = response.Hourly()
    hourly_rain = hourly.Variables(0).ValuesAsNumpy()
   
    
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    

    hourly_data["rain"] = hourly_rain

    past_rain = pd.DataFrame(data = hourly_data)
    
    return past_rain


def get_forecast_weather_data(lat,lon,openmeteo):
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	"latitude": lat,
	"longitude": lon,
	"hourly": "rain",
	"timezone": "GMT",
	"past_days": 0,
	"forecast_days": 10
    }
    
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    daily = response.Daily()
    
    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    dates_with_time = pd.to_datetime(daily_data["date"])
    dates = [date.strftime("%Y-%m-%d") for date in dates_with_time]  
    daily_precipitation_sum = daily.Variables(0).ValuesAsNumpy()
    forecast_data = {"date":dates,"precipitation":daily_precipitation_sum}
 
    return forecast_data  




    
def get_weather_data(city,weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()    
    
    
if __name__ == "__main__":
    run_predictionpage() 
