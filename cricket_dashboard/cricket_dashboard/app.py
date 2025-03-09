import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px


# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Update with your MySQL username
        password="Dheeraj2004@",  # Update with your MySQL password
        database="cricket_analysis"
    )


# Fetch data from MySQL
def fetch_data(query):
    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# Load Data
players_df = fetch_data("SELECT player_id, name AS player_name, country, role FROM players")
matches_df = fetch_data("SELECT match_id, date, team1, team2, winner, match_type FROM matches")
performances_df = fetch_data("SELECT perf_id, match_id, player_id, runs_scored, wickets_taken FROM performance")

# Merge Data
merged_df = performances_df.merge(players_df, on="player_id", how="left").merge(matches_df, on="match_id", how="left")

# Sidebar Navigation
st.sidebar.title("🏏 Cricket Stats Dashboard")
page = st.sidebar.radio("Select Analysis", [
    "📋 Show Database Tables",
    "🏏 Batter Comparison",
    "🌍 Batting Averages by Country",
    "🎯 Bowling Averages by Country",
    "⚔️ Batsman vs Batsman (Country-wise)"
])

# Show raw database tables
if page == "📋 Show Database Tables":
    st.title("📊 Raw Database Tables")

    st.subheader("Players Table")
    st.dataframe(players_df)

    st.subheader("Matches Table")
    st.dataframe(matches_df)

    st.subheader("Performance Table")
    st.dataframe(performances_df)

# Batter Comparison
elif page == "🏏 Batter Comparison":
    st.title("🏏 Batter Comparison")

    # Select two batters
    batters = players_df[players_df["role"] != "Bowler"]["player_name"].unique()
    batter1 = st.sidebar.selectbox("Select First Batter", batters, index=0)
    batter2 = st.sidebar.selectbox("Select Second Batter", batters, index=1)

    # Filter data
    batter1_data = merged_df[merged_df["player_name"] == batter1]
    batter2_data = merged_df[merged_df["player_name"] == batter2]

    if batter1_data.empty or batter2_data.empty:
        st.warning("No data available for selected batters. Please choose different batters.")
    else:
        # Compute total and average runs
        avg_runs1 = batter1_data["runs_scored"].mean()
        avg_runs2 = batter2_data["runs_scored"].mean()
        total_runs1 = batter1_data["runs_scored"].sum()
        total_runs2 = batter2_data["runs_scored"].sum()

        # Dataframe for visualization
        batter_comparison_df = pd.DataFrame({
            "Batter": [batter1, batter2],
            "Avg Runs": [avg_runs1, avg_runs2],
            "Total Runs": [total_runs1, total_runs2]
        })

        st.subheader(f"Comparison of {batter1} and {batter2}")
        st.dataframe(batter_comparison_df)

        # Plot Bar Chart
        fig = px.bar(
            batter_comparison_df,
            x="Batter",
            y=["Avg Runs", "Total Runs"],
            barmode="group",
            title="Batter Performance Comparison"
        )
        st.plotly_chart(fig)

# Batting Averages by Country
elif page == "🌍 Batting Averages by Country":
    st.title("🌍 Batting Averages by Country")

    # Compute average runs per country
    country_avg_runs = merged_df.groupby("country")["runs_scored"].mean().reset_index()
    country_avg_runs.columns = ["Country", "Avg Runs"]

    st.dataframe(country_avg_runs)

    # Visualization
    fig = px.bar(
        country_avg_runs,
        x="Country",
        y="Avg Runs",
        title="Average Batting Performance by Country",
        text_auto=True
    )
    st.plotly_chart(fig)

# Bowling Averages by Country
elif page == "🎯 Bowling Averages by Country":
    st.title("🎯 Bowling Averages by Country")

    # Compute average wickets per country
    country_avg_wickets = merged_df.groupby("country")["wickets_taken"].mean().reset_index()
    country_avg_wickets.columns = ["Country", "Avg Wickets"]

    st.dataframe(country_avg_wickets)

    # Visualization
    fig = px.bar(
        country_avg_wickets,
        x="Country",
        y="Avg Wickets",
        title="Average Bowling Performance by Country",
        text_auto=True
    )
    st.plotly_chart(fig)

# Batsman vs Batsman (Country-wise)
elif page == "⚔️ Batsman vs Batsman (Country-wise)":
    st.title("⚔️ Batsman vs Batsman (Comparison)")

    # Select Batsmen
    batsmen = players_df[players_df["role"] != "Bowler"]["player_name"].unique()
    selected_batsman1 = st.sidebar.selectbox("Select First Batsman", batsmen, index=0)
    selected_batsman2 = st.sidebar.selectbox("Select Second Batsman", batsmen, index=1)

    # Filter data for both batsmen
    batsman1_df = merged_df[merged_df["player_name"] == selected_batsman1]
    batsman2_df = merged_df[merged_df["player_name"] == selected_batsman2]

    # Ensure valid data exists for both batsmen
    if batsman1_df.empty or batsman2_df.empty:
        st.warning("No data available for selected batsmen. Please choose different batsmen.")
    else:
        # Compute average runs
        avg_runs_batsman1 = batsman1_df["runs_scored"].mean()
        avg_runs_batsman2 = batsman2_df["runs_scored"].mean()

        # Fetch their country names
        country_batsman1 = batsman1_df["country"].unique()[0]
        country_batsman2 = batsman2_df["country"].unique()[0]

        # Create a comparison DataFrame
        comparison_df = pd.DataFrame({
            "Batsman": [selected_batsman1, selected_batsman2],
            "Country": [country_batsman1, country_batsman2],
            "Avg Runs": [avg_runs_batsman1, avg_runs_batsman2]
        })

        st.subheader(f"Comparison of {selected_batsman1} and {selected_batsman2}")

        # Display Data
        st.dataframe(comparison_df)

        # Bar Chart
        fig = px.bar(
            comparison_df,
            x="Batsman",
            y="Avg Runs",
            color="Country",
            title=f"Batting Average Comparison: {selected_batsman1} vs {selected_batsman2}",
            labels={"Avg Runs": "Average Runs"},
            text_auto=True
        )
        st.plotly_chart(fig)
