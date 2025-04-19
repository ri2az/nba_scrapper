import streamlit as st
import pandas as pd
import requests
import numpy as np
import datetime
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# ======================
# 📊 Charger les stats NBA par saison
# ======================
@st.cache_data
def get_player_stats(season_year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season_year}_per_game.html"
    r = requests.get(url)
    dfs = pd.read_html(r.text)
    df = dfs[0]

    df = df[df['Rk'] != 'Rk']
    df = df.dropna(subset=['Player'])
    df = df.fillna(0)
    df['Player'] = df['Player'].astype(str)
    df.reset_index(drop=True, inplace=True)

    needed_cols = ['PTS', 'AST', 'TRB', 'STL', 'BLK', 'FG%', '3P%', 'FT%', 'MP', 'G', 'FGA']
    for col in needed_cols:
        if col not in df.columns:
            df[col] = 0

    # Supprimer les doublons de joueurs en gardant la ligne avec le plus de matchs joués (G)
    df['G'] = pd.to_numeric(df['G'], errors='coerce')
    df = df.sort_values(by=['Player', 'G'], ascending=[True, False])
    df = df.drop_duplicates(subset='Player', keep='first')

    return df

# ======================
# 📊 Charger les stats avancées
# ======================
@st.cache_data
def get_advanced_stats(season_year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season_year}_advanced.html"
    r = requests.get(url)
    dfs = pd.read_html(r.text)
    df = dfs[0]

    df = df[df['Rk'] != 'Rk']
    df = df.dropna(subset=['Player'])
    df = df.fillna(0)
    df['Player'] = df['Player'].astype(str)
    df.reset_index(drop=True, inplace=True)

    advanced_cols = ['Player', 'PER', 'TS%', 'WS']
    df = df[advanced_cols]

    for col in ['PER', 'TS%', 'WS']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# ======================
# 🧠 Fonction de scoring MVP
# ======================
def calculate_mvp_score(df):
    df = df.copy()
    df["MVP Score"] = (
        df["PTS"] * 0.4 +
        df["AST"] * 0.2 +
        df["TRB"] * 0.15 +
        df["STL"] * 0.05 +
        df["BLK"] * 0.05 +
        df["FG%"] * 0.03 +
        df["3P%"] * 0.01 +
        df["FT%"] * 0.01 +
        df["PER"] * 0.05 +
        df["TS%"] * 0.03 +
        df["WS"] * 0.02
    )
    return df

# ======================
# 🎯 Interface Streamlit
# ======================
st.set_page_config(page_title="NBA - Stats & MVP", layout="wide")
st.title("\U0001F3C0 NBA – Stats des Joueurs & Prédictions MVP")

# Choix de la saison
selected_year = st.selectbox("\U0001F4C5 Sélectionner une saison NBA :", list(range(2025, 1980, -1)))
players_df = get_player_stats(selected_year)
advanced_df = get_advanced_stats(selected_year)

# Fusion des stats classiques et avancées
players_df = pd.merge(players_df, advanced_df, on='Player', how='left')

# ======================
# 📋 Stats générales
# ======================
st.subheader(f"\U0001F4CB Stats des joueurs - Saison {selected_year}")
st.dataframe(players_df.sort_values(by='PTS', ascending=False), use_container_width=True)

# ======================
# 👤 Stats joueur unique
# ======================
st.subheader("\U0001F464 Statistiques individuelles")
selected_player = st.selectbox("Choisir un joueur :", sorted(players_df["Player"].unique()))
player_stats = players_df[players_df["Player"] == selected_player].reset_index(drop=True)
st.dataframe(player_stats, use_container_width=True)

