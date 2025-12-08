from airflow.decorators import dag, task
from airflow.utils.task_group import TaskGroup
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from airflow.models import Variable
import json


@dag(
    dag_id="shopverse_daily_pipeline",
    description="ShopVerse ETL Pipeline using fixed filenames (no date-based filenames)",
    schedule="0 1 * * *",   # Run daily at 1 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args={
        "owner": "Vivek",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["etl", "shopverse", "pipeline"],
)
def shopverse_daily_pipeline():

    base_path = Variable.get("shopverse_data_base_path")  # base folder path
    min_orders = int(Variable.get("shopverse_min_order_threshold", 10))

    # ----------------------------------------------------
    # 1. FILE SENSORS (wait for fixed filenames)
    # ----------------------------------------------------
    customers_file = FileSensor(
        task_id="wait_customers",
        fs_conn_id="fs_default",
        filepath=f"{base_path}/landing/customers/customers.csv",
        poke_interval=30,
        timeout=1800,
    )

    products_file = FileSensor(
        task_id="wait_products",
        fs_conn_id="fs_default",
        filepath=f"{base_path}/landing/products/products.csv",
        poke_interval=30,
        timeout=1800,
    )

    orders_file = FileSensor(
        task_id="wait_orders",
        fs_conn_id="fs_default",
        filepath=f"{base_path}/landing/orders/orders.json",
        poke_interval=30,
        timeout=1800,
    )

    # ----------------------------------------------------
    # 2. STAGING (truncate + load)
    # ----------------------------------------------------
    with TaskGroup("staging") as staging:

        @task
        def load_customers():
            hook = PostgresHook("postgres_dwh")
            file = f"{base_path}/landing/customers/customers.csv"

            hook.run("TRUNCATE TABLE stg_customers;")
            hook.copy_expert(
                sql="COPY stg_customers FROM STDIN WITH CSV HEADER;",
                filename=file,
            )

        @task
        def load_products():
            hook = PostgresHook("postgres_dwh")
            file = f"{base_path}/landing/products/products.csv"

            hook.run("TRUNCATE TABLE stg_products;")
            hook.copy_expert(
                sql="COPY stg_products FROM STDIN WITH CSV HEADER;",
                filename=file,
            )

        @task
        def load_orders():
            hook = PostgresHook("postgres_dwh")
            file = f"{base_path}/landing/orders/orders.json"

            hook.run("TRUNCATE TABLE stg_orders;")

            with open(file) as f:
                rows = json.load(f)

            for row in rows:
                hook.run(
                    """
                    INSERT INTO stg_orders (
                        order_id, order_timestamp,
                        customer_id, product_id,
                        quantity, total_amount,
                        currency, status
                    )
                    VALUES (
                        %(order_id)s,
                        %(order_timestamp)s,
                        %(customer_id)s,
                        %(product_id)s,
                        %(quantity)s,
                        %(total_amount)s,
                        %(currency)s,
                        %(status)s
                    );
                    """,
                    parameters=row,
                )

        load_customers() >> load_products() >> load_orders()

    # ----------------------------------------------------
    # 3. WAREHOUSE PROCESSING
    # ----------------------------------------------------
    with TaskGroup("warehouse") as warehouse:

        @task
        def dim_customers():
            hook = PostgresHook("postgres_dwh")
            hook.run("""
                INSERT INTO dim_customers
                SELECT DISTINCT *
                FROM stg_customers
                ON CONFLICT (customer_id) DO NOTHING;
            """)

        @task
        def dim_products():
            hook = PostgresHook("postgres_dwh")
            hook.run("""
                INSERT INTO dim_products
                SELECT DISTINCT *
                FROM stg_products
                ON CONFLICT (product_id) DO NOTHING;
            """)

        @task
        def fact_orders():
            hook = PostgresHook("postgres_dwh")

            # Prevent duplicate primary key errors
            hook.run("""
                DELETE FROM fact_orders
                WHERE order_id IN (SELECT order_id FROM stg_orders);
            """)

            hook.run("""
                INSERT INTO fact_orders (
                    order_id, order_timestamp, customer_id, product_id,
                    quantity, total_amount, currency_mismatch_flag
                )
                SELECT
                    order_id,
                    order_timestamp AT TIME ZONE 'UTC',
                    customer_id,
                    product_id,
                    quantity,
                    total_amount,
                    (currency <> 'USD') AS currency_mismatch_flag
                FROM stg_orders
                WHERE quantity > 0
                AND customer_id IS NOT NULL
                AND product_id IS NOT NULL;
            """)

        d1 = dim_customers()
        d2 = dim_products()
        f = fact_orders()

        d1 >> d2 >> f

    # ----------------------------------------------------
    # 4. DATA QUALITY CHECKS
    # ----------------------------------------------------
    @task
    def dq_checks():
        hook = PostgresHook("postgres_dwh")

        dim_count = hook.get_first("SELECT COUNT(*) FROM dim_customers;")[0]
        if dim_count == 0:
            raise Exception("DQ FAILED: dim_customers is empty")

        fact_count = hook.get_first("SELECT COUNT(*) FROM fact_orders;")[0]
        if fact_count == 0:
            raise Exception("DQ FAILED: fact_orders is empty")

        return fact_count

    # ----------------------------------------------------
    # 5. BRANCHING (EmptyOperators instead of Email)
    # ----------------------------------------------------
    @task.branch
    def branch(fact_count, min_orders=min_orders):
        return "warn_low_volume" if fact_count < min_orders else "normal_completion"

    warn_low_volume = EmptyOperator(task_id="warn_low_volume")
    normal_completion = EmptyOperator(task_id="normal_completion")

    end = EmptyOperator(task_id="end")

    # ----------------------------------------------------
    # 6. FULL PIPELINE FLOW
    # ----------------------------------------------------
    [customers_file, products_file, orders_file] >> staging >> warehouse

    fc = dq_checks()
    branch(fc) >> [warn_low_volume, normal_completion] >> end


pipeline = shopverse_daily_pipeline()