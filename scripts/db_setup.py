import duckdb
import os

# Resolve paths from this file so script works when run from project root
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)

DB_PATH = os.path.join(_PROJECT_ROOT, "db", "olist.duckdb")
DATA_PATH = os.path.join(_PROJECT_ROOT, "data")
SQL_DIR = os.path.join(_PROJECT_ROOT, "scripts", "sql")


def get_connection():
    """Return a DuckDB connection for use by the agent pipeline. Caller should close it."""
    return duckdb.connect(DB_PATH)


def load_tables() -> None:
    tables = {
        "customers": "olist_customers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "order_payments": "olist_order_payments_dataset.csv",
        "order_reviews": "olist_order_reviews_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "product_category_name_translation": "product_category_name_translation.csv",
    }

    with duckdb.connect(DB_PATH) as conn:
        for table, file in tables.items():
            csv_path = os.path.join(DATA_PATH, file)
            print(f"Loading {table} ...")

            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM read_csv_auto('{csv_path}')"
            )
        print(f"Data loaded successfully into DuckDB")


def products_english() -> None:
    print(f"Preparing Products Table to use English Names...")
    with open(os.path.join(SQL_DIR, "product_english_name.sql")) as f:
        sql_content = f.read()

    with duckdb.connect(DB_PATH) as conn:
        conn.execute(sql_content)


def create_analytics_view() -> None:
    print("Creating Analytics View 'analytics_orders'...")
    with open(os.path.join(SQL_DIR, "analytics_orders.sql")) as f:
        sql_content = f.read()

    with duckdb.connect(DB_PATH) as conn:
        conn.execute(sql_content)


if __name__ == "__main__":
    load_tables()
    products_english()
    create_analytics_view()
