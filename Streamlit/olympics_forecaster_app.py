import streamlit as st
import pandas as pd
from pathlib import Path
import pydeck as pdk
from urllib.error import URLError

st.title('Olympics Forecaster App')

medal_count_quality_df = pd.read_csv(Path('../Resources/medal_count_quality.csv'), index_col=False)
trend_plot_df = pd.read_csv(Path('../Resources/trend_plot.csv'))
all_time_count_df = pd.read_csv(Path('../Resources/all_time_count.csv'))


st.sidebar.title("Winter Olympics Forecaster App")
user_menu = st.sidebar.radio(
    'Select an option',
    ('Overview', 'Overall Medal Count Prediction', 'Sports Betting Analysis', 'Event Analysis', 'Historic Medal Count Visualizations')
)

if user_menu == 'Historic Medal Count Visualizations':

    st.title('Historic Medal Count Visualizations')

    try:
        ALL_LAYERS = {
            "Gold": pdk.Layer(
            "ColumnLayer",
            data=all_time_count_df,
            get_position=["Lon", "Lat"],
            get_elevation="Gold_x",
            radius=200,
            elevation_scale=40,
            elevation_range=[0, 1000],
            extruded=True,
             ),


            "Silver": pdk.Layer(
            "SilverLayer",
            data=all_time_count_df,
            get_position=["lon", "lat"],
            get_color=[200, 30, 0, 160],
            get_radius="[exits]",
            radius_scale=0.05,
            ),

            "Bronze": pdk.Layer(
            "BronzeLayer",
            data=all_time_count_df,
            get_position=["lon", "lat"],
            get_text="name",
            get_color=[0, 0, 0, 200],
            get_size=15,
            get_alignment_baseline="'bottom'",
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
                                "longitude": 31.657627, "zoom": 1, "pitch": 50},
                layers=selected_layers,
            ))
        else:
            st.error("Please choose at least one layer above.")

    except URLError as e:
        st.error("""
            **This demo requires internet access.**

            Connection error: %s
        """ % e.reason)