import streamlit as st
import pickle
import pandas as pd
import requests

# Create a requests session for reuse
session = requests.Session()

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id, fallback_title=None):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=2498807bd454a3b3a8e6022e9e8ff557&language=en-US'
        response = session.get(url, timeout=15)  # increased timeout
        response.raise_for_status()
        data = response.json()

        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            print(f"[TMDB] No poster path for: {fallback_title} (ID: {movie_id})")
    except requests.exceptions.HTTPError as e:
        print(f"[TMDB] HTTP error for {fallback_title} (ID: {movie_id}) -> {e} ({response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"[TMDB] Network error for {fallback_title} (ID: {movie_id}) -> {e}")

    # Final fallback poster
    return "https://via.placeholder.com/500x750?text=No+Poster+Available"

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Selected movie not found in database.")
        return [], []

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        print(f"Recommending: {title} (ID: {movie_id})")
        poster_url = fetch_poster(movie_id, fallback_title=title)

        recommended_movies.append(title)
        recommended_posters.append(poster_url)

    return recommended_movies, recommended_posters

# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Which movie do you like?',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    if names and posters:
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx], use_container_width=True)
