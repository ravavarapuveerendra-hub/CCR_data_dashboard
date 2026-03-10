import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# App title & logo
# -----------------------------
st.image("CCRLogo.png", width=200)
st.title("RF Plasma Sources Data Dashboard")

# -----------------------------
# Upload multiple source files
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload plasma source data files (Excel/CSV, one per source)",
    type=["xlsx", "csv"],
    accept_multiple_files=True
)

# Initialize dataframe
data = pd.DataFrame()

if uploaded_files:
    all_data = []
    for f in uploaded_files:
        # Read Excel or CSV
        if f.name.endswith(".xlsx"):
            df = pd.read_excel(f)
        else:
            df = pd.read_csv(f)

        # Ensure column names are lowercase and stripped
        df.columns = df.columns.str.strip().str.lower()

        # Standardize column names
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

        # Add source ID from filename
        df["source_id"] = f.name.split(".")[0]

        all_data.append(df)

    # Concatenate all uploaded sources
    data = pd.concat(all_data, ignore_index=True)

# -----------------------------
# Sidebar filters
# -----------------------------
if not data.empty:
    st.sidebar.header("Filters")

    source_ids = st.sidebar.multiselect(
        "Select Source ID",
        options=data["source_id"].unique()
    )

    filtered_data = data[data["source_id"].isin(source_ids)] if source_ids else pd.DataFrame()

    # -----------------------------
    # Plot selection
    # -----------------------------
    plot_options = st.sidebar.multiselect(
        "Choose plots",
        options=[
            "ICD vs Pressure",
            "IE vs Pressure",
            "Primary vs Secondary Matching"
        ]
    )

    # -----------------------------
    # Show filtered dataset
    # -----------------------------
    st.subheader("Filtered Dataset")
    st.dataframe(filtered_data)

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
            st.subheader("Primary vs Secondary Matching")
            fig = px.scatter(
                filtered_data,
                x="primary_steps",
                y="secondary_steps",
                color="source_id",
                hover_data=["pressure", "rf_power"]
            )
            fig.update_xaxes(title="Primary Steps", range=[0,2160])
            fig.update_yaxes(title="Secondary Steps", range=[0,2160])
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Upload one or more Excel/CSV files to get started.")
