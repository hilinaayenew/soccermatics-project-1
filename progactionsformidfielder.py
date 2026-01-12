import streamlit as st 
import pandas as pd
from scipy.stats import percentileofscore
import plotly.express as px

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(
    page_title="Euro 2024 Midfielders Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------
# Load data
# -----------------------
mid_prog_df = pd.read_csv("euro24_midfielders_full.csv")
mid_prog_df.columns = mid_prog_df.columns.str.strip()

# -----------------------
# Header
# -----------------------
st.title("Euro 2024 Midfielders: Ball Progression Dashboard")
st.markdown(
    """
    This dashboard shows how midfielders help move the ball forward during Euro 2024.  
    Metrics are shown **per 90 minutes** to allow fair comparison between players.  
    Only players with **200+ minutes played** are included.
    """
)

# -----------------------
# Player selector
# -----------------------
players = mid_prog_df["player"].tolist()
selected_player = st.selectbox("Choose a midfielder", players)
player_data = mid_prog_df[mid_prog_df["player"] == selected_player]

# -----------------------
# Hover text (user-friendly)
# -----------------------
mid_prog_df["hover_text"] = (
    "Player: " + mid_prog_df["player"] +
    "<br>Total matches played: " + mid_prog_df["total_games"].astype(str) +
    "<br>Matches played as midfielder: " + mid_prog_df["mid_games"].astype(str) +
    "<br>Progressive passes per 90: " + mid_prog_df["prog_passes_90"].round(2).astype(str) +
    "<br>Progressive carries per 90: " + mid_prog_df["prog_carries_90"].round(2).astype(str) +
    "<br>Final third entries per 90: " + mid_prog_df["prog_passes_final_third_90"].round(2).astype(str)
)

# -----------------------
# Color categories
# -----------------------
def assign_color(player):
    if player == "Christian Dannemann Eriksen":
        return "Christian Eriksen"
    elif player == selected_player:
        return "Selected player"
    else:
        return "Other midfielders"

mid_prog_df["color_label"] = mid_prog_df["player"].apply(assign_color)

COLOR_MAP = {
    "Christian Eriksen": "#0C6DBC",
    "Selected player": "#981717",
    "Other midfielders": "#ADD8E6"
}

# -----------------------
# Scatter plot 1
# -----------------------
st.subheader("Progressive Passing vs Progressive Carrying")

fig = px.scatter(
    mid_prog_df,
    x="prog_passes_90",
    y="prog_carries_90",
    color="color_label",
    color_discrete_map=COLOR_MAP,
    hover_name="player",
    hover_data={
        "prog_passes_90": True,
        "prog_carries_90": True,
        "prog_passes_final_third_90": True,
        "total_games": True,
        "mid_games": True,
        "color_label": False
    },
    labels={
        "prog_passes_90": "Progressive passes per 90 minutes",
        "prog_carries_90": "Progressive carries per 90 minutes"
    },
    title="How midfielders progress the ball through passing and carrying"
)

fig.update_traces(marker=dict(size=9))
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Scatter plot 2
# -----------------------
st.subheader("Progressive Passing vs Final Third Entries")

fig2 = px.scatter(
    mid_prog_df,
    x="prog_passes_90",
    y="prog_passes_final_third_90",
    color="color_label",
    color_discrete_map=COLOR_MAP,
    hover_name="player",
    labels={
        "prog_passes_90": "Progressive passes per 90 minutes",
        "prog_passes_final_third_90": "Final third entries per 90 minutes"
    },
    title="Relationship between progressive passing and attacking involvement"
)

fig2.update_traces(marker=dict(size=9))
st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# Percentile ranks
# -----------------------
st.subheader(f"How {selected_player} compares to other midfielders")

pp90 = float(player_data["prog_passes_90"].iloc[0])
pc90 = float(player_data["prog_carries_90"].iloc[0])
fte90 = float(player_data["prog_passes_final_third_90"].iloc[0])

st.write(
    f"**Progressive passes per 90 minutes:** "
    f"better than {percentileofscore(mid_prog_df['prog_passes_90'], pp90):.1f}% of midfielders"
)

st.write(
    f"**Progressive carries per 90 minutes:** "
    f"better than {percentileofscore(mid_prog_df['prog_carries_90'], pc90):.1f}% of midfielders"
)

st.write(
    f"**Final third entries per 90 minutes:** "
    f"better than {percentileofscore(mid_prog_df['prog_passes_final_third_90'], fte90):.1f}% of midfielders"
)

# -----------------------
# Ranking table
# -----------------------
st.subheader("Midfielders ranking table")

metric_labels = {
    "prog_passes_90": "Progressive passes per 90 minutes",
    "prog_carries_90": "Progressive carries per 90 minutes",
    "prog_passes_final_third_90": "Final third entries per 90 minutes",
    "prog_passes": "Total progressive passes",
    "prog_carries": "Total progressive carries",
    "prog_passes_final_third": "Total final third entries",
    "total_games": "Total matches played",
    "mid_games": "Matches played as midfielder"
}

selected_metric_label = st.selectbox(
    "Rank midfielders by:",
    list(metric_labels.values())
)

selected_metric = [k for k, v in metric_labels.items() if v == selected_metric_label][0]

rank_table = mid_prog_df.sort_values(selected_metric, ascending=False).reset_index(drop=True)
rank_table["Rank"] = rank_table.index + 1

rank_table = rank_table[
    [
        "Rank",
        "player",
        "total_games",
        "mid_games",
        "prog_passes",
        "prog_carries",
        "prog_passes_final_third",
        "prog_passes_90",
        "prog_carries_90",
        "prog_passes_final_third_90"
    ]
]

rank_table.columns = [
    "Rank",
    "Player",
    "Total matches",
    "Matches as midfielder",
    "Total progressive passes",
    "Total progressive carries",
    "Total final third entries",
    "Progressive passes per 90",
    "Progressive carries per 90",
    "Final third entries per 90"
]

def highlight_players(row):
    if row["Player"] == selected_player:
        return ["background-color: lightcoral"] * len(row)
    elif row["Player"] == "Christian Dannemann Eriksen":
        return ["background-color: lightblue"] * len(row)
    else:
        return [""] * len(row)

st.dataframe(rank_table.style.apply(highlight_players, axis=1))
