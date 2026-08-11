from agent.llm import generate_plan
from agent.tools import execute_sql


def run_agent(question, max_retries=3, initial_sql=None):
    """
    Generate SQL, execute it, and retry when SQL execution fails.
    """

    error = None

    for attempt in range(max_retries):

        if attempt == 0 and initial_sql:
            sql = initial_sql

        elif error:
            prompt = f"""
The previous SQL query failed.

User question:
{question}

Previous SQL error:
{error}

Generate a corrected SQLite SQL query.
Return ONLY the SQL query.
"""
            sql = generate_plan(prompt)

        else:
            prompt = f"""
Convert the following user question into a SQLite SQL query.

User question:
{question}

Return ONLY the SQL query.
"""
            sql = generate_plan(prompt)

        print(f"Attempt {attempt + 1}: {sql}")

        result = execute_sql(sql)

        if result["success"]:
            return {
                "success": True,
                "sql": sql,
                "result": result,
                "attempts": attempt + 1
            }

        print(f"SQL Error: {result['error']}")

        error = result["error"]

    return {
        "success": False,
        "error": error,
        "attempts": max_retries
    }