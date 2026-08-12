-- UC3 Sample Database
-- Self-Correcting SQL Agent

DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary INTEGER NOT NULL
);

INSERT INTO employees (id, name, department, salary) VALUES
(1, 'Arun', 'Engineering', 60000),
(2, 'Priya', 'Engineering', 65000),
(3, 'Karthik', 'Marketing', 50000),
(4, 'Divya', 'HR', 45000),
(5, 'Rahul', 'Engineering', 70000);