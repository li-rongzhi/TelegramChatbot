from datetime import datetime
import mysql.connector
from utils.utils import GENERAL, TASK_MANAGEMENT, TIMER
import os

current_directory = os.getcwd()

sql_file_name = "database/db_setup.sql"

sql_file_path = os.path.join(current_directory, sql_file_name)

class MySQLDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Connected to MySQL database")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def initialize(self):
        try:
            cursor = self.connection.cursor()
            # Read the SQL file
            with open(sql_file_path, 'r') as sql_file:
                sql_statements = sql_file.read()

            # Split the SQL file into individual statements
            statements = sql_statements.split(';')

            # Execute each SQL statement
            for statement in statements:
                if statement.strip():  # Ensure it's not an empty statement
                    cursor.execute(statement)

            self.connection.commit()

            cursor.close()

            print("SQL file executed successfully")
        except Exception as e:
            print("Error executing SQL file:", e)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database")

    def check_user_state(self, user_id: str, target: int) -> bool:
        return self.get_user_state(user_id) == target

    def get_user_state(self, user_id: str) -> int:
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT state FROM states WHERE user_id = %s", (user_id,))
            result = cursor.fetchall()
            return result[0][0]
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def initialize_user_state(self, user_id: str) -> None:
        """Initialize the user state to GENERAL

        Args:
            user_id (str): _description_
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT INTO states (user_id, state) VALUES (%s, %s) ON DUPLICATE KEY UPDATE state = %s", (user_id, GENERAL, GENERAL))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def update_user_state(self, user_id, new_state):
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE states SET state = %s WHERE user_id = %s", (new_state, user_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f'Error: {err}')
            return None
        finally:
            cursor.close()

    def add_task(self, user_id, description, duetime, remark):
        datetime_format = "%Y-%m-%d %H:%M"
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT MAX(task_id) FROM tasks WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            max_task_id = result[0] if result[0] is not None else 0
            next_task_id = max_task_id + 1
            sql_query = "INSERT INTO tasks (user_id, task_id"
            params = [user_id, next_task_id]

            # Check and append non-empty values to the SQL query and parameters
            if description:
                sql_query += ", description"
                params.append(description)
            else:
                print("No description provided")
            if duetime:
                try:
                    datetime_obj = datetime.strptime(duetime, datetime_format)
                    sql_query += ", due"
                    params.append(duetime)
                except ValueError:
                    print("Invalid datetime format for 'duetime'")
            if remark:
                sql_query += ", remark"
                params.append(remark)
            # Complete the SQL query and execute it
            sql_query += ") VALUES (" + ", ".join(["%s" for _ in params]) + ")"
            cursor.execute(sql_query, params)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def delete_task(self, user_id, task_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM tasks WHERE user_id = %s AND task_id = %s", (user_id, task_id))
            cursor.execute("UPDATE tasks SET task_id = task_id - 1 WHERE user_id = %s AND task_id > %s", (user_id, task_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

    def mark_task(self, user_id, task_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE tasks SET isDone = 1 WHERE user_id = %s AND task_id = %s", (user_id, task_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f'Error: {err}')
            return None
        finally:
            cursor.close()

    def list_tasks(self, user_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT task_id, description, isDone, remark, due FROM tasks WHERE user_id = %s", (user_id,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            cursor.close()

