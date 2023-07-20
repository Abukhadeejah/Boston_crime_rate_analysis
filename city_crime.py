import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import numpy as np
from PIL import Image
import shutil

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

