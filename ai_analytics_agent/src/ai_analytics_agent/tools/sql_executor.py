import duckdb
from pandas import DataFrame
import os
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[4] / "db" / "olist.duckdb"


def execute_query(query: str) -> DataFrame:
    query = (
        query.strip()
        .removeprefix("```sql")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    conn = duckdb.connect(database=DB_PATH)
    df = conn.execute(query).df()
    conn.close()
    return df
