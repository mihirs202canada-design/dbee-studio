import psycopg2
import mysql.connector
import sqlite3
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

class DatabaseDriver:
    """Handle connections to different database types"""
    
    def connect(self, db_type, config):
        """Create a database connection based on type"""
        if db_type == 'postgresql':
            return self._connect_postgresql(config)
        elif db_type == 'mysql':
            return self._connect_mysql(config)
        elif db_type == 'sqlite':
            return self._connect_sqlite(config)
        elif db_type == 'mongodb':
            return self._connect_mongodb(config)
        else:
            raise ValueError(f'Unsupported database type: {db_type}')
    
    def _connect_postgresql(self, config):
        """Connect to PostgreSQL"""
        return psycopg2.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            user=config.get('user'),
            password=config.get('password'),
            database=config.get('database')
        )
    
    def _connect_mysql(self, config):
        """Connect to MySQL"""
        return mysql.connector.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            user=config.get('user'),
            password=config.get('password'),
            database=config.get('database')
        )
    
    def _connect_sqlite(self, config):
        """Connect to SQLite"""
        db_path = config.get('path', ':memory:')
        return sqlite3.connect(db_path)
    
    def _connect_mongodb(self, config):
        """Connect to MongoDB"""
        uri = config.get('uri', 'mongodb://localhost:27017')
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        try:
            client.server_info()
            return client
        except ServerSelectionTimeoutError:
            raise Exception('Cannot connect to MongoDB')
    
    def execute_query(self, connection, query, db_type):
        """Execute a query on the connection"""
        if db_type == 'mongodb':
            return self._execute_mongo_query(connection, query)
        else:
            return self._execute_sql_query(connection, query, db_type)
    
    def _execute_sql_query(self, connection, query, db_type):
        """Execute SQL query"""
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                return {
                    'success': True,
                    'columns': columns,
                    'rows': [dict(zip(columns, row)) for row in rows],
                    'count': len(rows)
                }
            else:
                # INSERT, UPDATE, DELETE queries
                connection.commit()
                return {
                    'success': True,
                    'message': f'Query executed. Rows affected: {cursor.rowcount}',
                    'rowcount': cursor.rowcount
                }
        except Exception as e:
            connection.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            cursor.close()
    
    def _execute_mongo_query(self, client, query):
        """Execute MongoDB query"""
        try:
            # Parse and execute MongoDB command
            parts = query.split('.')
            db_name = parts[0] if len(parts) > 0 else 'test'
            
            db = client[db_name]
            # This is a simplified version; implement full MongoDB query parsing as needed
            return {
                'success': True,
                'message': 'MongoDB query support coming soon',
                'rows': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
