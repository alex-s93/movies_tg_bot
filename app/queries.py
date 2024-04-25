all_production_years = "SELECT DISTINCT year FROM movies ORDER BY year"

table_columns = "SHOW COLUMNS FROM movies"

most_common_queries = """
SELECT query, COUNT(query) AS query_count
FROM history
GROUP BY query
ORDER BY query_count DESC
LIMIT 10"""


def write_query_to_db(query, user_id):
    return f"INSERT INTO history (query, user_id) values ('{query}', {user_id});"


def search_films_by_keywords(film_keywords, amount, current_page):
    title_param = []
    plot_param = []
    for word in set(film_keywords.split(" ")):
        title_param.append(f"(title LIKE '% {word} %' OR title LIKE '{word} %' OR title LIKE '% {word}')")
        plot_param.append(f"(plot LIKE '% {word} %' OR plot LIKE '{word} %' OR plot LIKE '% {word}')")

    query = f"""
    SELECT
        id, title, plot, poster, `imdb.rating` AS rating
    FROM movies
    where ({' AND '.join(title_param)}) or ({' AND '.join(plot_param)})
    ORDER BY rating DESC 
    LIMIT {amount}
    """
    return __add_offset(query, current_page, amount)


def search_films_by_name(name, amount, current_page):
    query = f"""
    SELECT
        id, title, plot, poster, `imdb.rating` AS rating
    FROM movies
    where title LIKE '%{name}%'
    ORDER BY rating DESC 
    LIMIT {amount}
    """
    return __add_offset(query, current_page, amount)


def search_films_by_year_and_genres(year, genres, amount, current_page):
    query = f"""
    SELECT
        id, title, plot, poster, `imdb.rating` AS rating
    FROM movies
    WHERE year = {year}
    """
    for genre in genres:
        query += f" AND FIND_IN_SET('{genre}', genres) > 0"

    query += " ORDER BY rating DESC"
    query += f" LIMIT {amount}"
    return __add_offset(query, current_page, amount)


def search_films_by_genres(genres, amount, current_page):
    query = f"""
    SELECT
        id, title, plot, poster, `imdb.rating` AS rating
    FROM movies
    """
    for index, genre in enumerate(genres):
        help_word = ' WHERE' if index == 0 else ' AND'
        query += f" {help_word} FIND_IN_SET('{genre}', genres) > 0"
    query += " ORDER BY rating DESC"
    query += f" LIMIT {amount}"
    return __add_offset(query, current_page, amount)


def search_films_by_year(year, amount, current_page):
    query = f"""
    SELECT
        id, title, plot, poster, `imdb.rating` AS rating
    FROM movies
    WHERE year = {year}
    ORDER BY rating DESC
    LIMIT {amount}
    """
    return __add_offset(query, current_page, amount)


def search_films_by_actors(actors, amount, current_page):
    query = """
    SELECT
        id, title, plot, poster, `imdb.rating` AS rating
    FROM movies
    """
    for index, actor in enumerate(actors):
        help_word = ' WHERE' if index == 0 else ' OR'
        query += f" {help_word} JSON_CONTAINS(cast, '\"{actor.strip()}\"')"
    query += " ORDER BY rating DESC"
    query += f" LIMIT {amount}"
    return __add_offset(query, current_page, amount)


def search_film_by_id(film_id):
    query = f"""
    SELECT
        title, plot, genres, runtime, cast,
        poster, languages, directors, year, type,
        `imdb.rating` AS rating,
        `awards.text` AS awards
    FROM movies
    WHERE id = {film_id}
    """
    return query


def __add_offset(query, current_page, amount):
    if current_page > 1:
        query += f" OFFSET {(current_page - 1) * amount}"
    return query
