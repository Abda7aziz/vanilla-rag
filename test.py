import os
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes

def connect_with_connector():
    instance_connection_name = "visionai-446410:me-central2:exproai-dev-db"
    db_user = "rag"
    db_pass = 'PfGM@^L"z+nnyuRx'
    db_name = "expro_ai_dev_db"

    connector = Connector()

    def getconn():
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name
        )
        return conn

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool

# Example usage
db_pool = connect_with_connector()
with db_pool.connect() as conn:
    result = conn.execute(sqlalchemy.text("SELECT 1")).fetchall()
    print(f"Connection successful. Result: {result}")
