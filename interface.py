import streamlit as st
import pandas as pd
import plotly.express as px

st.title("CCR GmbH : RF Plasma Source Comparison Dashboard")

# Read the csv file
data = pd.read_excel(r"C:\Users\V.Ravavarapu\PycharmProjects\PythonProject_data\plasma_sources.xlsx")

# Clean column names
data.columns = data.columns.str.strip().str.lower()

st.write("Detected columns:", data.columns)

st.sidebar.header("Filters")

design_filter = st.sidebar.multiselect(
    "Select RF Design",
    options=data["design"].unique(),
    default=data["design"].unique()
)

filtered_data = data[data["design"].isin(design_filter)]

st.subheader("Dataset")
st.dataframe(filtered_data)

st.subheader("Ion Energy vs Current Density")

fig = px.scatter(
    filtered_data,
    x="ion_energy_ev",
    y="current_density_macm2",
    color="design",
    hover_data=["source_id"]
)

st.plotly_chart(fig)