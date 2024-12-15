import requests
import streamlit as st
from plotly import graph_objects as go
from streamlit_folium import folium_static
import folium

API_KEY = "9b833c0ea6426b70902aa7a4b1da285c"

# Define the graph generation functions
def bargraph(dates, values, label):
    fig = go.Figure(data=[
        go.Bar(x=dates, y=values, marker_color='crimson')
    ])
    fig.update_layout(xaxis_title="Dates", yaxis_title=label, margin=dict(l=70, r=10, t=80, b=80), font=dict(color="white"))
    st.plotly_chart(fig)

def linegraph(dates, values, label):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=values, name=label))
    fig.update_layout(xaxis_title="Dates", yaxis_title=label, font=dict(color="white"))
    st.plotly_chart(fig)

def get_weather_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"

    current_weather_params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "en"
    }

    forecast_params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "en"
    }

    response_current = requests.get(base_url, params=current_weather_params)
    response_forecast = requests.get(forecast_url, params=forecast_params)

    if response_current.status_code == 200 and response_forecast.status_code == 200:
        current_data = response_current.json()
        forecast_data = response_forecast.json()
        return current_data, forecast_data  
    else:
        st.error(f"Error fetching weather data. Status code: {response_current.status_code} for current weather and {response_forecast.status_code} for forecast data")

def display_weather_forecast(weather_data):
    if weather_data:
        current_data, _ = weather_data
        latitude = current_data['coord']['lat']
        longitude = current_data['coord']['lon']
        m = folium.Map(location=[latitude, longitude], zoom_start=10)
        pop_up_content = f"""
        <b>City:</b> {current_data['name']}<br>
        <b>Country:</b> {current_data['sys']['country']}<br>
        <b>Current Temperature:</b> {current_data['main']['temp']}°C<br>
        <b>Weather:</b> {current_data['weather'][0]['description'].capitalize()}
        """

        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(folium.Html(pop_up_content, script=True)),
            icon=folium.Icon(color='blue')
        ).add_to(m)
    
        st.info(f"""City: {current_data['name']} 
                \nCountry: {current_data['sys']['country']} 
                \nCurrent Temperature: {current_data['main']['temp']}°C 
                \nWeather: {current_data['weather'][0]['description'].capitalize()}""")
        
        return m    

def run_weather_forecast():
    tab1, tab2 = st.tabs(["Weather", "Map"])
    
    with tab1:
        st.header("Weather Conditions",divider='rainbow')
        city = st.text_input("Enter city name", "")
        submit = st.button("Get Weather")

        if submit:
            weather_data = get_weather_data(city)
            if weather_data:
                st.title(f"Weather Updates for {city}:")
                current_data, forecast_data = weather_data

                # Display temperature
                st.markdown(
                    """
                    <style>
                    .weather-block {
                        width: 100%;
                        padding: 10px;
                        background-color: #100720;
                        border-radius: 10px;
                        transition: background-color 0.5s;
                    }

                    .weather-block:hover {
                        background-color: #330033;
                    }

                    .weather-title {
                        color: #fff;
                        font-size: 20px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }

                    .weather-value {
                        color: #fff;
                        font-size: 22px; /* Increased font size for better visibility */
                        margin-bottom: 10px;
                    }

                    .button {
                        width: 100%;
                        padding: 20px; /* Increased padding for larger button */
                        cursor: pointer;
                        color: #fff;
                        font-size: 17px;
                        border-radius: 1rem;
                        border: none;
                        position: relative;
                        background: #100720;
                        transition: all 0.5s;
                    }

                    .button:hover {
                        background: #330033;
                    }

                    .button::after {
                        content: '';
                        width: 100%;
                        height: 100%;
                        background-image: radial-gradient( circle farthest-corner at 10% 20%, rgba(255,94,247,1) 17.8%, rgba(2,245,255,1) 100.2% );
                        filter: blur(15px);
                        z-index: -1;
                        position: absolute;
                        left: 0;
                        top: 0;
                        transition: all 0.5s;
                    }

                    .button:hover::after {
                        transform: scale(1.1);
                        opacity: 0;
                    }

                    .button:active {
                        transform: scale(0.9) rotate(3deg);
                        background: radial-gradient( circle farthest-corner at 10% 20%, rgba(255,94,247,1) 17.8%, rgba(2,245,255,1) 100.2% );
                        transition: 0.5s;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<button class="button"><div class="weather-title">Temperature 🌡</div><div class="weather-value">{}</div></button>'.format(current_data['main']['temp']), unsafe_allow_html=True)
                    st.markdown('<button class="button"><div class="weather-title">Humidity 💧</div><div class="weather-value">{}</div></button>'.format(current_data['main']['humidity']), unsafe_allow_html=True)
                with col2:
                    st.markdown('<button class="button"><div class="weather-title">Pressure 💨</div><div class="weather-value">{}</div></button>'.format(current_data['main']['pressure']), unsafe_allow_html=True)
                    st.markdown('<button class="button"><div class="weather-title">Wind Speed 🍃</div><div class="weather-value">{}</div></button>'.format(current_data['wind']['speed']), unsafe_allow_html=True)
                
                st.info('Live weather data collected from the API')


                dates = []
                maxtemp = []
                mintemp = []
                for forecast in forecast_data['list']:  
                    dates.append(forecast["dt_txt"])
                    maxtemp.append(forecast["main"]["temp_max"])
                    mintemp.append(forecast["main"]["temp_min"])

                linegraph(dates, maxtemp, "Temperature (°C)")
                st.info("Temperature Line Graph")
                bargraph(dates, maxtemp, "Temperature (°C)")
                st.info("Temperature Bar Graph")

                humidity_dates = []
                humidity_values = []
                for forecast in forecast_data['list']:  
                    humidity_dates.append(forecast["dt_txt"])
                    humidity_values.append(forecast["main"]["humidity"])

                linegraph(humidity_dates, humidity_values, "Humidity (%)")
                st.info("Humidity Line Graph")
                bargraph(humidity_dates, humidity_values, "Humidity (%)")
                st.info("Humidity Bar Graph")

                pressure_dates = []
                pressure_values = []
                for forecast in forecast_data['list']:  
                    pressure_dates.append(forecast["dt_txt"])
                    pressure_values.append(forecast["main"]["pressure"])

                linegraph(pressure_dates, pressure_values, "Pressure (hPa)")
                st.info("Pressure Line Graph")
                bargraph(pressure_dates, pressure_values, "Pressure (hPa)")
                st.info("Pressure Bar Graph")

    with tab2:
        st.header("Weather Map",divider='rainbow')
        city = st.text_input("Enter a city name for the map", "")

        if st.button("Show Map"):
            weather_data = get_weather_data(city)
            if weather_data:
                map_display = display_weather_forecast(weather_data)
                if map_display:
                    folium_static(map_display)
                else:
                    st.error("Failed to fetch weather data. Please check the city name and try again.")


if __name__ == "__main__":
    run_weather_forecast()