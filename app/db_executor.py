import mysql.connector
import logging
from app.constants import (
    Environment as Env,
    Messages as Msg
)

logger = logging.getLogger(__name__)


class DBExecutor:
    def __init__(self, host, database, user, password):
        self.__host = host
        self.__database = database
        self.__user = user
        self.__password = password
        self.connection = self.__create_connection()

    def __create_connection(self):
        db_config = {Env.Key.host: self.__host,
                     Env.Key.user: self.__user,
                     Env.Key.password: self.__password,
                     Env.Key.database: self.__database}

        connection = None
        try:
            connection = mysql.connector.connect(**db_config)
        except mysql.connector.Error as e:
            logger.warning(Msg.mysql_err.format(e))

        return connection

    @staticmethod
    def execute_read_query(connection, query):
        cursor = connection.cursor(dictionary=True)
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except mysql.connector.Error as e:
            logger.warning(Msg.mysql_err.format(e))
        finally:
            cursor.close()
        return result

    @staticmethod
    def execute_write_query(connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
        except mysql.connector.Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
