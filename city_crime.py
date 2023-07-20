import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from PIL import Image

image = Image.open('boston.jpg')
st.image(image, caption='Boston')

#Function to load the data and cache it
@st.cache_data
def load_data():
    data = pd.read_csv('Boston_Crime_data.csv')
    return data

#load the data and cache it using Streamlit cache
crime_data = load_data()
