from utils.imports import pyodbc, pd
from contextlib import contextmanager
from core.config import Config
from core.logger import logger
import time

class HospitalStitch:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.conn_str = Config.CONNECTION_STRING
        self._schema_cache = None

    def test_connection(self):
        """Verifies if SQL Server is reachable without throwing a crash-level exception."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Health Check Failed: {e}")
            return False

    def _load_schema_cache(self):
        """Introspects the DB to prevent 'Invalid Column' errors."""
        if self._schema_cache is not None:
            return
        try:
            query = "SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS"
            with self.connect() as conn:
                df = pd.read_sql(query, conn)
                self._schema_cache = df.groupby('TABLE_NAME')['COLUMN_NAME'].apply(list).to_dict()
                logger.info("SQL Safe Mode: Schema indexed successfully.")
        except Exception as e:
            logger.error(f"SQL Safe Mode failed to index schema: {e}")
            self._schema_cache = {}

    def validate_query(self, query):
        """Optional: Could be used to lint queries against the cache."""
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

    @contextmanager
    def connect(self):
        conn = None
        for attempt in range(self.max_retries):
            try:
                conn = pyodbc.connect(self.conn_str, timeout=30)
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
                try: conn.close()
                except: pass

    # --- CQRS READ ---
    def fetch(self, query, params=None):
        self._load_schema_cache() # Lazy load
        params = self.safe_params(params)
        with self.connect() as conn:
            p = params if params and len(params) > 0 else None
            return pd.read_sql(query, conn, params=p)

    def fetch_scalar(self, query, params=None):
        self._load_schema_cache()
        params = self.safe_params(params)
        with self.connect() as conn:
            cursor = conn.cursor()
            if params and len(params) > 0:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return row[0] if row else None

    # --- CQRS WRITE ---
    def execute(self, query, params=None):
        self._load_schema_cache()
        params = self.safe_params(params)
        with self.connect() as conn:
            cursor = conn.cursor()
            if params and len(params) > 0:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            
    def execute_transaction(self, queries_and_params):
        self._load_schema_cache()
        with self.connect() as conn:
            cursor = conn.cursor()
            try:
                for q, p in queries_and_params:
                    p = self.safe_params(p)
                    if p and len(p) > 0:
                        cursor.execute(q, p)
                    else:
                        cursor.execute(q)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
                
db = HospitalStitch()
