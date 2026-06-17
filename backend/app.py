from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from database_manager import DatabaseManager
from connection_manager import ConnectionManager

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize managers
db_manager = DatabaseManager()
conn_manager = ConnectionManager()

# Store connections in memory (use database in production)
connections = {}

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/connections', methods=['POST'])
def create_connection():
    """Create a new database connection"""
    try:
        data = request.json
        conn_id = conn_manager.create_connection(
            name=data.get('name'),
            db_type=data.get('type'),
            config=data.get('config')
        )
        connections[conn_id] = data
        return jsonify({'id': conn_id, 'message': 'Connection created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/connections', methods=['GET'])
def list_connections():
    """List all connections"""
    try:
        conns = conn_manager.list_connections()
        return jsonify(conns), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/connections/<conn_id>', methods=['DELETE'])
def delete_connection(conn_id):
    """Delete a connection"""
    try:
        conn_manager.delete_connection(conn_id)
        if conn_id in connections:
            del connections[conn_id]
        return jsonify({'message': 'Connection deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/connections/<conn_id>/test', methods=['POST'])
def test_connection(conn_id):
    """Test a connection"""
    try:
        result = conn_manager.test_connection(conn_id)
        return jsonify({'success': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a query"""
    try:
        data = request.json
        conn_id = data.get('connection_id')
        query = data.get('query')
        
        if not conn_id or not query:
            return jsonify({'error': 'Missing connection_id or query'}), 400
        
        result = db_manager.execute_query(conn_id, query)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schema/<conn_id>', methods=['GET'])
def get_schema(conn_id):
    """Get schema information for a connection"""
    try:
        schema = db_manager.get_schema(conn_id)
        return jsonify(schema), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/export', methods=['POST'])
def export_data():
    """Export query results"""
    try:
        data = request.json
        rows = data.get('rows', [])
        format_type = data.get('format', 'csv')
        filename = data.get('filename', 'export')
        
        result = db_manager.export_data(rows, format_type, filename)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
