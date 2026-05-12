from data.connection import db

class SchemaIntrospector:
    _schema_cache = None

    @classmethod
    def get_table_schema(cls, table_name):
        if cls._schema_cache is None:
            cls.load_schema()
        return cls._schema_cache.get(table_name, [])

    @classmethod
    def load_schema(cls):
        query = """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME != 'sysdiagrams'
        """
        try:
            df = db.fetch_df(query)
            schema = {}
            for _, row in df.iterrows():
                t_name = row['TABLE_NAME']
                if t_name not in schema:
                    schema[t_name] = []
                schema[t_name].append({
                    'column': row['COLUMN_NAME'],
                    'type': row['DATA_TYPE'],
                    'max_len': row['CHARACTER_MAXIMUM_LENGTH']
                })
            cls._schema_cache = schema
        except Exception as e:
            print('Schema load error:', e)
            cls._schema_cache = {}

schema_manager = SchemaIntrospector()
