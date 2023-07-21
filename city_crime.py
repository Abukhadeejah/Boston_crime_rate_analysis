import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import numpy as np
from PIL import Image
import shutil
import json

# Copy the original file to a new file
shutil.copy('Boston_Crime_data.csv', 'Boston_Crime_data_with_day_of_month.csv')

image = Image.open('boston.jpg')
st.image(image, caption='Boston')

#Function to load the data and cache it
@st.cache_data
def load_data():
    data = pd.read_csv('Boston_Crime_data_with_day_of_month.csv')
    data['OCCURRED_ON_DATE'] = pd.to_datetime(data['OCCURRED_ON_DATE'])
    data['DAY_OF_MONTH'] = data['OCCURRED_ON_DATE'].dt.day

    # Drop the 'Location' column from the DataFrame
    # data.drop(columns=['Location', 'OCCURRED_ON_DATE'], inplace=True)

    return data

#load the data and cache it using Streamlit cache
crime_data = load_data()

#create a check box to display the raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    load_state = st.text('Loading data...')
    st.write(crime_data)
    load_state.text('Loading completed...')


# Create a Check box to show few summary details.

if st.checkbox('Crime Summary'):
    grp_data = crime_data.copy()
    grp_data['Count'] = 1
    st.subheader('Top 50 Crimes in a Month')
    st.write(pd.DataFrame(grp_data.groupby(['OFFENSE_DESCRIPTION'], sort=False)['Count'].count().rename_axis(["Type of Crime"]).nlargest(50)))
    st.subheader('# of Crimes by Day of Month')
    df = pd.DataFrame(grp_data.groupby(['DAY_OF_MONTH'])['Count'].count().rename_axis(["Day of Month"]))
    df = df.sort_values('Count', ascending=False)
    st.write(df)


# Bar chart to show the Top 10 Crimes using plotly
    st.subheader(" Top 10 Crimes ")
    grp_data = crime_data.copy()
    grp_data['Count'] = 1
    k = pd.DataFrame(grp_data.groupby(['OFFENSE_DESCRIPTION'], sort=False)['STREET'].count().rename_axis(["Type of Crime"]).nlargest(10))
    Crime = pd.Series(k.index[:])
    Count = list(k['STREET'][:])
    Crime_Count = pd.DataFrame(list(zip(Crime, Count)),
                               columns=['Crime', 'Count'])
    fig = px.bar(Crime_Count, x='Crime', y='Count', color='Count',
                 labels={'Crime': 'Crime Type', 'Count': 'Crime Count'})
    st.plotly_chart(fig)


# Slider to select the required day of month to analyse
st.subheader('Crime Location on Map - Select the day of a Month')
Day_filter = st.slider('Select a day of the month', 1, 31, 5)
Crime_Filter = crime_data[crime_data['DAY_OF_MONTH'] == Day_filter]

# Convert the filtered data to GeoJSON format
features = []
for _, row in Crime_Filter.iterrows():
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [row['Long'], row['Lat']]
        },
        'properties': row.fillna('').to_dict()
    }
    features.append(feature)

geojson_data = {
    'type': 'FeatureCollection',
    'features': features
}

# Replace NaN values with null values
geojson_data = json.loads(json.dumps(geojson_data, default=str))

# Create a PyDeck GeoJSONLayer with the GeoJSON data
geojson_layer = pdk.Layer(
    'GeoJsonLayer',
    data=geojson_data,
    get_position='[Long, Lat]',
    get_color='[255, 0, 0]',
    get_radius=50,
    pickable=True,
    auto_highlight=True,
    tooltip={
        'html': '<b>Incident Number:</b> {INCIDENT_NUMBER}<br/>' +
                '<b>Offense Code:</b> {OFFENSE_CODE}<br/>' +
                '<b>Offense Code Group:</b> {OFFENSE_CODE_GROUP}<br/>' +
                '<b>Location:</b> {Location}<br/>' +
                '<b>Date:</b> {OCCURRED_ON_DATE}<br/>' +
                '<b>Day of Month:</b> {DAY_OF_MONTH}'
    }
)

# Set the initial view state for the map
view_state = pdk.ViewState(
    latitude=42.3601,
    longitude=-71.0589,
    zoom=11,
    pitch=50
)

# Create the PyDeck chart
pydeck_chart = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=view_state,
    layers=[geojson_layer]
)

# Display the PyDeck chart using Streamlit
st.pydeck_chart(pydeck_chart)

    

# Histogram to show the no of Crimes by Hour for the selcted day of month.
hist_values = np.histogram(Crime_Filter['HOUR'], bins=24, range=(0, 23))[0]
st.bar_chart(hist_values)
st.write('--------------------------------- No. of Crimes by Hour in a given day ---------------------------------')
st.success("     ")

