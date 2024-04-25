import json
from os import getenv
import app.queries as queries
from app.db_executor import DBExecutor
from app.constants import (
    TableFields as Tf,
    Environment as Env
)


class AppService:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = DBExecutor(getenv(Env.Value.host), getenv(Env.Value.database), getenv(Env.Value.user),
                                     getenv(Env.Value.password)).connection
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def get_all_genres(self):
        with self:
            result = DBExecutor.execute_read_query(self.connection, queries.table_columns)
            index = next((index for index, d in enumerate(result) if d.get(Tf.field) == Tf.genres), None)
            set_str = result[index][Tf.type].replace("set(", "").replace(")", "").replace("'", "")
            return sorted(set(set_str.split(",")))

    def get_all_production_years(self):
        with self:
            result = DBExecutor.execute_read_query(self.connection, queries.all_production_years)
            return [str(i[Tf.year]) for i in result]

    def get_films_by_year(self, year, amount, current_page):
        with self:
            return DBExecutor.execute_read_query(self.connection,
                                                 queries.search_films_by_year(year, amount, current_page))

    def get_films_by_actors(self, actors, amount, current_page):
        with self:
            return DBExecutor.execute_read_query(self.connection,
                                                 queries.search_films_by_actors(actors, amount, current_page))

    def get_films_by_keywords(self, keywords, amount, current_page):
        with self:
            return DBExecutor.execute_read_query(self.connection,
                                                 queries.search_films_by_keywords(keywords, amount, current_page))

    def get_films_by_name(self, name, amount, current_page):
        with self:
            return DBExecutor.execute_read_query(self.connection,
                                                 queries.search_films_by_name(name, amount, current_page))

    def get_films_by_genres(self, genres, amount, current_page):
        with self:
            return DBExecutor.execute_read_query(self.connection,
                                                 queries.search_films_by_genres(genres, amount, current_page))

    def get_films_by_year_n_genres(self, year, genres, amount, current_page):
        with self:
            return DBExecutor.execute_read_query(self.connection,
                                                 queries.search_films_by_year_and_genres(year, genres, amount,
                                                                                         current_page))

    def get_film_by_id(self, film_id):
        with self:
            data = DBExecutor.execute_read_query(self.connection, queries.search_film_by_id(film_id))[0]
            cast = json.loads(data[Tf.cast])
            data[Tf.cast] = cast
            directors = json.loads(data[Tf.directors])
            data[Tf.directors] = directors
            languages = json.loads(data[Tf.languages])
            data[Tf.languages] = languages
            return data

    def save_query(self, query, user_id):
        with self:
            DBExecutor.execute_write_query(self.connection, queries.write_query_to_db(query, user_id))

    def show_most_common_queries(self):
        with self:
            return DBExecutor.execute_read_query(self.connection, queries.most_common_queries)
