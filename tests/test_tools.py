from agent.tools import initialize_database, inspect_database, execute_sql


def test_initialize_database():
    initialize_database()

    schema = inspect_database()

    assert "employees" in schema


def test_inspect_database():
    initialize_database()

    schema = inspect_database()

    assert "employees" in schema

    columns = [column["name"] for column in schema["employees"]]

    assert "id" in columns
    assert "name" in columns
    assert "department" in columns
    assert "salary" in columns


def test_execute_sql_success():
    initialize_database()

    result = execute_sql(
        "SELECT name, salary FROM employees WHERE salary > 60000;"
    )

    assert result["success"] is True
    assert result["row_count"] == 2


def test_execute_sql_error():
    initialize_database()

    result = execute_sql(
        "SELECT name, score FROM employees;"
    )

    assert result["success"] is False
    assert "no such column" in result["error"]