import streamlit as st
import folium
from rain_prediction import run_predictionpage
from rain_forecast import run_weather_forecast
from streamlit_option_menu import option_menu

def run_apps():

   with st.sidebar:
# Sidebar configuration
    st.sidebar.title("Main Menu")

# the options
    options = ["Weather Forecast","Precipitation Predictions"]

# Selectbox for menu 
    selected = option_menu(
      menu_title="Select an option",
      options=options,
    #   icons=["weather", "rain"],
      menu_icon="cast",
      default_index = 0,
    #   orientation = "horizontal"
    )

   if selected == "Weather Forecast":
       run_weather_forecast()
   elif selected == "Precipitation Predictions":
       run_predictionpage()


run_apps()



#/home/codespace/.local/lib/python3.10/site-packages/bin/streamlit run main.py






