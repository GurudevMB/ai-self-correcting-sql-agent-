import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "database" / "agent.db"
SEED_PATH = Path(__file__).resolve().parent.parent / "database" / "seed.sql"


def initialize_database():
    """Create the sample SQLite database using seed.sql."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        with open(SEED_PATH, "r", encoding="utf-8") as file:
            seed_sql = file.read()

        connection.executescript(seed_sql)
        connection.commit()

    finally:
        connection.close()


def inspect_database():
    """Return the available tables and their columns."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%'
            """
        )

        tables = cursor.fetchall()

        schema = {}

        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            schema[table_name] = [
                {
                    "name": column[1],
                    "type": column[2],
                }
                for column in columns
            ]

        return schema

    finally:
        connection.close()


def execute_sql(query: str):
    """Execute a SQL query and return rows or an error."""

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()
        cursor.execute(query)

        if cursor.description:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }

        connection.commit()

        return {
            "success": True,
            "columns": [],
            "rows": [],
            "row_count": 0,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        connection.close()