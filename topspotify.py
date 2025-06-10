# IMPORT LIBRARIES
import pandas as pd
import plotly.express as px
import streamlit as st 
import seaborn as sns
import matplotlib.pyplot as plt 

# MEMBUAT KONFIGURASI PADA CANVAS DASHBOARD
st.set_page_config(
  page_title="Spotify Dashboard",
  page_icon="💽",
  layout="wide"                 
)

# MENENTUKAN TEMA WARNA DASHBOARD
st.markdown(
    """
    <style>
    .stApp {
        background-color: #191414;
        color: #1DB954;
    }

    div[data-testid="stMetricValue"], 
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, 
    .stMarkdown h5, .stMarkdown h6, 
    div[data-testid="stMarkdownContainer"] > p {
        color: #1DB954 !important;
        font-weight: bold;

    .stButton>button {
        background-color: #1DB954; 
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #00796B;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_data():
    df = pd.read_csv("dataspotify_baru.csv")
    df = df.rename(columns={
        "track_name": "Title",
        "track_artist": "Artist",
        "track_popularity": "Popularity",
        "track_album_name": "Album",
        "track_album_release_date": "Release_Date",
        "playlist_genre": "Genre",
        "danceability": "Danceability",
        "valence": "Valence",
        "acousticness": "Acousticness",
        "instrumentalness": "Instrumentalness",
        "track_id": "Track_ID"
    })
    df["Release_Year"] = pd.to_datetime(df["Release_Date"], errors="coerce").dt.year
    df = df.dropna(subset=["Title", "Artist", "Popularity", "Release_Year", "Genre"])
    df = df.drop_duplicates(subset=["Track_ID"])
    return df

df = load_data()

# MEMBUAT HEADER PADA DASHBOARD
st.title("💽 Spotify Dashboard")
st.write("⭐ Jelajahi lagu di Spotify! Temukan artis, lagu, dan genre terpopuler serta cari lagu yang cocok untuk suasana hatimu.")
# Membuat button klik yang menampilkan credit
klik = st.button("Click Here for Credit")
if klik:
    st.write("Created by Kelompok 7")
    st.write("Data Source: Spotify Dataset")
st.markdown("##")

# MEMBUAT SIDEBAR
st.sidebar.header("🎛️ Filter")

genre_sb = st.sidebar.multiselect(
    "Pilih Genre:",
    options=df["Genre"].unique(),
    default=df["Genre"].unique()
)

year_sb = st.sidebar.multiselect(
    "Pilih Tahun:",
    options=sorted(df["Release_Year"].unique()),
    default=sorted(df["Release_Year"].unique())
)

# Filter Data berdasarkan input user
df_selection = df[
    (df["Genre"].isin(genre_sb)) &
    (df["Release_Year"].isin(year_sb))
]


# KPI Section
col1, col2, col3, col4, col5 = st.columns(5)

# Top Artist
popular_df = df_selection[df_selection["Popularity"] >= 50]
top_artist_name = popular_df["Artist"].value_counts().idxmax()
top_artist_count = popular_df["Artist"].value_counts().max()
col1.metric("🎤 Top Artist", top_artist_name)

# Top Song
top_song = popular_df.sort_values("Popularity", ascending=False).iloc[0]
col2.metric("🎧 Top Song", top_song["Title"])

# Top Genre
top_genre = popular_df["Genre"].value_counts().idxmax()
col3.metric("🎼 Top Genre", top_genre)

# Top Album
top_album_name = popular_df["Album"].value_counts().idxmax()
top_album_count = popular_df["Album"].value_counts().max()
col4.metric("💿 Top Album", top_album_name)

# Rata-rata Valence
avg_val = popular_df["Valence"].mean()
col5.metric("🤍 Music Valence", f"{avg_val:.2f}")


# TOP LAGU
st.subheader("🎧 Top 10 Songs")
top_songs = popular_df.sort_values(by="Popularity", ascending=False).head(10)
top_songs_display = top_songs.reset_index(drop=True)
top_songs_display.index = top_songs_display.index + 1
top_songs_display.index.name = "No"
st.dataframe(top_songs_display[["Title", "Artist"]])

# TOP ARTIS
st.subheader("🎤 Top 10 Artists")
top_artists = popular_df["Artist"].value_counts().head(10).reset_index()
top_artists.columns = ["Artist", "Jumlah Lagu Populer"]
fig_artists = px.bar(top_artists, x="Artist", y="Jumlah Lagu Populer")
st.plotly_chart(fig_artists)

# REKOMENDASI LAGU
st.subheader("🔍 Temukan Lagu Favoritmu!")
# Slider input
acoustic_slider = st.slider("Minimum Acousticness", 0.0, 1.0, 0.5)
dance_slider = st.slider("Minimum Danceability", 0.0, 1.0, 0.5)

recommended = df_selection[
    (df_selection["Acousticness"] >= acoustic_slider) &
    (df_selection["Danceability"] >= dance_slider)
].sort_values(by="Popularity", ascending=False).head(10)

recommended_display = recommended.reset_index(drop=True)
recommended_display.index = recommended_display.index + 1
recommended_display.index.name = "No"

st.dataframe(recommended_display[["Title", "Artist"]])

# SEBARAN GENRE
st.subheader("🪩 Sebaran Genre pada Danceability dan Acousticness")
fig = px.scatter(df_selection, x="Acousticness", y="Danceability",
                 color="Genre", hover_data=["Title", "Artist"])
st.plotly_chart(fig)

# TOP GENRE
st.subheader("🎼 Top 10 Genres")
top_genres = popular_df["Genre"].value_counts().head(10).reset_index()
top_genres.columns = ["Genre", "Jumlah"]

fig_genre = px.pie(
    top_genres,
    names="Genre",
    values="Jumlah",
    hole=0.4  # untuk membuatnya seperti donut chart
)
st.plotly_chart(fig_genre)


# TOP ALBUM
st.subheader("💿 Top 10 Albums")
top_albums = popular_df["Album"].value_counts().head(10).reset_index()
top_albums.columns = ["Album", "Jumlah Lagu Populer"]

fig_album = px.bar(
    top_albums,
    x="Jumlah Lagu Populer",
    y="Album",
    orientation="h",
    color="Jumlah Lagu Populer",
    color_continuous_scale="Greens",
    category_orders={"Album": top_albums.sort_values("Jumlah Lagu Populer", ascending=False)["Album"]}
)
st.plotly_chart(fig_album)

