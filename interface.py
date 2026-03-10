import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.image("CCRLogo.png", width=200)
st.title("RF Plasma Sources Data Dashboard")

# -----------------------------
# Load all Excel files from 'data/' folder
data_folder = "data"
all_files = [f for f in os.listdir(data_folder) if f.endswith((".xlsx", ".csv"))]

all_data = []

for f in all_files:
    file_path = os.path.join(data_folder, f)
    if f.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    col_map = {
        "gas": "gas",
        "coil current": "coil_current",
        "pressure": "pressure",
        "rf power": "rf_power",
        "primary": "primary_steps",
        "secondary": "secondary_steps",
        "icd": "ion_current_density",
        "ie": "ion_energy"
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Forward-fill missing Gas and Coil Current values
    if "gas" in df.columns:
        df["gas"].ffill(inplace=True)
    if "coil_current" in df.columns:
        df["coil_current"].ffill(inplace=True)

    # Convert numeric columns
    numeric_cols = ["pressure", "rf_power", "primary_steps", "secondary_steps", "ion_current_density", "ion_energy"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

    # Set source ID from filename
    df["source_id"] = f.split(".")[0]

    all_data.append(df)

# Concatenate all data
if all_data:
    data = pd.concat(all_data, ignore_index=True)
else:
    st.warning("No data files found in the 'data/' folder.")
    st.stop()

# -----------------------------
# Sidebar filters
st.sidebar.header("Filters")

source_type_options = data["gas"].unique() if "gas" in data.columns else []
source_type_selected = st.sidebar.multiselect(
    "Select Plasma Source Type",
    options=source_type_options,
    key="source_type"
)

design_options = data[data["gas"].isin(source_type_selected)]["coil_current"].unique() if source_type_selected else []
design_selected = st.sidebar.multiselect(
    "Select Design (Coil Current)",
    options=design_options,
    key="design"
)

version_options = data[
    (data["gas"].isin(source_type_selected)) &
    (data["coil_current"].isin(design_selected))
]["rf_power"].unique() if design_selected else []
version_selected = st.sidebar.multiselect(
    "Select Version (RF Power)",
    options=version_options,
    key="version"
)

source_id_options = data[
    (data["gas"].isin(source_type_selected)) &
    (data["coil_current"].isin(design_selected)) &
    (data["rf_power"].isin(version_selected))
]["source_id"].unique() if version_selected else []
source_id_selected = st.sidebar.multiselect(
    "Select Source ID",
    options=source_id_options,
    key="source_id"
)

# -----------------------------
# Filter data
filtered_data = data[
    (data["gas"].isin(source_type_selected)) &
    (data["coil_current"].isin(design_selected)) &
    (data["rf_power"].isin(version_selected)) &
    (data["source_id"].isin(source_id_selected))
] if source_id_selected else pd.DataFrame()

# -----------------------------
# Show dataset
st.subheader("Filtered Dataset")
st.dataframe(filtered_data)

# -----------------------------
# Plot selection
st.sidebar.header("Select Plots")
plot_options = st.sidebar.multiselect(
    "Choose plots",
    [
        "ICD vs Pressure",
        "IE vs Pressure",
        "Primary vs Secondary Matching"
    ],
    key="plots"
)

# -----------------------------
# Plotting
if not filtered_data.empty:

    if "ICD vs Pressure" in plot_options:
        st.subheader("Ion Current Density vs Pressure")
        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_current_density",
            color="source_id",
            hover_data=["rf_power", "primary_steps", "secondary_steps"]
        )
        fig.update_xaxes(title="Pressure (mbar)", type="log", range=[-5, -2])
        fig.update_yaxes(title="Ion Current Density (mA/cm²)", range=[0, filtered_data["ion_current_density"].max()*1.1])
        st.plotly_chart(fig, use_container_width=True)

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
        fig.update_yaxes(title="Ion Energy (eV)", range=[0, filtered_data["ion_energy"].max()*1.1])
        st.plotly_chart(fig, use_container_width=True)

    if "Primary vs Secondary Matching" in plot_options:
        st.subheader("Matching Map (Primary vs Secondary)")
        fig = px.scatter(
            filtered_data,
            x="primary_steps",
            y="secondary_steps",
            color="source_id",
            hover_data=["pressure", "rf_power"]
        )
        fig.update_xaxes(title="Primary Matching Steps", range=[0,2160])
        fig.update_yaxes(title="Secondary Matching Steps", range=[0,2160])
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Select filters to see comparison plots.")
