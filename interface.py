import streamlit as st
import pandas as pd
import plotly.express as px

st.image("CCRLogo.png", width=200)
st.title("RF Plasma Sources Data Dashboard")

# -----------------------------
# Load Excel file automatically
data = pd.read_excel("plasma_sources.xlsx")

# Clean column names
data.columns = data.columns.str.strip().str.lower()

# Standardize expected column names
col_map = {
    "plasma source type": "source_type",
    "design": "design",
    "version": "version",
    "source id": "source_id",
    "pressure (mbar)": "pressure",
    "pressure": "pressure",
    "ion current density": "ion_current_density",
    "ion current density (ma/cm2)": "ion_current_density",
    "ion energy": "ion_energy",
    "ion energy (ev)": "ion_energy",
    "rf power (w)": "rf_power",
    "rf power": "rf_power",
    "primary steps": "primary_steps",
    "secondary steps": "secondary_steps"
}
data = data.rename(columns={k: v for k, v in col_map.items() if k in data.columns})

# -----------------------------
# Sidebar filters
st.sidebar.header("Filters")

source_type_selected = st.sidebar.multiselect(
    "Select Plasma Source Type",
    options=data["source_type"].unique()
)

design_selected = st.sidebar.multiselect(
    "Select Design",
    options=data[data["source_type"].isin(source_type_selected)]["design"].unique()
    if source_type_selected else []
)

version_selected = st.sidebar.multiselect(
    "Select Version",
    options=data[(data["source_type"].isin(source_type_selected)) &
                 (data["design"].isin(design_selected))]["version"].unique()
    if source_type_selected and design_selected else []
)

source_id_selected = st.sidebar.multiselect(
    "Select Source ID",
    options=data[(data["source_type"].isin(source_type_selected)) &
                 (data["design"].isin(design_selected)) &
                 (data["version"].isin(version_selected))]["source_id"].unique()
    if source_type_selected and design_selected and version_selected else []
)

# -----------------------------
# Comparison level
st.sidebar.header("Comparison Settings")

compare_by = st.sidebar.selectbox(
    "Compare By",
    ["source_id", "design", "version", "source_type"]
)

# -----------------------------
# Filter data
filtered_data = data[
    (data["source_type"].isin(source_type_selected)) &
    (data["design"].isin(design_selected)) &
    (data["version"].isin(version_selected)) &
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
    ]
)

# -----------------------------
# Plotting
if not filtered_data.empty:

    # ICD vs Pressure
    if "ICD vs Pressure" in plot_options:

        st.subheader("Ion Current Density vs Pressure")

        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_current_density",
            color=compare_by,
            hover_data=["source_id","rf_power","primary_steps","secondary_steps"]
        )

        fig.update_xaxes(
            title="Pressure (mbar)",
            type="log",
            range=[-5, -2]
        )

        fig.update_yaxes(
            title="Ion Current Density (mA/cm²)",
            range=[0, filtered_data["ion_current_density"].max()*1.1]
        )

        st.plotly_chart(fig, use_container_width=True)

    # IE vs Pressure
    if "IE vs Pressure" in plot_options:

        st.subheader("Ion Energy vs Pressure")

        fig = px.scatter(
            filtered_data,
            x="pressure",
            y="ion_energy",
            color=compare_by,
            hover_data=["source_id","rf_power","primary_steps","secondary_steps"]
        )

        fig.update_xaxes(
            title="Pressure (mbar)",
            type="log",
            range=[-5, -2]
        )

        fig.update_yaxes(
            title="Ion Energy (eV)",
            range=[0, filtered_data["ion_energy"].max()*1.1]
        )

        st.plotly_chart(fig, use_container_width=True)

    # Matching Map
    if "Primary vs Secondary Matching" in plot_options:

        st.subheader("Matching Map (Primary vs Secondary)")

        fig = px.scatter(
            filtered_data,
            x="primary_steps",
            y="secondary_steps",
            color=compare_by,
            hover_data=["pressure","rf_power","source_id"]
        )

        fig.update_xaxes(
            title="Primary Matching Steps",
            range=[0,2160]
        )

        fig.update_yaxes(
            title="Secondary Matching Steps",
            range=[0,2160]
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Select filters to see comparison plots.")
