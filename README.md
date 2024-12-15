# RainInsight: Rain Prediction and Forecasting

RainInsight is a Streamlit application that provides rain prediction and forecasting for a given location. The application uses an LSTM model to predict rainfall based on historical and current weather data, as well as live weather data from the OpenWeather API. It also provides visualizations using Folium maps to display weather data on a map.

## Features

- Predict rainfall for the next 10 days using a trained LSTM model.
- Visualize predicted rainfall using Streamlit line charts.
- Retrieve and display historical precipitation data for the past 15 days.
- Use the Open-Meteo API to fetch current and forecasted weather data.
- Fetch live weather data using the OpenWeather API.
- Display weather data on a map using Folium maps.
- Cache and retry API requests for improved performance and reliability.

## Requirements

- Python 3.10 or later
- The following Python packages:
    - streamlit
    - numpy
    - pandas
    - scikit-learn
    - keras
    - requests
    - openmeteo-requests
    - requests-cache
    - retry-requests
    - folium

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/your_username/RainInsight.git
    cd RainInsight
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Download the LSTM model (`UK_model.h5`) and place it in the project directory.

## Usage

1. Run the Streamlit application:

    ```bash
    streamlit run rain_prediction.py
    ```

2. Enter the name of the city in the input box and click "Get Weather" to fetch live weather data and make predictions.

3. The application will display predicted rainfall for the next 10 days, live weather data on Folium maps, and historical precipitation data for the past 15 days.

## API Key

The application uses the OpenWeather API and Open-Meteo API to fetch weather data. You will need to provide your own API keys:

- Replace the value of `weather_api_key` in `rain_prediction.py` with your OpenWeather API key.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

