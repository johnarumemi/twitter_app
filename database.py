# Class to interact with database and retrieve data
from psycopg2 import pool
import os
HOST = "localhost"
USER = "postgres"
PASSWD = os.getenv("PGUSER_PASSWD")
DB = "learning"


class Database:
    __connection_pool = None

    @classmethod
    def initialise(cls, **kwargs):
        kwargs.setdefault("database", DB)
        kwargs.setdefault("user", USER)
        kwargs.setdefault("password", PASSWD)
        kwargs.setdefault("host", HOST)
        kwargs.setdefault("sslmode", "disable")
        kwargs.setdefault("gssencmode", "disable")
        cls.__connection_pool = pool.SimpleConnectionPool(1, 10, **kwargs)


    @classmethod
    def connected(cls):
            return False if cls.__connection_pool is None else True

    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        # Stops all commits from going through and closes them all
        cls.__connection_pool.closeall()


class ConnectionFromPool(object):

    def __init__(self):
        self.connection = None

    def __enter__(self):
        # called on entry into a with context
        if not Database.connected():
            Database.initialise()
        self.connection = Database.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Called on exit from with context
        # We now also need to do the things a connection object did when entering a with statement
        # in this case, commit changes
        self.connection.commit()
        Database.return_connection(self.connection)


class CursorFromConnectionFromPool(object):

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        # called on entry into a with context
        if not Database.connected():
            Database.initialise()
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """

        :param exc_type:    Exception_type
        :param exc_val:     Exception Value
        :param exc_tb:      Exception_traceback
        If an error happens within a with clause the above info is provided
        :return:
        """
        if exc_val is not None:
            # if an error occurs then rollback the connection
            self.connection.rollback()  # e.g. TypeError, AttributeError, ValueError
        else:
            # Called on exit from with context
            # We now also need to do the things a connection object did when entering a with statement
            # in this case, commit changes
            self.cursor.close()
            self.connection.commit()

        Database.return_connection(self.connection)
