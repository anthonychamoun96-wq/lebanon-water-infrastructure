import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Lebanon Water Infrastructure Explorer",
    page_icon="🇱🇧",
    layout="wide"
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_csv(
        "MSBA325 Streamlit Assignment.csv",
        encoding="utf-8"
    )

    # Convert binary and numeric columns to numbers
    numeric_columns = [
        "State of the water network - good",
        "State of the water network - acceptable",
        "State of the water network - bad",
        "Potable water source - water point",
        "Potable water source - gallons purchase",
        "Potable water source - artesian well",
        "Potable water source - public network",
        "Potable water source - other",
        "Total number of permanent water springs",
        "Total number of seasonal water springs",
        "latitude",
        "longitude"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column]
        )

    # -----------------------------------------------------
    # CREATE NETWORK STATUS
    # -----------------------------------------------------

    data["Network Status"] = "Unknown"

    data.loc[
        data["State of the water network - good"] == 1,
        "Network Status"
    ] = "Good"

    data.loc[
        data["State of the water network - acceptable"] == 1,
        "Network Status"
    ] = "Acceptable"

    data.loc[
        data["State of the water network - bad"] == 1,
        "Network Status"
    ] = "Bad"

    # -----------------------------------------------------
    # CREATE TOTAL SPRINGS
    # -----------------------------------------------------

    data["Total Water Springs"] = (
        data["Total number of permanent water springs"]
        +
        data["Total number of seasonal water springs"]
    )

    # -----------------------------------------------------
    # CREATE NUMBER OF POTABLE WATER SOURCES
    # -----------------------------------------------------

    source_columns = [
        "Potable water source - water point",
        "Potable water source - gallons purchase",
        "Potable water source - artesian well",
        "Potable water source - public network",
        "Potable water source - other"
    ]

    data["Number of Potable Sources"] = (
        data[source_columns]
        .sum(axis=1)
    )

    return data


data = load_data()


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("🇱🇧 Lebanon Water Infrastructure Explorer")

st.markdown(
    """
    Explore the condition of the water network, potable water
    sources, and water springs across Lebanese towns.
    """
)

st.caption(
    """Note: The original dataset contained 1,137 towns. For this analysis,
    596 towns were selected after data-quality checks, as the remaining
    observations contained data inconsistencies that could affect the
    accuracy and comparability of the visualizations."""
)


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("🔎 Explore the Data")


# Governorate filter
governorates = sorted(
    data["Governorate"].unique()
)

selected_governorates = st.sidebar.multiselect(
    "Governorate",
    governorates,
    default=governorates
)


# Filter temporarily by governorate
filtered_for_district = data[
    data["Governorate"].isin(selected_governorates)
]


# District filter
districts = sorted(
    filtered_for_district["District"]
    .unique()
)

selected_districts = st.sidebar.multiselect(
    "District",
    districts,
    default=districts
)

with st.sidebar.expander("ℹ️ Interaction Design"):

    st.write(
        """
        **Governorate filter:** This feature helps the user answer the question,
        "How does water infrastructure vary across different governorates?"
        A multiselect was chosen instead of a dropdown because users may want
        to compare several governorates at the same time. This supports
        comparison while reducing clutter by allowing the user to focus only
        on the geographic areas of interest.
        """
    )

    st.write(
        """
        **District filter:** This feature helps the user answer the more
        specific question, "Which districts within the selected governorates
        show these water infrastructure patterns?" A multiselect was chosen
        instead of a separate independent filter because it allows users to
        compare multiple districts while supporting geographic drill-down.
        The district options are dynamically linked to the selected
        governorates, which helps provide context and reduces irrelevant
        choices.
        """
    )


# Network status filter
network_statuses = [
    "Good",
    "Acceptable",
    "Bad"
]

selected_statuses = st.sidebar.multiselect(
    "Network Status",
    network_statuses,
    default=network_statuses
)


# ---------------------------------------------------------
# POTABLE WATER SOURCE FILTER
# ---------------------------------------------------------

source_options = {
    "Water Point": "Potable water source - water point",
    "Gallons Purchase": "Potable water source - gallons purchase",
    "Artesian Well": "Potable water source - artesian well",
    "Public Network": "Potable water source - public network",
    "Other": "Potable water source - other"
}

selected_sources = st.sidebar.multiselect(
    "Potable Water Source",
    list(source_options.keys())
)


# ---------------------------------------------------------
# TOWN SEARCH
# ---------------------------------------------------------

town_search = st.sidebar.text_input(
    "Search for a town",
    placeholder="Type a town name..."
)


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered_data = data[
    data["Governorate"].isin(selected_governorates)
    &
    data["District"].isin(selected_districts)
    &
    data["Network Status"].isin(selected_statuses)
].copy()


# Apply potable source filter
if selected_sources:

    for source_name in selected_sources:

        source_column = source_options[source_name]

        filtered_data = filtered_data[
            filtered_data[source_column] == 1
        ]


# Apply town search
if town_search:

    filtered_data = filtered_data[
        filtered_data["Town"]
        .astype(str)
        .str.contains(
            town_search,
            case=False,
            na=False
        )
    ]



# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Towns Shown",
        len(filtered_data)
    )


with col2:
    bad_count = (
        filtered_data["Network Status"] == "Bad"
    ).sum()

    st.metric(
        "Towns with Bad Networks",
        bad_count
    )


with col3:
    springs = int(
        filtered_data["Total Water Springs"].sum()
    )

    st.metric(
        "Total Water Springs",
        springs
    )


with col4:
    sources = round(
        filtered_data["Number of Potable Sources"].mean(),
        1
    ) if len(filtered_data) > 0 else 0

    st.metric(
        "Avg. Potable Sources / Town",
        sources
    )


st.divider()


# ---------------------------------------------------------
# KEY INSIGHTS
# ---------------------------------------------------------

st.subheader("💡 Key Insights")

st.info(
    """
    **Insight 1 — Public network availability is almost universal, but
    network condition is not.** Across the 596 towns, 592 towns (99.3%)
    report a public network as a potable water source. However, only 119
    towns (20.0%) have a good network, while 340 (57.0%) have an acceptable
    network and 137 (23.0%) have a bad network. This shows that the presence
    of a public network and the condition of that network are distinct
    dimensions of the water infrastructure.
    """
)

st.info(
    """
    **Insight 2 — Network condition varies across governorates.** The
    percentage of towns classified as having a bad network ranges from 17.8%
    in the North to 30.8% in El Nabatieh. The percentage classified as having
    a good network also varies substantially, ranging from 6.2% in
    Baalbek-El Hermel to 27.5% in the Bekaa. This geographic variation
    highlights why examining water infrastructure at the governorate and
    district levels is useful.
    """
)


# ---------------------------------------------------------
# MAP DISPLAY OPTIONS
# ---------------------------------------------------------

st.subheader("🗺️ Interactive Water Infrastructure Map")

map_display = st.radio(
    "Choose what you want to explore:",
    [
        "Network Condition",
        "Water Springs",
        "Potable Water Sources"
    ],
    horizontal=True
)


# ---------------------------------------------------------
# NETWORK CONDITION MAP
# ---------------------------------------------------------

if map_display == "Network Condition":

    fig = px.scatter_map(
        filtered_data,
        lat="latitude",
        lon="longitude",
        color="Network Status",
        hover_name="Town",
        hover_data={
            "District": True,
            "Governorate": True,
            "Network Status": True,
            "Number of Potable Sources": True,
            "Total number of permanent water springs": True,
            "Total number of seasonal water springs": True,
            "Total Water Springs": False,
            "latitude": False,
            "longitude": False
        },
        color_discrete_map={
            "Good": "green",
            "Acceptable": "orange",
            "Bad": "red"
        },
        zoom=7,
        center={
            "lat": 33.85,
            "lon": 35.85
        },
        map_style="open-street-map",
        height=650
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),
        legend_title_text="Network Condition"
    )


# ---------------------------------------------------------
# WATER SPRINGS MAP
# ---------------------------------------------------------

elif map_display == "Water Springs":

    filtered_data["Spring Size"] = np.sqrt(filtered_data["Total Water Springs"])

    fig = px.scatter_map(
        filtered_data,
        lat="latitude",
        lon="longitude",
        color="Total Water Springs",
        size="Spring Size",
        hover_name="Town",
        hover_data={
            "District": True,
            "Governorate": True,
            "Network Status": True,
            "Total number of permanent water springs": True,
            "Total number of seasonal water springs": True,
            "Number of Potable Sources": True,
            "Total Water Springs": False,
            "latitude": False,
            "longitude": False,
            "Spring Size": False
        },
        color_continuous_scale="Blues",
        zoom=7,
        center={
            "lat": 33.85,
            "lon": 35.85
        },
        map_style="open-street-map",
        height=650
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),
        coloraxis_colorbar_title="Water Springs"
    )


# ---------------------------------------------------------
# POTABLE SOURCES MAP
# ---------------------------------------------------------

else:

    fig = px.scatter_map(
        filtered_data,
        lat="latitude",
        lon="longitude",
        color="Number of Potable Sources",
        size="Number of Potable Sources",
        size_max=15,
        hover_name="Town",
        hover_data={
            "District": True,
            "Governorate": True,
            "Network Status": True,
            "Number of Potable Sources": True,
            "Total number of permanent water springs": True,
            "Total number of seasonal water springs": True,
            "latitude": False,
            "longitude": False
        },
        color_continuous_scale="Viridis",
        zoom=7,
        center={
            "lat": 33.85,
            "lon": 35.85
        },
        map_style="open-street-map",
        height=650
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),
        coloraxis_colorbar_title="Number of Sources"
    )


# ---------------------------------------------------------
# DISPLAY MAP
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------------------------
# SELECTED TOWN DETAILS
# ---------------------------------------------------------

st.divider()

st.subheader("📍 Town Details")

if len(filtered_data) > 0:

    selected_town = st.selectbox(
        "Select a town to view its water profile:",
        sorted(filtered_data["Town"].unique())
    )

    town_data = filtered_data[
        filtered_data["Town"] == selected_town
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("### Location")

        st.write(
            f"**Town:** {town_data['Town']}"
        )

        st.write(
            f"**District:** {town_data['District']}"
        )

        st.write(
            f"**Governorate:** {town_data['Governorate']}"
        )

    with col2:

        st.write("### Network")

        st.write(
            f"**Condition:** {town_data['Network Status']}"
        )

        st.write(
            f"**Permanent Springs:** "
            f"{int(town_data['Total number of permanent water springs'])}"
        )

        st.write(
            f"**Seasonal Springs:** "
            f"{int(town_data['Total number of seasonal water springs'])}"
        )

    with col3:

        st.write("### Potable Water Sources")

        st.write(
            f"**Number of Sources:** "
            f"{int(town_data['Number of Potable Sources'])}"
        )

        source_labels = [
            (
                "Water Point",
                "Potable water source - water point"
            ),
            (
                "Gallons Purchase",
                "Potable water source - gallons purchase"
            ),
            (
                "Artesian Well",
                "Potable water source - artesian well"
            ),
            (
                "Public Network",
                "Potable water source - public network"
            ),
            (
                "Other",
                "Potable water source - other"
            )
        ]

        for label, column in source_labels:

            if town_data[column] == 1:
                st.write(f"✓ {label}")

else:

    st.warning(
        "No towns match the **selected filters**."
    )


# ---------------------------------------------------------
# EXPLANATION
# ---------------------------------------------------------

with st.expander("ℹ️ About this visualization"):

    st.write(
        """
        Each point represents a Lebanese town with available
        geographic coordinates.

        Network condition is determined from the three binary
        network-condition variables: Good, Acceptable, and Bad.

        Potable water sources are represented by five binary
        variables: water point, gallons purchase, artesian well,
        public network, and other.

        Total water springs combines permanent and seasonal
        water springs.
        """
    )


# =========================================================
# SECOND VISUALIZATION
# POTABLE WATER SOURCE PROFILE
# =========================================================

st.divider()

st.header("💧 Potable Water Source Profile")
st.write(
    "Explore how potable water sources vary across different network conditions."
)

source_columns = {
    "Water Point": "Potable water source - water point",
    "Gallons Purchase": "Potable water source - gallons purchase",
    "Artesian Well": "Potable water source - artesian well",
    "Public Network": "Potable water source - public network",
    "Other": "Potable water source - other"
}

group_by = st.radio(
    "Compare potable water sources by:",
    ["Network Condition", "Governorate"],
    horizontal=True
)

if group_by == "Network Condition":
    group_column = "Network Status"
else:
    group_column = "Governorate"

source_data = filtered_data[
    [group_column] + list(source_columns.values())
].copy()

source_summary = (
    source_data
    .groupby(group_column)[list(source_columns.values())]
    .mean()
    * 100
)

source_summary.rename(
    columns=dict(
        zip(source_columns.values(), source_columns.keys())
    ),
    inplace=True
)

source_summary = source_summary.round(1)

heatmap_data = source_summary.reset_index().melt(
    id_vars=group_column,
    var_name="Potable Water Source",
    value_name="Percentage"
)

fig = px.density_heatmap(
    heatmap_data,
    x="Potable Water Source",
    y=group_column,
    z="Percentage",
    text_auto=".1f",
    labels = {
    "Percentage": "Percentage of Towns",
    group_column: group_by
}
)


if group_by == "Network Condition":
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=["Bad", "Acceptable", "Good"]
    )

else:
    fig.update_yaxes(
        categoryorder="category descending"
    )

    
fig.update_layout(
    title="Potable Water Source Usage",
    xaxis_title="Potable Water Source",
    yaxis_title=group_by,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    """Note: A town can use more than one potable water source, so percentages
    across water sources do not need to add up to 100%."""
)

with st.expander("ℹ️ About this visualization"):
    st.write(
        """
        This heatmap shows the percentage of towns using each potable water
        source across different network conditions or governorates.

        Each cell represents the percentage of towns in that group that use
        the selected water source. Darker cells indicate a higher percentage.

        Use the selector above the chart to switch between comparing network
        conditions and comparing governorates. The sidebar filters also
        update this visualization automatically.
        """
    )