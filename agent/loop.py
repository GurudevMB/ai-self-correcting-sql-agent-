import json
from pathlib import Path

from agent.llm import generate_plan
from agent.tools import execute_sql, inspect_database


LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "iteration_trace.json"


def save_iteration_trace(trace):
    """Save the complete agent iteration trace to a JSON file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_PATH, "w", encoding="utf-8") as file:
        json.dump(trace, file, indent=4)


def run_agent(question, max_retries=3, initial_sql=None):
    """
    Run the Perceive -> Plan -> Act -> Observe agent loop.

    The agent:
    1. Perceives the question and database schema.
    2. Plans SQL using Gemini.
    3. Acts by executing the SQL.
    4. Observes the execution result.
    5. Retries with corrected SQL when execution fails.
    """

    error = None
    iteration_trace = []

    for attempt in range(max_retries):

        # ---------------------------------------------------------
        # PERCEIVE
        # ---------------------------------------------------------
        schema = inspect_database()

        print(f"Attempt {attempt + 1} - PERCEIVE")
        print(f"Database schema: {schema}")

        # ---------------------------------------------------------
        # PLAN
        # ---------------------------------------------------------
        if attempt == 0 and initial_sql:
            sql = initial_sql

        elif error:
            prompt = f"""
The previous SQL query failed.

Database schema:
{schema}

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

Database schema:
{schema}

User question:
{question}

Return ONLY the SQL query.
"""
            sql = generate_plan(prompt)

        print(f"Attempt {attempt + 1} - PLAN")
        print(f"Generated SQL: {sql}")

        # ---------------------------------------------------------
        # ACT
        # ---------------------------------------------------------
        print(f"Attempt {attempt + 1} - ACT")
        print("Tool: execute_sql")

        result = execute_sql(sql)

        # ---------------------------------------------------------
        # OBSERVE
        # ---------------------------------------------------------
        print(f"Attempt {attempt + 1} - OBSERVE")

        if result["success"]:
            print("Observation: SQL execution successful")

            iteration = {
                "iteration": attempt + 1,
                "perceive": {
                    "question": question,
                    "schema": schema
                },
                "plan": {
                    "sql": sql
                },
                "act": {
                    "tool": "execute_sql",
                    "action": "Execute generated SQL"
                },
                "observe": {
                    "success": True,
                    "result": result
                }
            }

            iteration_trace.append(iteration)
            save_iteration_trace(iteration_trace)

            return {
                "success": True,
                "sql": sql,
                "result": result,
                "attempts": attempt + 1
            }

        error = result["error"]

        print(f"Observation: SQL execution failed")
        print(f"SQL Error: {error}")

        iteration = {
            "iteration": attempt + 1,
            "perceive": {
                "question": question,
                "schema": schema
            },
            "plan": {
                "sql": sql
            },
            "act": {
                "tool": "execute_sql",
                "action": "Execute generated SQL"
            },
            "observe": {
                "success": False,
                "error": error
            }
        }

        iteration_trace.append(iteration)
        save_iteration_trace(iteration_trace)

    return {
        "success": False,
        "error": error,
        "attempts": max_retries
    }