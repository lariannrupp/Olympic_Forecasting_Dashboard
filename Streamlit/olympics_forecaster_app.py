

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

trend_plot_df = pd.read_csv(Path('../Resources/trend_plot.csv'))
all_time_count_df = pd.read_csv(Path('../Resources/all_time_count.csv'))
beijing_total_medal_count_forecast_df = pd.read_csv(Path('../Resources/beijing_total_medal_count_forecast.csv'))
all_winter_medals_df = pd.read_csv(Path("../Resources/all_winter_medals_locations_gsb.csv"))
medal_summary_stats_df = pd.read_csv(Path("../Resources/medal_summary_stats.csv"))
medal_quality_df = pd.read_csv(Path('../Resources/medal_quality.csv'))
temp_only_df = pd.read_csv(Path('../Resources/temp_only.csv'))




# Create sidebar and title

logo = Image.open("../Images/olympics_app_logo.jpg")
# Image credit, Creative Commons License: https://www.maxpixel.net/Russia-Winter-Olympics-Olympiad-Sochi-2014-262145

st.image(logo)

st.sidebar.title("Winter Olympics Forecaster App")
user_menu = st.sidebar.radio(
    'Select an option',
    ('Overview', 'Overall Medal Count Prediction', 'Sports Betting Analysis', 'Historic Medal Count World Map', 'Temperature Data')
)


# OVERVIEW

if user_menu == 'Overview':
    st.title('Overview')

    st.markdown('The objective of this project is to predict the medal count for the 2022 Winter Olympics in a user friendly interface')

    st.subheader('Team')
    st.markdown('This project was created in conjunction with UC Berkeley Extension by Rachel Bates, Daniel English, Lari Rupp, and Jose Viana-Prieto')
    st.markdown('---')

    ucb_logo = Image.open("../Images/ucb_logo.jpg")
    # Image credit, https://www.businesswire.com/news/home/20180626006239/en/UC-Berkeley-Extension-Announces-Global-Alumni-Partnership
    st.image(ucb_logo)



# OVERALL MEDAL COUNT PREDICTION

# Add a description of the process to get the df 


if user_menu == 'Overall Medal Count Prediction':
    st.title('Overall Medal Count Prediction')

    st.markdown("Historical Winter Olympics Medal data was run through the Prophet forecasting tool, and the following outcome was predicted for the 2022 Beijing Winter Olympics Games:")
    st.dataframe(beijing_total_medal_count_forecast_df)

    st.markdown('')
    st.markdown('---')
    st.markdown('')


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


# SPORTS BETTING ANALYSIS
if user_menu == 'Sports Betting Analysis':

    st.title('Sports Betting Analysis')
    st.markdown('Total Beijing Winter Olympic medal numbers were imported and compared with team predicted medal counts.')

    st.markdown('')
    st.markdown('')

    st.image('../Images/total_number_of_medals_with_projected_totals.jpg', caption='Total Number of Medals with Projected Totals')

    st.markdown('')
    st.markdown('')

    st.markdown('Total Predictions from the Prophet forcasting tool were calculated to produce gambling odds.')
    st.image('../Images/projected_medals_with_calculations.jpg', caption='Projected Medal Count with Odds Calculations')

    st.markdown('')
    st.markdown('')

    st.markdown('American Odds were imported from Odds Shark website and calculated to produce numbers for UK and European odds')
    st.image('../Images/odds_shark_odds_with_calculations.jpg', caption='Odds Shark American Odds with Calculations for UK and European')

    st.markdown('')
    st.markdown('')

    st.markdown('Odds Shark Odds were charted to compare with team odds calculations')
    st.image('../Images/odds_shark_odds_comparison.jpg', caption='Odds Shark Odds with Team Predictions')


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
                map_style="mapbox://styles/skrhee/ckbtiaefh0wrr1hp7h4ya3zy4",
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

    st.subheader('Summary Statistics of Historic Medal Data')
    st.dataframe(medal_summary_stats_df)

    st.markdown("---")

    st.subheader('Box Plot of Historic Medal Quality')
    box_plot = medal_quality_df.hvplot.box(y=['Medal Rank'], height=300, width=600, legend=False, title='Medal Rank with Gold=1, Silver=2, Bronze=3', invert=True)
    st.bokeh_chart(hv.render(box_plot, backend='bokeh'))



if user_menu == 'Temperature Data':

    st.title('Temperature Data')

    st.subheader('Temperature Around The World')

    temp_chart= temp_only_df.hvplot(kind='bar', title= 'Average Annual Temperatures', x = 'Country Name', y = 'Avg Annual Temp (Celsius)', rot=90, height=450, width=900)

    st.bokeh_chart(hv.render(temp_chart, backend='bokeh'))