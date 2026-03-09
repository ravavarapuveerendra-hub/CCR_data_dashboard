import streamlit as st
import pandas as pd
import plotly.express as px

st.image("CCRLogo.png", width=200)
st.title("CCR GmbH : RF Plasma Source Comparison Dashboard")

# -----------------------------
# Read the Excel file
uploaded_file = st.file_uploader(
    "Upload plasma source master data file (Excel)",
    type=["xlsx", "csv"]
)

if uploaded_file:
    if uploaded_file.name.endswith(".xlsx"):
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)

    # Clean column names
    data.columns = data.columns.str.strip().str.lower()

    # Map columns to expected names
    col_map = {
        "pressure (mbar)": "pressure",
        "pressure": "pressure",
        "ion current density": "ion_current_density",
        "ion current density (ma/cm2)": "ion_current_density",
        "ion energy": "ion_energy",
        "ion energy (ev)": "ion_energy",
        "rf power (w)": "rf_power",
        "rf power": "rf_power",
        "primary steps": "primary_steps",
        "secondary steps": "secondary_steps",
        "source id": "source_id",
        "version": "version",
        "design": "design",
        "plasma source type": "source_type"
    }
    data = data.rename(columns={k: v for k, v in col_map.items() if k in data.columns})

    # Check required columns
    required_cols = ['source_type', 'design', 'version', 'source_id',
                     'pressure', 'ion_current_density', 'ion_energy', 'rf_power',
                     'primary_steps', 'secondary_steps']

    missing = [c for c in required_cols if c not in data.columns]
    if missing:
        st.error(f"Missing columns in Excel: {missing}")
        st.stop()

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

    # Filter data
    filtered_data = data[
        (data["source_type"].isin(source_type_selected)) &
        (data["design"].isin(design_selected)) &
        (data["version"].isin(version_selected)) &
        (data["source_id"].isin(source_id_selected))
    ] if source_id_selected else pd.DataFrame()

    st.subheader("Filtered Dataset")
    st.dataframe(filtered_data)

    # -----------------------------
    # Plot selection
    st.sidebar.header("Select Plots")
    plot_options = st.sidebar.multiselect(
        "Choose plots",
        options=[
            "ICD vs Pressure",
            "IE vs Pressure",
            "ICD vs RF Power",
            "IE vs RF Power"
        ]
    )

    # -----------------------------
    # Dynamic plots
    if not filtered_data.empty:
        if "ICD vs Pressure" in plot_options:
            st.subheader("ICD vs Pressure")
            fig = px.scatter(
                filtered_data,
                x="pressure",
                y="ion_current_density",
                color="source_id",
                hover_data=["rf_power", "primary_steps", "secondary_steps"]
            )
            fig.update_xaxes(title="Pressure (mbar)", type='log', range=[-5, -2])
            fig.update_yaxes(title="Ion Current Density (mA/cm²)", tickformat=",.0f", range=[0, filtered_data["ion_current_density"].max()*1.1])
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
            fig.update_xaxes(title="Pressure (mbar)", type='log', range=[-5, -2])
            fig.update_yaxes(title="Ion Energy (eV)", tickformat=",.0f", range=[0, filtered_data["ion_energy"].max()*1.1])
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
            fig.update_yaxes(title="Ion Current Density (mA/cm²)", tickformat=",.0f", range=[0, filtered_data["ion_current_density"].max()*1.1])
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
            fig.update_yaxes(title="Ion Energy (eV)", tickformat=",.0f", range=[0, filtered_data["ion_energy"].max()*1.1])
            st.plotly_chart(fig)

    else:
        st.info("Select filters to see comparison plots.")

else:
    st.info("Upload a master Excel file to get started.")
