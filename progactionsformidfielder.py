import streamlit as st 
import pandas as pd
from scipy.stats import percentileofscore
import plotly.express as px

# -----------------------
# Load CSV
# -----------------------
mid_prog_df = pd.read_csv("euro24_midfielders_full.csv")
mid_prog_df.columns = mid_prog_df.columns.str.strip()

# -----------------------
# Header
# -----------------------
st.title("Euro 2024 Midfielders: Progressive Actions Dashboard")
st.markdown("Visualization of progressive passes, carries, and final third entries.")
st.markdown("This data applies to players with above 200 total minutes played.")

# -----------------------
# Player selector
# -----------------------
players = mid_prog_df["player"].tolist()
selected_player = st.selectbox("Select a player", players)
player_data = mid_prog_df[mid_prog_df["player"] == selected_player]

# -----------------------
# Hover text for Plotly
# -----------------------
mid_prog_df['hover_text'] = (
    "Player: " + mid_prog_df['player'] +
    "<br>Total games: " + mid_prog_df['total_games'].astype(str) +
    "<br>Mid games: " + mid_prog_df['mid_games'].astype(str) +
    "<br>Prog Passes /90: " + mid_prog_df['prog_passes_90'].round(2).astype(str) +
    "<br>Prog Carries /90: " + mid_prog_df['prog_carries_90'].round(2).astype(str) +
    "<br>Final Third /90: " + mid_prog_df['prog_passes_final_third_90'].round(2).astype(str)
)

# -----------------------
# Assign color categories for plot
# -----------------------
def assign_color(player):
    if player == "Christian Dannemann Eriksen":
        return "Eriksen"
    elif player == selected_player:
        return "Selected Player : {selected_player}"
    else:
        return "Other Midfielders"

mid_prog_df['color_label'] = mid_prog_df['player'].apply(assign_color)

COLOR_MAP = {
   "Eriksen ": "#0C6DBC",
    f"Selected: {selected_player} ": "#981717",
    "Other midfielders ": "#ADD8E6"
}

# -----------------------
# Assign marker sizes
# -----------------------
mid_prog_df['marker_size'] = mid_prog_df['player'].apply(
    lambda x: 18 if x == selected_player else 16 if x == "Christian Dannemann Eriksen" else 12
)

# -----------------------
# Scatter plot 1: Passes vs Carries
# -----------------------
st.subheader("Progressive Passes vs Carries per 90")

fig = px.scatter(
    mid_prog_df,
    x='prog_passes_90',
    y='prog_carries_90',
    color='color_label',
    color_discrete_map=COLOR_MAP,
    hover_name='player',
    hover_data={
        'total_games': True,
        'mid_games': True,
        'prog_passes_90': True,
        'prog_carries_90': True,
        'prog_passes_final_third_90': True,
        'color_label': False
    },
    size='marker_size',
    size_max=25,
    opacity=0.8
)

fig.update_layout(
    title='Progressive Passes vs Carries per 90',
    xaxis_title='Prog Passes /90',
    yaxis_title='Prog Carries /90',
    legend_title_text='Player Type'
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Scatter plot 2: Passes vs Final Third
# -----------------------
st.subheader("Progressive Passes vs Final Third Entries per 90")

fig2 = px.scatter(
    mid_prog_df,
    x='prog_passes_90',
    y='prog_passes_final_third_90',
    color='color_label',
    color_discrete_map=COLOR_MAP,
    hover_name='player',
    hover_data={
        'total_games': True,
        'mid_games': True,
        'prog_passes_90': True,
        'prog_carries_90': True,
        'prog_passes_final_third_90': True,
        'color_label': False
    },
    size='marker_size',
    size_max=25,
    opacity=0.8
)

fig2.update_layout(
    title='Progressive Passes vs Final Third Entries',
    xaxis_title='Prog Passes /90',
    yaxis_title='Final Third /90',
    legend_title_text='Player Type'
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# Percentile ranks
# -----------------------
st.subheader(f"{selected_player} Percentile Ranks")

pp90 = float(player_data["prog_passes_90"].iloc[0])
pc90 = float(player_data["prog_carries_90"].iloc[0])
fte = float(player_data["prog_passes_final_third_90"].iloc[0])

st.write(f"Progressive Passes / 90: {percentileofscore(mid_prog_df['prog_passes_90'], pp90):.1f}th percentile")
st.write(f"Progressive Carries / 90: {percentileofscore(mid_prog_df['prog_carries_90'], pc90):.1f}th percentile")
st.write(f"Final Third Entries / 90: {percentileofscore(mid_prog_df['prog_passes_final_third_90'], fte):.1f}th percentile")

# -----------------------
# Ranking table
# -----------------------
st.subheader("Midfielders Rank Table")

metrics = [
    "prog_passes_90", 
    "prog_carries_90", 
    "prog_passes_final_third_90", 
    "prog_passes", 
    "prog_carries", 
    "prog_passes_final_third", 
    "total_games", 
    "mid_games"
]

selected_metric = st.selectbox("Select metric to rank by", metrics)

rank_table = mid_prog_df.sort_values(selected_metric, ascending=False).reset_index(drop=True)
rank_table["rank"] = rank_table.index + 1

rank_table = rank_table[[
    "rank", "player", "total_games", "mid_games",
    "prog_passes", "prog_carries", "prog_passes_final_third",
    "prog_passes_90", "prog_carries_90", "prog_passes_final_third_90"
]]

def highlight_players(row):
    if row["player"] == selected_player:
        return ['background-color: lightgreen' for _ in row]
    elif row["player"] == "Christian Dannemann Eriksen":
        return ['background-color: lightcoral' for _ in row]
    else:
        return ['' for _ in row]

st.dataframe(rank_table.style.apply(highlight_players, axis=1))
