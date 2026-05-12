import pyodbc
from core.config import Config
from core.logger import logger
import time
from contextlib import contextmanager
import pandas as pd

class ConnectionPoolManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    @contextmanager
    def get_connection(self):
        conn = None
        for attempt in range(self.max_retries):
            try:
                conn = pyodbc.connect(Config.CONNECTION_STRING, timeout=5)
                break
            except pyodbc.Error as e:
                logger.warning(f"Connection attempt {attempt+1} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error("Database connection failed permanently.")
                    raise e
                time.sleep(1)
        
        try:
            yield conn
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def safe_params(self, params):
        if not params:
            return params
        cleaned = []
        for p in params:
            if hasattr(p, "item"):
                cleaned.append(p.item())
            else:
                cleaned.append(p)
        return tuple(cleaned)

    def fetch_df(self, query, params=()):
        with self.get_connection() as conn:
            return pd.read_sql(query, conn, params=self.safe_params(params))

    def execute_transaction(self, queries_and_params):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                for query, params in queries_and_params:
                    cursor.execute(query, self.safe_params(params))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
                raise e

    def execute_scalar(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, self.safe_params(params))
            result = cursor.fetchone()
            return result[0] if result else None

db = ConnectionPoolManager()
