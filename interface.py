import streamlit as st
import pandas as pd
import plotly.express as px
import os
from glob import glob

st.set_page_config(layout="wide")
st.image("CCRLogo.png", width=200)
st.title("RF Plasma Sources Data Dashboard")

# -----------------------------
# Load all Excel/CSV files from data folder
# -----------------------------
data_folder = "data"  # folder containing your source files
all_files = glob(os.path.join(data_folder, "*.xlsx")) + glob(os.path.join(data_folder, "*.csv"))

if not all_files:
    st.warning("No data files found in the 'data' folder. Please add Excel/CSV files for sources.")
    st.stop()

all_data = []
for file_path in all_files:
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        # Ensure column names are strings and lowercase
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Standardize column names
        col_map = {
            "pressure": "pressure",
            "rf power": "rf_power",
            "coil current": "coil_current",
            "primary": "primary_steps",
            "secondary": "secondary_steps",
            "icd": "ion_current_density",
            "ie": "ion_energy"
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        # Extract metadata from filename
        fname = os.path.splitext(os.path.basename(file_path))[0]  # e.g., "COPRA_DN_160_01"
        parts = fname.split("_")
        df["source_type"] = parts[0] + " " + parts[1] if len(parts) > 1 else parts[0]
        df["design"] = parts[1] if len(parts) > 1 else ""
        df["version"] = parts[2] if len(parts) > 2 else ""
        df["source_id"] = fname

        all_data.append(df)
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")

# Combine all data
data = pd.concat(all_data, ignore_index=True)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

# Source Type filter
source_type_selected = st.sidebar.multiselect(
    "Select Plasma Source Type",
    options=data["source_type"].dropna().unique(),
    key="source_type"
)

# Design filter
design_options = data[data["source_type"].isin(source_type_selected)]["design"].dropna().unique() if source_type_selected else []
design_selected = st.sidebar.multiselect(
    "Select Design",
    options=design_options,
    key="design"
)

# Version filter
version_options = data[
    (data["source_type"].isin(source_type_selected)) &
    (data["design"].isin(design_selected))
]["version"].dropna().unique() if design_selected else []
version_selected = st.sidebar.multiselect(
    "Select Version",
    options=version_options,
    key="version"
)

# Source ID filter
source_id_options = data[
    (data["source_type"].isin(source_type_selected)) &
    (data["design"].isin(design_selected)) &
    (data["version"].isin(version_selected))
]["source_id"].dropna().unique() if version_selected else []
source_id_selected = st.sidebar.multiselect(
    "Select Source ID",
    options=source_id_options,
    key="source_id"
)

# -----------------------------
# Filter data based on selections
# -----------------------------
filtered_data = data[
    (data["source_type"].isin(source_type_selected)) &
    (data["design"].isin(design_selected)) &
    (data["version"].isin(version_selected)) &
    (data["source_id"].isin(source_id_selected))
] if source_id_selected else pd.DataFrame()

# -----------------------------
# Show key source info (coil current, RF power)
# -----------------------------
if not filtered_data.empty:
    st.subheader("Selected Sources Info")
    info_cols = ["source_id", "coil_current", "rf_power"]
    st.table(filtered_data[info_cols].drop_duplicates().reset_index(drop=True))

# -----------------------------
# Plot selection
# -----------------------------
st.sidebar.header("Select Plots")
plot_options = st.sidebar.multiselect(
    "Choose plots",
    options=[
        "ICD vs Pressure",
        "IE vs Pressure",
        "Primary vs Secondary Matching"
    ],
    key="plots"
)

# -----------------------------
# Plotting
# -----------------------------
if not filtered_data.empty:

    if "ICD vs Pressure" in plot_options:
        st.subheader("Ion Current Density vs Pressure")
        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_current_density",
            color="source_id",
            hover_data=["rf_power", "coil_current", "primary_steps", "secondary_steps"]
        )
        # Autoscale x-axis based on filtered data
        pressure_min = filtered_data["pressure"].min()
        pressure_max = filtered_data["pressure"].max()
        fig.update_xaxes(
            title="Pressure (mbar)",
            type="log",
            tickformat=".2e",
            range=[pd.np.log10(pressure_min), pd.np.log10(pressure_max)]
        )
        fig.update_yaxes(
            title="Ion Current Density (mA/cm²)",
            range=[0, filtered_data["ion_current_density"].max() * 1.1]
        )
        st.plotly_chart(fig, use_container_width=True)

    if "IE vs Pressure" in plot_options:
        st.subheader("Ion Energy vs Pressure")
        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_energy",
            color="source_id",
            hover_data=["rf_power", "coil_current", "primary_steps", "secondary_steps"]
        )
        # Autoscale x-axis
        pressure_min = filtered_data["pressure"].min()
        pressure_max = filtered_data["pressure"].max()
        fig.update_xaxes(
            title="Pressure (mbar)",
            type="log",
            tickformat=".2e",
            range=[pd.np.log10(pressure_min), pd.np.log10(pressure_max)]
        )
        fig.update_yaxes(
            title="Ion Energy (eV)",
            range=[0, filtered_data["ion_energy"].max() * 1.1]
        )
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
        fig.update_xaxes(title="Primary Matching Steps", range=[0, 2160])
        fig.update_yaxes(title="Secondary Matching Steps", range=[0, 2160])
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Select filters and plots to see comparison charts.")
