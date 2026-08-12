import json
from pathlib import Path

from agent.llm import generate_plan
from agent.tools import execute_sql


LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "iteration_trace.json"


def save_iteration_trace(trace):
    """Save the agent's iteration trace to a JSON file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_PATH, "w", encoding="utf-8") as file:
        json.dump(trace, file, indent=4)


def run_agent(question, max_retries=3, initial_sql=None):
    """
    Generate SQL, execute it, retry when SQL execution fails,
    and log every iteration.
    """

    error = None
    iteration_trace = []

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

        iteration = {
            "attempt": attempt + 1,
            "question": question,
            "sql": sql,
            "success": result["success"],
        }

        if result["success"]:
            iteration["result"] = result

            iteration_trace.append(iteration)
            save_iteration_trace(iteration_trace)

            return {
                "success": True,
                "sql": sql,
                "result": result,
                "attempts": attempt + 1,
            }

        error = result["error"]

        print(f"SQL Error: {error}")

        iteration["error"] = error
        iteration_trace.append(iteration)

        save_iteration_trace(iteration_trace)

    return {
        "success": False,
        "error": error,
        "attempts": max_retries,
    }