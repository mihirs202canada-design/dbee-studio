import csv
import json
from io import StringIO
from database_driver import DatabaseDriver
from connection_manager import ConnectionManager

class DatabaseManager:
    """Manage database operations"""
    
    def __init__(self):
        self.driver = DatabaseDriver()
        self.conn_manager = ConnectionManager()
        self.connections_cache = {}
    
    def execute_query(self, conn_id, query):
        """Execute a query on a connection"""
        connection_config = self.conn_manager.get_connection(conn_id)
        
        if not connection_config:
            return {
                'success': False,
                'error': 'Connection not found'
            }
        
        try:
            # Get or create connection
            connection = self.driver.connect(
                connection_config['type'],
                connection_config['config']
            )
            
            result = self.driver.execute_query(
                connection,
                query,
                connection_config['type']
            )
            
            if connection_config['type'] != 'mongodb':
                connection.close()
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_schema(self, conn_id):
        """Get schema information for a connection"""
        connection_config = self.conn_manager.get_connection(conn_id)
        
        if not connection_config:
            return {'error': 'Connection not found'}
        
        try:
            connection = self.driver.connect(
                connection_config['type'],
                connection_config['config']
            )
            
            db_type = connection_config['type']
            
            if db_type == 'postgresql':
                schema = self._get_postgresql_schema(connection)
            elif db_type == 'mysql':
                schema = self._get_mysql_schema(connection)
            elif db_type == 'sqlite':
                schema = self._get_sqlite_schema(connection)
            elif db_type == 'mongodb':
                schema = self._get_mongodb_schema(connection)
            else:
                schema = {}
            
            connection.close()
            return schema
        except Exception as e:
            return {'error': str(e)}
    
    def _get_postgresql_schema(self, connection):
        """Get PostgreSQL schema"""
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type FROM information_schema.columns 
                WHERE table_name = '{table}'
            """)
            columns = [{'name': row[0], 'type': row[1]} for row in cursor.fetchall()]
            schema[table] = columns
        
        cursor.close()
        return schema
    
    def _get_mysql_schema(self, connection):
        """Get MySQL schema"""
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = [{'name': row[0], 'type': row[1]} for row in cursor.fetchall()]
            schema[table] = columns
        
        cursor.close()
        return schema
    
    def _get_sqlite_schema(self, connection):
        """Get SQLite schema"""
        cursor = connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
            schema[table] = columns
        
        cursor.close()
        return schema
    
    def _get_mongodb_schema(self, client):
        """Get MongoDB schema"""
        schema = {}
        try:
            for db_name in client.list_database_names():
                if db_name not in ['admin', 'config', 'local']:
                    db = client[db_name]
                    schema[db_name] = db.list_collection_names()
        except:
            pass
        return schema
    
    def export_data(self, rows, format_type, filename):
        """Export data to different formats"""
        try:
            if format_type == 'csv':
                return self._export_csv(rows, filename)
            elif format_type == 'json':
                return self._export_json(rows, filename)
            else:
                return {'error': 'Unsupported format'}
        except Exception as e:
            return {'error': str(e)}
    
    def _export_csv(self, rows, filename):
        """Export as CSV"""
        if not rows:
            return {'error': 'No data to export'}
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        
        return {
            'success': True,
            'data': output.getvalue(),
            'filename': f'{filename}.csv'
        }
    
    def _export_json(self, rows, filename):
        """Export as JSON"""
        return {
            'success': True,
            'data': json.dumps(rows, indent=2, default=str),
            'filename': f'{filename}.json'
        }
