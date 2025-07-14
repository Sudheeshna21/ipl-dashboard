import streamlit as st
import pandas as pd
import plotly.express as px
import os

@st.cache_data
def load_data():
    if not os.path.exists("matches.csv") or not os.path.exists("deliveries.csv"):
        st.error("CSV files not found! Make sure they are in the same directory as app.py.")
        st.stop()
    
    matches = pd.read_csv("matches.csv")
    deliveries = pd.read_csv("deliveries.csv")
    return matches, deliveries
matches_df, deliveries_df = load_data()

st.set_page_config(layout="wide")
st.title("🏏 IPL Dashboard (2008 - 2024)")

with st.sidebar:
    st.header("🎛️ Filters")
    all_seasons = sorted(matches_df["season"].unique())
    selected_season = st.selectbox("📅 Select Season", all_seasons)

    season_matches = matches_df[matches_df["season"] == selected_season]
    season_match_ids = season_matches["id"].unique()
    season_deliveries = deliveries_df[deliveries_df["match_id"].isin(season_match_ids)]

    batters = sorted(season_deliveries["batter"].dropna().unique())
    bowlers = sorted(season_deliveries["bowler"].dropna().unique())
    selected_batsman = st.selectbox("🧢 Batsman", batters)
    selected_bowler = st.selectbox("🎯 Bowler", bowlers)

    teams = sorted(matches_df["team1"].dropna().unique())
    team1 = st.selectbox("🏏 Team A", teams)
    team2 = st.selectbox("🏏 Team B", teams)

st.header(f"📊 Season Overview - {selected_season}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches", season_matches.shape[0])
col2.metric("Cities", season_matches["city"].nunique())
col3.metric("Teams", season_matches["team1"].nunique())
col4.metric("Venues", season_matches["venue"].nunique())

winner_count = season_matches["winner"].value_counts()
fig = px.bar(x=winner_count.index, y=winner_count.values,
             title="🏆 Wins Per Team", labels={"x": "Team", "y": "Wins"})
st.plotly_chart(fig, use_container_width=True)

st.subheader("🌟 Top Performers")

top_batsmen = season_deliveries.groupby("batter")["batsman_runs"].sum().sort_values(ascending=False).head(5)
fig2 = px.bar(x=top_batsmen.index, y=top_batsmen.values,
              labels={"x": "Batsman", "y": "Runs"}, color=top_batsmen.values,
              title="🟠 Orange Cap - Most Runs")
st.plotly_chart(fig2, use_container_width=True)

wickets_df = season_deliveries[season_deliveries["dismissal_kind"].notnull()]
wickets_df = wickets_df[~wickets_df["dismissal_kind"].isin(["run out", "retired hurt", "obstructing the field"])]
top_bowlers = wickets_df["bowler"].value_counts().head(5)
fig3 = px.bar(x=top_bowlers.index, y=top_bowlers.values,
              labels={"x": "Bowler", "y": "Wickets"}, color=top_bowlers.values,
              title="🟣 Purple Cap - Most Wickets")
st.plotly_chart(fig3, use_container_width=True)

top_mom = season_matches["player_of_match"].value_counts().head(5)
fig4 = px.bar(x=top_mom.index, y=top_mom.values,
              labels={"x": "Player", "y": "Awards"}, color=top_mom.values,
              title="🏆 Most Player of the Match Awards")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("🆚 Player vs Player Stats")

pvp_df = season_deliveries[(season_deliveries["batter"] == selected_batsman) &
                           (season_deliveries["bowler"] == selected_bowler)]

if pvp_df.empty:
    st.warning("No data for this matchup.")
else:
    runs = pvp_df["batsman_runs"].sum()
    balls = pvp_df.shape[0]
    dismissals = pvp_df[pvp_df["player_dismissed"] == selected_batsman].shape[0]
    strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0
    boundaries = pvp_df[pvp_df["batsman_runs"].isin([4, 6])]["batsman_runs"].value_counts()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Runs", runs)
    col2.metric("Balls", balls)
    col3.metric("Dismissals", dismissals)
    col4.metric("Strike Rate", strike_rate)
    st.write(f"🏏 Fours: {boundaries.get(4,0)} &nbsp;&nbsp; 🔥 Sixes: {boundaries.get(6,0)}")

st.subheader("🏟️ Head-to-Head Battle")

if team1 != team2:
    h2h_df = matches_df[((matches_df["team1"] == team1) & (matches_df["team2"] == team2)) |
                        ((matches_df["team1"] == team2) & (matches_df["team2"] == team1))]
    total = h2h_df.shape[0]
    t1_wins = h2h_df[h2h_df["winner"] == team1].shape[0]
    t2_wins = h2h_df[h2h_df["winner"] == team2].shape[0]
    ties = total - t1_wins - t2_wins

    col1, col2, col3 = st.columns(3)
    col1.metric(f"{team1} Wins", t1_wins)
    col2.metric(f"{team2} Wins", t2_wins)
    col3.metric("Ties/Other", ties)

    fig5 = px.pie(names=[team1, team2, "Tie/Other"],
                  values=[t1_wins, t2_wins, ties],
                  title="Head-to-Head Record")
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("Choose two different teams.")

st.subheader("⚡ Thriller of the Season")

thrillers = season_matches[season_matches["result"] == "normal"].sort_values(by="result_margin")
if not thrillers.empty:
    thriller = thrillers.iloc[0]
    st.markdown(f"""
    - 🏟️ **Venue**: {thriller['venue']}
    - 📅 **Date**: {thriller['date']}
    - 🆚 **Match**: {thriller['team1']} vs {thriller['team2']}
    - 🏆 **Winner**: {thriller['winner']}
    - 📊 **Result Margin**: {thriller['result_margin']}
    """)
else:
    st.info("No close match found for this season.")

st.subheader("📈 Batting & Bowling Leaders")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏏 Top Run Scorers")
    top_batsmen = season_deliveries.groupby("batter")["batsman_runs"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_batsmen)

    st.markdown("#### 💣 Top Six Hitters")
    most_sixes = season_deliveries[season_deliveries["batsman_runs"] == 6]["batter"].value_counts().head(10)
    st.bar_chart(most_sixes)

with col2:
    st.markdown("#### 🎯 Top Wicket Takers")
    top_wickets = wickets_df["bowler"].value_counts().head(10)
    st.bar_chart(top_wickets)

    st.markdown("#### 🧊 Dot Ball Specialists")
    dot_balls = season_deliveries[season_deliveries["total_runs"] == 0]
    dot_bowlers = dot_balls["bowler"].value_counts().head(10)
    st.bar_chart(dot_bowlers)
