"""
test_movie_recommender.py

Automatic tester for movie_recommender.py

This script validates movie recommender functions by checking data types, 
sorting orders, and edge cases. 

Usage:
    1. Command Line: python test_movie_recommender.py <movies_file> <ratings_file>
    2. Interactive:  python test_movie_recommender.py 
       (Script will prompt for filenames or use defaults if Enter is pressed)
"""

import os
import sys
import movie_recommender as mr


def passed(msg):
    print(f"  PASS: {msg}")


def failed(msg):
    print(f"  FAIL: {msg}")


# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────

def load_data():
    print("=" * 50)
    print("Loading data files...")
    print("=" * 50)

    # Accept filenames as command line arguments so any files can be used:
    #   > python test_movie_recommender.py movies.txt ratings.txt
    # Falls back to default names if no arguments provided.
    if len(sys.argv) == 3:
        movies_file = sys.argv[1]
        ratings_file = sys.argv[2]
    else:
        # No arguments, ask the user to type the name and assign values or defaults.
        print("No filenames provided in command line.\n")
        m_input = input("Enter movies file (Default: 'genreMovieSample.txt'): ").strip()
        movies_file = m_input if m_input else "genreMovieSample.txt"
        if not m_input:
            print(f"  -> Using default: {movies_file}\n")

        r_input = input("Enter ratings file (Default: 'movieRatingSample.txt'): ").strip()
        ratings_file = r_input if r_input else "movieRatingSample.txt"
        if not r_input:
            print(f"  -> Using default: {ratings_file}\n")

    if not os.path.exists(movies_file):
        print(f"ERROR: '{movies_file}' not found.")
        exit(1)

    if not os.path.exists(ratings_file):
        print(f"ERROR: '{ratings_file}' not found.")
        exit(1)

    movies = mr.load_movies(movies_file)
    ratings, user_ratings = mr.load_ratings(ratings_file)
    popularity = mr.movie_popularity(ratings)

    print(f"  Movies loaded:  {len(movies)}")
    print(f"  Ratings loaded: {len(ratings)} movies rated")
    print(f"  Users loaded:   {len(user_ratings)}")

    return movies, ratings, user_ratings, popularity


# ─────────────────────────────────────────────
# Test: load_movies
# ─────────────────────────────────────────────

def test_load_movies(movies):
    print("\n--- test_load_movies ---")

    assert isinstance(movies, dict), "movies should be a dict"
    passed("load_movies returns a dict")

    assert len(movies) > 0, "movies dict should not be empty"
    passed("load_movies loaded at least one movie")

    for key, val in movies.items():
        assert isinstance(key, str), f"movie key should be str, got {type(key)}"
        assert isinstance(val, tuple) and len(val) == 3, \
            f"movie value should be 3-tuple, got {val}"
        original_name, genre_key, genre_original = val
        assert isinstance(original_name, str) and original_name, \
            "original_name should be non-empty string"
        assert isinstance(genre_key, str) and genre_key, \
            "genre_key should be non-empty string"
        assert genre_key == genre_key.lower(), \
            f"genre_key should be lowercase, got '{genre_key}'"
        assert key == key.lower(), \
            f"movie key should be lowercase, got '{key}'"
    passed("all movie entries have correct structure and lowercase keys")

    for key, (original_name, _, _) in movies.items():
        assert key == original_name.lower(), \
            f"key '{key}' should match lowercase of '{original_name}'"
    passed("movie keys are lowercase of original names")

    passed("no duplicate movie keys (enforced by dict structure)")


# ─────────────────────────────────────────────
# Test: load_ratings
# ─────────────────────────────────────────────

def test_load_ratings(ratings, user_ratings):
    print("\n--- test_load_ratings ---")

    assert isinstance(ratings, dict), "ratings should be a dict"
    passed("load_ratings returns ratings dict")

    assert isinstance(user_ratings, dict), "user_ratings should be a dict"
    passed("load_ratings returns user_ratings dict")

    for movie_key, rating_list in ratings.items():
        assert isinstance(rating_list, list), \
            f"ratings['{movie_key}'] should be a list"
        for r in rating_list:
            assert isinstance(r, float), \
                f"rating should be float, got {type(r)}"
            assert 0.0 <= r <= 5.0, \
                f"rating {r} out of range [0, 5]"
    passed("all ratings are floats in range [0, 5]")

    # Tolerance-based float comparison to avoid floating point false negatives
    for user_id, rated_movies in user_ratings.items():
        for movie_key, r in rated_movies.items():
            assert movie_key in ratings, \
                f"movie '{movie_key}' in user_ratings but not in ratings"
            assert any(abs(r - x) < 1e-9 for x in ratings[movie_key]), \
                f"rating {r} for '{movie_key}' missing from ratings list"
    passed("user_ratings is consistent with ratings dict")

    for user_id, rated_movies in user_ratings.items():
        movie_keys = list(rated_movies.keys())
        assert len(movie_keys) == len(set(movie_keys)), \
            f"user '{user_id}' has duplicate ratings"
    passed("no user has duplicate ratings")


# ─────────────────────────────────────────────
# Test: movie_popularity
# ─────────────────────────────────────────────

def test_movie_popularity(ratings, popularity):
    print("\n--- test_movie_popularity ---")

    assert isinstance(popularity, dict), "popularity should be a dict"
    passed("movie_popularity returns a dict")

    for movie_key, rating_list in ratings.items():
        if rating_list:
            assert movie_key in popularity, \
                f"rated movie '{movie_key}' missing from popularity"
    passed("all rated movies appear in popularity")

    for movie_key, score in popularity.items():
        assert isinstance(score, float), \
            f"popularity score should be float, got {type(score)}"
        assert 0.0 <= score <= 5.0, \
            f"popularity score {score} out of range"
    passed("all popularity scores are floats in [0, 5]")

    for movie_key, score in popularity.items():
        if movie_key in ratings and ratings[movie_key]:
            expected = sum(ratings[movie_key]) / len(ratings[movie_key])
            assert abs(score - expected) < 1e-9, \
                f"wrong average for '{movie_key}': got {score}, expected {expected}"
    passed("popularity scores are correct averages")


# ─────────────────────────────────────────────
# Test: top_n_movies
# ─────────────────────────────────────────────

def test_top_n_movies(movies, popularity):
    print("\n--- test_top_n_movies ---")

    result = mr.top_n_movies(movies, popularity, 0)
    assert result == [], f"n=0 should return [], got {result}"
    passed("n=0 returns empty list")

    result = mr.top_n_movies(movies, popularity, -5)
    assert result == [], f"negative n should return [], got {result}"
    passed("negative n returns empty list")

    result = mr.top_n_movies(movies, popularity, 1)
    assert len(result) <= 1, f"n=1 should return at most 1, got {len(result)}"
    passed("n=1 returns at most 1 result")

    result = mr.top_n_movies(movies, popularity, 99999)
    assert isinstance(result, list), "large n should still return a list"
    passed("n larger than total movies returns all available movies")

    n = 5
    result = mr.top_n_movies(movies, popularity, n)
    assert len(result) <= n, f"result length {len(result)} exceeds n={n}"
    passed(f"top_n_movies returns at most {n} results")

    scores = [score for _, score in result]
    assert scores == sorted(scores, reverse=True), \
        f"results not sorted descending: {scores}"
    passed("results are sorted by score descending")

    for movie_name, score in result:
        assert movie_name.lower() in movies, \
            f"'{movie_name}' not found in movies dict"
    passed("all returned movies exist in movies dict")

    for _, score in result:
        assert isinstance(score, float), f"score should be float, got {type(score)}"
    passed("all scores are floats")

    for i in range(len(result) - 1):
        name_a, score_a = result[i]
        name_b, score_b = result[i + 1]
        if abs(score_a - score_b) < 1e-9:
            assert name_a.lower() <= name_b.lower(), \
                f"tie not broken alphabetically: '{name_a}' vs '{name_b}'"
    passed("ties broken alphabetically ascending")


# ─────────────────────────────────────────────
# Test: top_n_movies_in_genre
# ─────────────────────────────────────────────

def test_top_n_movies_in_genre(movies, popularity):
    print("\n--- test_top_n_movies_in_genre ---")

    result = mr.top_n_movies_in_genre(movies, popularity, "fakegenreXYZ999", 5)
    assert result == [], f"nonexistent genre should return [], got {result}"
    passed("nonexistent genre returns empty list")

    if movies:
        some_genre = next(iter(movies.values()))[1]
        result = mr.top_n_movies_in_genre(movies, popularity, some_genre, 0)
        assert result == [], f"n=0 should return [], got {result}"
        passed("n=0 returns empty list")

    if movies:
        genre_lower = next(iter(movies.values()))[1]
        genre_upper = genre_lower.upper()
        result_lower = mr.top_n_movies_in_genre(movies, popularity, genre_lower, 5)
        result_upper = mr.top_n_movies_in_genre(movies, popularity, genre_upper, 5)
        assert result_lower == result_upper, \
            "genre matching should be case-insensitive"
        passed("genre matching is case-insensitive")

    genre_with_ratings = None
    for movie_key, (_, genre_key, _) in movies.items():
        if movie_key in popularity:
            genre_with_ratings = genre_key
            break

    if genre_with_ratings:
        n = 5
        result = mr.top_n_movies_in_genre(movies, popularity, genre_with_ratings, n)
        assert len(result) <= n, f"result length {len(result)} exceeds n={n}"
        passed(f"returns at most {n} results for valid genre")

        for movie_name, score in result:
            movie_key = movie_name.lower()
            assert movie_key in movies, f"'{movie_name}' not in movies dict"
            assert movies[movie_key][1] == genre_with_ratings.lower(), \
                f"'{movie_name}' is not in genre '{genre_with_ratings}'"
        passed("all returned movies belong to the correct genre")

        scores = [score for _, score in result]
        assert scores == sorted(scores, reverse=True), \
            f"results not sorted descending: {scores}"
        passed("results sorted by score descending")

        for i in range(len(result) - 1):
            name_a, score_a = result[i]
            name_b, score_b = result[i + 1]
            if abs(score_a - score_b) < 1e-9:
                assert name_a.lower() <= name_b.lower(), \
                    f"tie not broken alphabetically: '{name_a}' vs '{name_b}'"
        passed("ties broken alphabetically ascending")


# ─────────────────────────────────────────────
# Test: genre_popularity
# ─────────────────────────────────────────────

def test_genre_popularity(movies, popularity):
    print("\n--- test_genre_popularity ---")

    gp = mr.genre_popularity(movies, popularity)

    assert isinstance(gp, dict), "genre_popularity should return a dict"
    passed("genre_popularity returns a dict")

    for genre, score in gp.items():
        assert isinstance(score, float), \
            f"genre score should be float, got {type(score)}"
        assert 0.0 <= score <= 5.0, \
            f"genre score {score} out of range for '{genre}'"
    passed("all genre scores are floats in [0, 5]")

    known_genres = {v[1] for v in movies.values()}
    for genre_display in gp.keys():
        assert genre_display.lower() in known_genres, \
            f"genre '{genre_display}' not found in movies"
    passed("all genres in result exist in movies data")

    genres_with_ratings = set()
    for movie_key, (_, genre_key, _) in movies.items():
        if movie_key in popularity:
            genres_with_ratings.add(genre_key)
    for genre_display in gp.keys():
        assert genre_display.lower() in genres_with_ratings, \
            f"genre '{genre_display}' has no rated movies but appears in result"
    passed("only genres with rated movies appear in result")

    result_empty = mr.genre_popularity(movies, {})
    assert result_empty == {}, \
        f"empty popularity should yield empty genre_popularity, got {result_empty}"
    passed("empty popularity returns empty dict")


# ─────────────────────────────────────────────
# Test: top_n_genres
# ─────────────────────────────────────────────

def test_top_n_genres(movies, popularity):
    print("\n--- test_top_n_genres ---")

    result = mr.top_n_genres(movies, popularity, 0)
    assert result == [], f"n=0 should return [], got {result}"
    passed("n=0 returns empty list")

    result = mr.top_n_genres(movies, popularity, -5)
    assert result == [], f"negative n should return [], got {result}"
    passed("negative n returns empty list")

    result = mr.top_n_genres(movies, popularity, 99999)
    assert isinstance(result, list), "large n should still return a list"
    passed("n larger than total genres returns all available genres")

    n = 3
    result = mr.top_n_genres(movies, popularity, n)
    assert len(result) <= n, f"result length {len(result)} exceeds n={n}"
    passed(f"top_n_genres returns at most {n} results")

    # All returned genres must exist in movies data
    known_genres = {v[1] for v in movies.values()}
    for genre_name, score in result:
        assert genre_name.lower() in known_genres, \
            f"'{genre_name}' not found in movies data"
    passed("all returned genres exist in movies data")

    # Scores should be floats in [0, 5]
    for _, score in result:
        assert isinstance(score, float), f"score should be float, got {type(score)}"
        assert 0.0 <= score <= 5.0, f"genre score {score} out of range"
    passed("all genre scores are floats in [0, 5]")

    # Results should be sorted descending by score
    scores = [score for _, score in result]
    assert scores == sorted(scores, reverse=True), \
        f"results not sorted descending: {scores}"
    passed("results sorted by score descending")

    # Tie-breaking: same score => alphabetical ascending by genre name
    for i in range(len(result) - 1):
        name_a, score_a = result[i]
        name_b, score_b = result[i + 1]
        if abs(score_a - score_b) < 1e-9:
            assert name_a.lower() <= name_b.lower(), \
                f"tie not broken alphabetically: '{name_a}' vs '{name_b}'"
    passed("ties broken alphabetically ascending")

    # Empty popularity should return empty list
    result_empty = mr.top_n_genres(movies, {}, 5)
    assert result_empty == [], \
        f"empty popularity should return [], got {result_empty}"
    passed("empty popularity returns empty list")


# ─────────────────────────────────────────────
# Test: check_cross_file_consistency
# ─────────────────────────────────────────────

def test_check_cross_file_consistency(movies, ratings):
    print("\n--- test_check_cross_file_consistency ---")

    # Should run without crashing on normal data
    try:
        mr.check_cross_file_consistency(movies, ratings)
        passed("check_cross_file_consistency runs without error on normal data")
    except Exception as e:
        failed(f"check_cross_file_consistency raised an exception: {e}")

    # Orphaned rating (in ratings but not movies) should not crash
    fake_ratings = {"orphaned_movie_xyz": [3.0]}
    try:
        mr.check_cross_file_consistency(movies, fake_ratings)
        passed("check_cross_file_consistency handles orphaned ratings gracefully")
    except Exception as e:
        failed(f"check_cross_file_consistency crashed on orphaned rating: {e}")

    # Empty inputs should not crash
    try:
        mr.check_cross_file_consistency({}, {})
        passed("check_cross_file_consistency handles empty inputs")
    except Exception as e:
        failed(f"check_cross_file_consistency crashed on empty inputs: {e}")


# ─────────────────────────────────────────────
# Test: user_preferred_genre
# ─────────────────────────────────────────────

def test_user_preferred_genre(movies, user_ratings):
    print("\n--- test_user_preferred_genre ---")

    result = mr.user_preferred_genre("nonexistent_user_xyz_999", user_ratings, movies)
    assert result is None, \
        f"nonexistent user should return None, got '{result}'"
    passed("nonexistent user returns None")

    known_genres_lower = {v[1] for v in movies.values()}

    for user_id in user_ratings:
        preferred = mr.user_preferred_genre(user_id, user_ratings, movies)
        if preferred is not None:
            assert preferred.lower() in known_genres_lower, \
                f"preferred genre '{preferred}' for user '{user_id}' not in movies"
    passed("preferred genre for all users is a known genre")

    for user_id in user_ratings:
        preferred = mr.user_preferred_genre(user_id, user_ratings, movies)
        if preferred is not None:
            assert isinstance(preferred, str), \
                f"preferred genre should be str, got {type(preferred)}"
    passed("preferred genre is a string")

    empty_user_ratings = {"ghost_user": {}}
    result = mr.user_preferred_genre("ghost_user", empty_user_ratings, movies)
    assert result is None, \
        f"user with no ratings should return None, got '{result}'"
    passed("user with empty ratings returns None")


# ─────────────────────────────────────────────
# Test: recommend_movies
# ─────────────────────────────────────────────

def test_recommend_movies(movies, ratings, user_ratings):
    print("\n--- test_recommend_movies ---")

    result = mr.recommend_movies("nonexistent_user_xyz_999", movies, ratings, user_ratings)
    assert result == [], \
        f"nonexistent user should return [], got {result}"
    passed("nonexistent user returns empty list")

    for user_id in user_ratings:
        result = mr.recommend_movies(user_id, movies, ratings, user_ratings)

        assert isinstance(result, list), \
            f"recommend_movies should return list for user '{user_id}'"

        assert len(result) <= 3, \
            f"should return at most 3 recs for user '{user_id}', got {len(result)}"

        if result:
            preferred = mr.user_preferred_genre(user_id, user_ratings, movies)
            rated_movies = set(user_ratings[user_id].keys())

            for movie_name, score in result:
                movie_key = movie_name.lower()

                assert movie_key in movies, \
                    f"rec '{movie_name}' not in movies dict"

                assert movies[movie_key][1] == preferred.lower(), \
                    f"rec '{movie_name}' not in preferred genre '{preferred}'"

                assert movie_key not in rated_movies, \
                    f"rec '{movie_name}' already rated by user '{user_id}'"

                assert isinstance(score, float), \
                    f"rec score should be float, got {type(score)}"
                assert 0.0 <= score <= 5.0, \
                    f"rec score {score} out of range"

            scores = [score for _, score in result]
            assert scores == sorted(scores, reverse=True), \
                f"recs not sorted descending for user '{user_id}'"

            for i in range(len(result) - 1):
                name_a, score_a = result[i]
                name_b, score_b = result[i + 1]
                if abs(score_a - score_b) < 1e-9:
                    assert name_a.lower() <= name_b.lower(), \
                        f"tie not broken alphabetically: '{name_a}' vs '{name_b}'"

    passed("all recommendations are valid for all users")
    passed("no recommendation already rated by user")
    passed("all recommendations are in user's preferred genre")
    passed("recommendations sorted by score descending")
    passed("recommendations at most 3")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def run_tests():
    movies, ratings, user_ratings, popularity = load_data()
    

    test_load_movies(movies)
    test_load_ratings(ratings, user_ratings)
    test_movie_popularity(ratings, popularity)
    test_top_n_movies(movies, popularity)
    test_top_n_movies_in_genre(movies, popularity)
    test_genre_popularity(movies, popularity)
    test_top_n_genres(movies, popularity)
    test_check_cross_file_consistency(movies, ratings)
    test_user_preferred_genre(movies, user_ratings)
    test_recommend_movies(movies, ratings, user_ratings)

    print("\n" + "=" * 50)
    print("All tests completed.")
    print("=" * 50)
    input("\nTests finished. Press Enter to exit...")


if __name__ == "__main__":
    run_tests()
