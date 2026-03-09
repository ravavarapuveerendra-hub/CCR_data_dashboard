import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# App title and logo
# -----------------------------
st.image("CCRLogo.png", width=200)
st.title("CCR GmbH : RF Plasma Source Comparison Dashboard")

# -----------------------------
# Read the Excel file
# -----------------------------
data = pd.read_excel("plasma_sources.xlsx")
data.columns = data.columns.str.strip().str.lower()  # clean column names

# Ensure the following columns exist: source_type, design, version, source_id, pressure, ion_current_density, ion_energy, rf_power, primary_steps, secondary_steps
required_cols = ["source_type", "design", "version", "source_id",
                 "pressure", "ion_current_density", "ion_energy",
                 "rf_power", "primary_steps", "secondary_steps"]

missing_cols = [c for c in required_cols if c not in data.columns]
if missing_cols:
    st.error(f"Missing columns in Excel: {missing_cols}")
    st.stop()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

selected_types = st.sidebar.multiselect(
    "Select Plasma Source Type",
    options=data["source_type"].unique(),
    default=[]
)

selected_designs = st.sidebar.multiselect(
    "Select Design",
    options=data[data["source_type"].isin(selected_types)]["design"].unique() if selected_types else [],
    default=[]
)

selected_versions = st.sidebar.multiselect(
    "Select Version",
    options=data[
        (data["source_type"].isin(selected_types)) &
        (data["design"].isin(selected_designs))
    ]["version"].unique() if selected_types and selected_designs else [],
    default=[]
)

selected_sources = st.sidebar.multiselect(
    "Select Source ID(s)",
    options=data[
        (data["source_type"].isin(selected_types)) &
        (data["design"].isin(selected_designs)) &
        (data["version"].isin(selected_versions))
    ]["source_id"].unique() if selected_types and selected_designs and selected_versions else [],
    default=[]
)

# -----------------------------
# Filter the dataset based on selections
# -----------------------------
if selected_types or selected_designs or selected_versions or selected_sources:
    filtered_data = data[
        (data["source_type"].isin(selected_types) if selected_types else True) &
        (data["design"].isin(selected_designs) if selected_designs else True) &
        (data["version"].isin(selected_versions) if selected_versions else True) &
        (data["source_id"].isin(selected_sources) if selected_sources else True)
    ]

    st.subheader("Filtered Dataset")
    st.dataframe(filtered_data)

    # -----------------------------
    # Plot selection
    # -----------------------------
    st.sidebar.header("Select Plots")
    plot_options = st.sidebar.multiselect(
        "Choose plots",
        options=[
            "ICD vs Pressure",
            "IE vs Pressure",
            "ICD vs RF Power",
            "IE vs RF Power"
        ],
        default=[]
    )

    # -----------------------------
    # Dynamic plots
    # -----------------------------
    if "ICD vs Pressure" in plot_options:
        st.subheader("ICD vs Pressure")
        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_current_density",
            color="source_id",
            hover_data=["rf_power", "primary_steps", "secondary_steps"]
        )
        fig.update_xaxes(title="Pressure (mbar)", type="log", range=[-5, -2])  # wide range E-05 to E-02
        fig.update_yaxes(title="Ion Current Density", range=[0, filtered_data["ion_current_density"].max() * 1.1])
        st.plotly_chart(fig)

    if "IE vs Pressure" in plot_options:
        st.subheader("Ion Energy vs Pressure")
        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_energy",
            color="source_id",
            hover_data=["rf_power", "primary_steps", "secondary_steps"]
        )
        fig.update_xaxes(title="Pressure (mbar)", type="log", range=[-5, -2])
        fig.update_yaxes(title="Ion Energy", range=[0, filtered_data["ion_energy"].max() * 1.1])
        st.plotly_chart(fig)

    if "ICD vs RF Power" in plot_options:
        st.subheader("ICD vs RF Power")
        fig = px.scatter(
            filtered_data,
            x="rf_power",
            y="ion_current_density",
            color="source_id",
            hover_data=["pressure", "primary_steps", "secondary_steps"]
        )
        fig.update_xaxes(title="RF Power (W)")
        fig.update_yaxes(title="Ion Current Density", range=[0, filtered_data["ion_current_density"].max() * 1.1])
        st.plotly_chart(fig)

    if "IE vs RF Power" in plot_options:
        st.subheader("Ion Energy vs RF Power")
        fig = px.scatter(
            filtered_data,
            x="rf_power",
            y="ion_energy",
            color="source_id",
            hover_data=["pressure", "primary_steps", "secondary_steps"]
        )
        fig.update_xaxes(title="RF Power (W)")
        fig.update_yaxes(title="Ion Energy", range=[0, filtered_data["ion_energy"].max() * 1.1])
        st.plotly_chart(fig)

else:
    st.info("Please select filters from the sidebar to display data.")
