import psycopg2


class PostgreSQLManager:
    """A class to manage a PostgreSQL database."""
    def __init__(self, dbname, user, password, host, port):
        """Initializes the database connection.

        Args:
            dbname (str): The name of the database.
            user (str): The username to connect to the database.
            password (str): The password to connect to the database.
            host (str): The host address of the database server.
            port (str): The port number of the database server.
        """

        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()

    def create_table(self, table_name):
        """Creates a table in the database.

        Args:
            table_name: The name of the table to create.
        """
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            name TEXT,
            label TEXT[],
            vector FLOAT[],
            image TEXT
        )
        """
        self.cur.execute(create_table_query)
        self.conn.commit()

    def insert_data(self, table_name, data):
        """Inserts data into a table in the database.

        Args:
            table_name: The name of the table to insert data into.
            data: The data to insert into the table.
        """
        insert_data_query = f"""
        INSERT INTO {table_name} (name, label, vector, image)
        VALUES (%s, %s, %s, %s)
        """
        self.cur.execute(insert_data_query, data)
        self.conn.commit()

    def delete_data(self, table_name, id):
        """Deletes data from a table in the database.

        Args:
            table_name: The name of the table to delete data from.
            id: The ID of the row to delete.
        """
        delete_data_query = f"""
        DELETE FROM {table_name} WHERE id = %s
        """
        self.cur.execute(delete_data_query, (id,))
        self.conn.commit()

    def drop_table(self, table_name):
        """Drops a table from the database.

        Args:
            table_name (str): The name of the table to drop.
        """
        drop_table_query = f"""
        DROP TABLE IF EXISTS {table_name}
        """
        self.cur.execute(drop_table_query)
        self.conn.commit()

    def close_connection(self):
        """Closes the database connection."""
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    db = PostgreSQLManager(
            dbname="thanhbd",
            user="postgres",
            password="1",
            host="localhost",
            port="5432"
            )

    db.drop_table('data')
    db.create_table('data')
