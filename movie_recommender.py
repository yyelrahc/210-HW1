"""
movie_recommender.py

Command line movie recommendation system.

Features:
- Load movie and rating datasets
- Compute movie popularity
- Show top N movies
- Show top N movies in a genre
- Show top N genres
- Determine user's preferred genre
- Recommend movies to user

Designed for Python 3.12
"""

from collections import defaultdict


def load_movies(filename):
    """
    Load movies from a pipe-delimited file.

    Format per line:
        genre|movie_id|movie_name

    - Skips lines that don't have exactly 3 fields.
    - Strips whitespace from all fields.
    - Normalizes genre to lowercase.
    - Stores movie name in original casing for display, but keys the dict
      on the lowercase version so cross-file lookups are case-insensitive.
    - movie_id is parsed but validated to be non-empty before storing.

    Args:
        filename (str): Path to the movies file.

    Returns:
        dict: {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}
    """

    movies = {}

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                if len(parts) != 3:
                    print(f"Skipping malformed movie line: {line}")
                    continue

                genre, movie_id, movie_name = [p.strip() for p in parts]

                if not genre or not movie_id or not movie_name:
                    print(f"Skipping movie line with empty fields: {line}")
                    continue

                genre_original = genre
                genre_key = genre.lower()
                movie_key = movie_name.lower()

                if movie_key in movies:
                    print(f"Duplicate movie name in movies file (keeping first): {movie_name}")
                    continue

                movies[movie_key] = (movie_name, genre_key, genre_original)

    except FileNotFoundError:
        print(f"Movie file not found: {filename}")

    return movies


def load_ratings(filename):
    """
    Load movie ratings from a pipe-delimited file.

    Format per line:
        movie_name|rating|user_id

    - Skips lines that don't have exactly 3 fields.
    - Strips whitespace from all fields.
    - Normalizes movie names to lowercase to match movies file keys.
    - Validates that rating is a float between 0 and 5 inclusive.
    - If a user rates the same movie more than once, the duplicate is skipped
      with a warning (keeps both data structures in sync).

    Args:
        filename (str): Path to the ratings file.

    Returns:
        tuple:
            ratings (dict): {movie_name_lowercase: [list of float ratings]}
            user_ratings (dict): {user_id: {movie_name_lowercase: float rating}}
    """

    ratings = defaultdict(list)
    user_ratings = defaultdict(dict)

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                if len(parts) != 3:
                    print(f"Skipping malformed rating line: {line}")
                    continue

                movie_name, rating_str, user_id = [p.strip() for p in parts]

                if not movie_name or not user_id:
                    print(f"Skipping rating line with empty fields: {line}")
                    continue

                movie_key = movie_name.lower()

                try:
                    rating = float(rating_str)
                except ValueError:
                    print(f"Invalid rating value '{rating_str}' on line: {line}")
                    continue

                if rating < 0 or rating > 5:
                    print(f"Rating out of range ({rating}) on line: {line}")
                    continue

                if movie_key in user_ratings[user_id]:
                    print(f"Duplicate rating skipped — user '{user_id}' already rated '{movie_name}'")
                    continue

                ratings[movie_key].append(rating)
                user_ratings[user_id][movie_key] = rating

    except FileNotFoundError:
        print(f"Ratings file not found: {filename}")

    return ratings, user_ratings


def check_cross_file_consistency(movies, ratings):
    """
    Warn about movies that appear in the ratings file but not in the movies file.

    These orphaned ratings are excluded from all genre-based and recommendation features.

    Args:
        movies (dict): {movie_name_lowercase: ...}
        ratings (dict): {movie_name_lowercase: [list of float ratings]}
    """

    for movie_key in ratings:
        if movie_key not in movies:
            print(f"Warning: rated movie '{movie_key}' not found in movies file — will be excluded from genre features.")


def movie_popularity(ratings):
    """
    Compute the average rating for each movie.

    Movies with no ratings are excluded.

    Args:
        ratings (dict): {movie_name_lowercase: [list of float ratings]}

    Returns:
        dict: {movie_name_lowercase: average_rating (float)}
    """

    popularity = {}

    for movie, rating_list in ratings.items():
        if len(rating_list) == 0:
            continue
        popularity[movie] = sum(rating_list) / len(rating_list)

    return popularity


def top_n_movies(movies, popularity, n):
    """
    Return the top N movies ranked by average rating (descending).

    Ties are broken alphabetically by original movie name (ascending).

    Args:
        movies (dict): {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}
        popularity (dict): {movie_name_lowercase: average_rating (float)}
        n (int): Number of top movies to return. Must be an integer >= 1.

    Returns:
        list of (movie_name_original, average_rating) tuples, or [] if n < 1.
    """

    if not isinstance(n, int):
        print("N must be an integer.")
        return []

    if n < 1:
        print("N must be at least 1.")
        return []

    results = []
    for movie_key, score in popularity.items():
        if movie_key not in movies:
            continue
        display_name = movies[movie_key][0]
        results.append((display_name, score))

    results.sort(key=lambda x: (-x[1], x[0].lower()))

    return results[:n]


def top_n_movies_in_genre(movies, popularity, genre, n):
    """
    Return the top N movies in a specific genre ranked by average rating (descending).

    Ties are broken alphabetically by original movie name.
    Genre matching is case-insensitive.

    Args:
        movies (dict): {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}
        popularity (dict): {movie_name_lowercase: average_rating (float)}
        genre (str): Genre to filter by.
        n (int): Number of top movies to return. Must be an integer >= 1.

    Returns:
        list of (movie_name_original, average_rating) tuples.
    """

    if not isinstance(n, int):
        print("N must be an integer.")
        return []

    if n < 1:
        print("N must be at least 1.")
        return []

    genre = genre.strip().lower()

    filtered = []
    for movie_key, (original_name, g, _) in movies.items():
        if g == genre and movie_key in popularity:
            filtered.append((original_name, popularity[movie_key]))

    if not filtered:
        print(f"No rated movies found in genre: '{genre}'")
        return []

    filtered.sort(key=lambda x: (-x[1], x[0].lower()))

    return filtered[:n]


def genre_popularity(movies, popularity):
    """
    Compute the popularity of each genre.

    Genre popularity = average of the average ratings of all movies in that genre.
    Only movies that appear in both the movies dict and the popularity dict are counted.

    Args:
        movies (dict): {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}
        popularity (dict): {movie_name_lowercase: average_rating (float)}

    Returns:
        dict: {genre_original: average_of_averages (float)}
    """

    genre_scores = defaultdict(list)
    genre_display = {}

    for movie_key, (original_name, genre_key, genre_original) in movies.items():
        if movie_key in popularity:
            genre_scores[genre_key].append(popularity[movie_key])
            if genre_key not in genre_display:
                genre_display[genre_key] = genre_original

    genre_avg = {}

    for genre_key, scores in genre_scores.items():
        if scores:
            display = genre_display.get(genre_key, genre_key)
            genre_avg[display] = sum(scores) / len(scores)

    return genre_avg


def top_n_genres(movies, popularity, n):
    """
    Return the top N genres ranked by average of average ratings (descending).

    Ties are broken alphabetically by genre name (ascending).

    Args:
        movies (dict): {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}
        popularity (dict): {movie_name_lowercase: average_rating (float)}
        n (int): Number of top genres to return. Must be an integer >= 1.

    Returns:
        list of (genre_original, average_rating) tuples, or [] if n < 1.
    """

    if not isinstance(n, int):
        print("N must be an integer.")
        return []

    if n < 1:
        print("N must be at least 1.")
        return []

    gp = genre_popularity(movies, popularity)
    sorted_genres = sorted(gp.items(), key=lambda x: (-x[1], x[0].lower()))
    return sorted_genres[:n]


def user_preferred_genre(user_id, user_ratings, movies):
    """
    Determine the genre most preferred by a user.

    Preferred genre = genre with highest average of the user's ratings
    for movies in that genre.

    Ties are broken alphabetically (ascending) by genre display name (lowercased)
    for consistency.

    Args:
        user_id (str): The user's ID.
        user_ratings (dict): {user_id: {movie_name_lowercase: rating}}
        movies (dict): {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}

    Returns:
        str: The preferred genre name (original casing), or None if user has no valid rated movies.
    """

    if user_id not in user_ratings:
        print(f"User '{user_id}' not found.")
        return None

    genre_scores = defaultdict(list)
    genre_display = {}

    for movie_key, rating in user_ratings[user_id].items():
        if movie_key in movies:
            genre_key = movies[movie_key][1]
            genre_original = movies[movie_key][2]
            genre_scores[genre_key].append(rating)
            if genre_key not in genre_display:
                genre_display[genre_key] = genre_original
        else:
            print(f"Warning: rated movie '{movie_key}' not found in movies dataset.")

    if not genre_scores:
        print(f"User '{user_id}' has no ratings for known movies.")
        return None

    genre_avg = {
        genre_key: sum(scores) / len(scores)
        for genre_key, scores in genre_scores.items()
        if scores
    }

    if not genre_avg:
        return None

    best_key = sorted(genre_avg, key=lambda g: (-genre_avg[g], genre_display.get(g, g).lower()))[0]
    return genre_display.get(best_key, best_key)


def recommend_movies(user_id, movies, ratings, user_ratings):
    """
    Recommend up to 3 movies from the user's preferred genre
    that the user has not yet rated.

    Only movies that have at least one rating (i.e., appear in popularity)
    are considered as candidates.

    Args:
        user_id (str): The user's ID.
        movies (dict): {movie_name_lowercase: (movie_name_original, genre_lowercase, genre_original)}
        ratings (dict): {movie_name_lowercase: [list of float ratings]}
        user_ratings (dict): {user_id: {movie_name_lowercase: rating}}

    Returns:
        list of (movie_name_original, average_rating) tuples (up to 3), or [] if none found.
    """

    if user_id not in user_ratings:
        print(f"User '{user_id}' not found.")
        return []

    popularity = movie_popularity(ratings)

    preferred_genre = user_preferred_genre(user_id, user_ratings, movies)

    if preferred_genre is None:
        print("Cannot determine preferred genre — no recommendations available.")
        return []

    preferred_genre_key = preferred_genre.lower()

    rated_movies = set(user_ratings[user_id].keys())

    candidates = []
    for movie_key, (original_name, genre_key, genre_original) in movies.items():
        if genre_key == preferred_genre_key and movie_key not in rated_movies and movie_key in popularity:
            candidates.append((original_name, popularity[movie_key]))

    if not candidates:
        print(f"No unrated movies with existing ratings found in genre '{preferred_genre}'.")
        return []

    candidates.sort(key=lambda x: (-x[1], x[0].lower()))

    return candidates[:3]


def menu():
    """
    Command line interface for the movie recommendation system.

    Provides options to load data files and test each feature interactively.
    """

    movies = {}
    ratings = {}
    user_ratings = {}

    while True:

        print("\nMovie Recommendation System")
        print("1. Load movies file")
        print("2. Load ratings file")
        print("3. Show top N movies")
        print("4. Show top N movies in genre")
        print("5. Show top N genres")
        print("6. Show user preferred genre")
        print("7. Recommend movies for user")
        print("8. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            filename = input("Enter movies filename: ").strip()
            movies = load_movies(filename)
            if movies:
                print(f"Loaded {len(movies)} movies.")
                if ratings:
                    check_cross_file_consistency(movies, ratings)
            else:
                print("No movies loaded.")

        elif choice == "2":
            filename = input("Enter ratings filename: ").strip()
            ratings, user_ratings = load_ratings(filename)
            if ratings:
                print(f"Loaded ratings for {len(ratings)} movies.")
                if movies:
                    check_cross_file_consistency(movies, ratings)
            else:
                print("No ratings loaded.")

        elif choice == "3":
            # Require both files loaded, consistent with all other feature options
            if not ratings or not movies:
                print("Load both movies and ratings files first.")
                continue

            try:
                n = int(input("Enter number of movies: ").strip())
            except ValueError:
                print("Invalid number.")
                continue

            popularity = movie_popularity(ratings)
            results = top_n_movies(movies, popularity, n)

            if results:
                print(f"\nTop {n} Movies:")
                for movie, score in results:
                    print(f"  {movie}: {round(score, 2)}")
            else:
                print("No results.")

        elif choice == "4":
            if not ratings or not movies:
                print("Load both movies and ratings files first.")
                continue

            genre = input("Enter genre: ").strip()
            if not genre:
                print("Genre cannot be empty.")
                continue

            try:
                n = int(input("Enter number of movies: ").strip())
            except ValueError:
                print("Invalid number.")
                continue

            popularity = movie_popularity(ratings)
            results = top_n_movies_in_genre(movies, popularity, genre, n)

            if results:
                print(f"\nTop {n} Movies in '{genre}':")
                for movie, score in results:
                    print(f"  {movie}: {round(score, 2)}")
            else:
                print("No results.")

        elif choice == "5":
            if not ratings or not movies:
                print("Load both movies and ratings files first.")
                continue

            try:
                n = int(input("Enter number of genres: ").strip())
            except ValueError:
                print("Invalid number.")
                continue

            popularity = movie_popularity(ratings)
            results = top_n_genres(movies, popularity, n)

            if results:
                print(f"\nTop {n} Genres:")
                for genre, score in results:
                    print(f"  {genre}: {round(score, 2)}")
            else:
                print("No genre data available.")

        elif choice == "6":
            if not ratings or not movies:
                print("Load both movies and ratings files first.")
                continue

            user_id = input("Enter user ID: ").strip()
            if not user_id:
                print("User ID cannot be empty.")
                continue

            preferred = user_preferred_genre(user_id, user_ratings, movies)

            if preferred:
                print(f"User '{user_id}' preferred genre: {preferred}")

        elif choice == "7":
            if not ratings or not movies:
                print("Load both movies and ratings files first.")
                continue

            user_id = input("Enter user ID: ").strip()
            if not user_id:
                print("User ID cannot be empty.")
                continue

            recs = recommend_movies(user_id, movies, ratings, user_ratings)

            if recs:
                print(f"\nRecommended movies for user '{user_id}':")
                for movie, score in recs:
                    print(f"  {movie}: {round(score, 2)}")

        elif choice == "8":
            print("Exiting program.")
            break

        else:
            print("Invalid menu option. Please enter a number between 1 and 8.")


if __name__ == "__main__":
    menu()
