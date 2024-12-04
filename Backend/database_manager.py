import mysql.connector

class databaseManager:
    def __init__(self):
        self.connection = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                database='flight_sim',
                user='root',
                password='root',
                charset='utf8mb4',
                collation='utf8mb4_general_ci',
                autocommit=True
        )
        self.cursor = self.connection.cursor(buffered=True)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor
        except Exception as e:
            self.connection.rollback()
            raise e

    def fetch_one(self, query, params=None):
        self.execute_query(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        self.execute_query(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()

