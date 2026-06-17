import uuid
import json
from datetime import datetime
from database_driver import DatabaseDriver

class ConnectionManager:
    def __init__(self):
        self.connections = {}
        self.driver = DatabaseDriver()
    
    def create_connection(self, name, db_type, config):
        """Create a new connection"""
        conn_id = str(uuid.uuid4())
        
        connection = {
            'id': conn_id,
            'name': name,
            'type': db_type,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'status': 'disconnected'
        }
        
        self.connections[conn_id] = connection
        return conn_id
    
    def list_connections(self):
        """List all connections"""
        return list(self.connections.values())
    
    def get_connection(self, conn_id):
        """Get connection details"""
        return self.connections.get(conn_id)
    
    def delete_connection(self, conn_id):
        """Delete a connection"""
        if conn_id in self.connections:
            del self.connections[conn_id]
            return True
        return False
    
    def test_connection(self, conn_id):
        """Test if a connection works"""
        connection = self.get_connection(conn_id)
        if not connection:
            raise Exception('Connection not found')
        
        try:
            conn = self.driver.connect(
                connection['type'],
                connection['config']
            )
            conn.close()
            self.connections[conn_id]['status'] = 'connected'
            return True
        except Exception as e:
            self.connections[conn_id]['status'] = 'error'
            raise e
    
    def update_connection(self, conn_id, updates):
        """Update connection details"""
        if conn_id in self.connections:
            self.connections[conn_id].update(updates)
            return True
        return False
