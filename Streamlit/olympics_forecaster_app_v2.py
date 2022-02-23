

'''

Project 1 - Olympics Forecaster App


'''



# Imports

import streamlit as st
import pandas as pd
from pathlib import Path
import pydeck as pdk
from urllib.error import URLError
from PIL import Image
import hvplot.pandas
import holoviews as hv
hv.extension('bokeh', logo=False)



# Read in the csv's that will be displayed in the app

medal_count_quality_df = pd.read_csv(Path('../Resources/medal_count_quality.csv'), index_col=False)
trend_plot_df = pd.read_csv(Path('../Resources/trend_plot.csv'))
all_time_count_df = pd.read_csv(Path('../Resources/all_time_count.csv'))
beijing_total_medal_count_forecast_df = pd.read_csv(Path('../Resources/beijing_total_medal_count_forecast.csv'))
all_winter_medals_df = pd.read_csv(Path("../Resources/all_winter_medals_locations_gsb.csv"))
medal_summary_stats_df = pd.read_csv(Path("../Resources/medal_summary_stats.csv"))



# Create sidebar and title

logo = Image.open("../Images/olympics_app_logo.jpg")
# Image credit, Creative Commons License: https://www.maxpixel.net/Russia-Winter-Olympics-Olympiad-Sochi-2014-262145

st.image(logo)

st.sidebar.title("Winter Olympics Forecaster App")
user_menu = st.sidebar.radio(
    'Select an option',
    ('Overview', 'Overall Medal Count Prediction', 'Sports Betting Analysis', 'Event Analysis', 'Historic Medal Count World Map')
)



# OVERALL MEDAL COUNT PREDICTION

# Add a description of the process to get the df 


if user_menu == 'Overall Medal Count Prediction':
    st.title('Overall Medal Count Prediction')

    st.markdown("Historical Winter Olympics Medal data was run through the Prophet forecasting tool, and the following outcome was predicted for the 2022 Beijing Winter Olympics Games:")
    st.dataframe(beijing_total_medal_count_forecast_df)
    st.markdown('---')


    st.header("Creating the Predictive Model")
    st.subheader("Inital Data Selection")
    st.markdown('The team started with a csv of medal data from data.world user @vizwiz. Data for the 2018 Winter Olympics was added from Olympedia.com. Additional geographic coordinate data was added for capitol cities of competing nations. A boolean filter was created for each category of medal so that medals could be summed by a groupby function.')
    st.dataframe(all_winter_medals_df)
    
    st.subheader("Plot the Historical Medal Data")
    st.markdown("The starting csv was cleaned and prepared into a dataframe that could be used for an hv plot of historical medal data, by country.")
    st.markdown("To view the trend plots, please select a country from the sidebar.")

    country_list = trend_plot_df['Country'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.sidebar.selectbox('Select Country', country_list)

    overlay_gsbt= trend_plot_df.hvplot(x='Year', y=['Gold_x', 'Silver_x', 'Bronze_x', 'Total_x'], groupby='Country', height=375, width=900, value_label='Number of Medals')
    
    st.bokeh_chart(hv.render(overlay_gsbt, backend='bokeh'))

 


    st.subheader("Forecast 2022 Results With a Prophet Simulation")
    st.markdown("The data was run through a 4 year simulation with the Prophet forecasting tool for each country and medal ranking. This is an example of China Gold Medals:")
    code = '''
# Clone the trend_plot_df into a new dataframe and reset the index
kl_df=trend_plot_df
kl_df=kl_df.reset_index()

# Select data from kl_df into a dataframe the Prophet dependency can read 
# Here is where you input Medal_x into the function for GSBT predictions
all_countries_df=kl_df.pivot(index='Year', columns='Country', values='Gold_x').reset_index(drop=False)

all_countries_df.head()

# Clean the Year column into date time format
all_countries_df['Year']=pd.to_datetime(all_countries_df['Year'], format='%Y')

# Select the columns from the all_countries_df that will be used in the Prophet simulation
# Here is where you input 'Country' into the function for GSBT predictions
one_df=all_countries_df[['Year', 'China']]
# Rename the columns so they are in syntax of the Prophet documentation
one_df.columns=['ds', 'y']

one_df.head()

# Fit the model by instantiating a new Prophet object
model=Prophet()
model.fit(one_df)

# Get a suitable dataframe that extends into the future a specified number of days
# Use 4*365 days from the 2018 data
future=model.make_future_dataframe(periods=1461)

# Use the predict method to assign each row in future a predicted value named yhat
forecast = model.predict(future)
# Display only the yhat prediction value for 1461 days from last value in 2018
forecast[['ds', 'yhat']].tail(1)'''


    st.code(code, language='python')


    prophet_china = Image.open("../Images/prophet_china.jpg")
    st.image(prophet_china)
    
    prophet = Image.open("../Images/prophet_image.jpg")
    st.image(prophet)

    st.subheader("Create the Beijing 2022 forecast DataFrame")
    st.markdown("Prophet was run for each cell value and scribed into a final medal count by country and medal ranking, which is displayed at the top of the page.")





# WORLD MAP OF MEDALS


if user_menu == 'Historic Medal Count World Map':

    st.title('Historic Medal Count World Map')

    try:
        ALL_LAYERS = {
            "Gold": pdk.Layer(
            "ColumnLayer",
            data=all_time_count_df,
            get_position=["Lon", "Lat"],
            get_elevation="Gold_x",
            get_color=[255, 215, 0, 200],
            radius=50000,
            elevation_scale=4000,
            elevation_range=[0, 4000],
            extruded=True,
             ),

            "Silver": pdk.Layer(
            "ColumnLayer",
            data=all_time_count_df,
            get_position=["Lon", "Lat"],
            get_elevation="Silver_x",
            get_color=[192, 192, 192, 200],
            radius=50000,
            elevation_scale = 4000,
            elevation_range = [0,4000],
            extruded = True,
            ),

            "Bronze": pdk.Layer(
            "ColumnLayer",
            data=all_time_count_df,
            get_position=["Lon", "Lat"],
            get_elevation="Bronze_x",
            get_color=[205, 127, 50, 200],
            radius=50000,
            elevation_scale = 4000,
            elevation_range = [0,4000],
            extruded = True,
            ),

            "Total Medals": pdk.Layer(
            "ColumnLayer",
            data=all_time_count_df,
            get_position=["Lon", "Lat"],
            get_elevation="Total_x",
            get_color=[255, 0, 0, 200],
            radius=50000,
            elevation_scale=4000,
            elevation_range=[0, 4000],
            extruded=True,
             ),
        
        }
        st.sidebar.markdown('### Map Layers')
        selected_layers = [
            layer for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)]
        if selected_layers:
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={"latitude": 44.777781,
                                "longitude": 31.657627, "zoom": 1, "pitch": 40},
                layers=selected_layers,
            ))
        else:
            st.error("Please choose at least one layer above.")

    except URLError as e:
        st.error("""
            **This demo requires internet access.**

            Connection error: %s
        """ % e.reason)

    st.markdown("---")

    st.subheader('Summary Statistics of Historical Medal Data')
    st.dataframe(medal_summary_stats_df)


