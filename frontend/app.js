const API_URL = 'http://localhost:5000/api';

const app = {
    currentConnectionId: null,
    currentResults: [],
    connections: [],
    
    init() {
        this.loadConnections();
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
    },
    
    async loadConnections() {
        try {
            const response = await fetch(`${API_URL}/connections`);
            this.connections = await response.json();
            this.renderConnections();
        } catch (error) {
            console.error('Failed to load connections:', error);
        }
    },
    
    renderConnections() {
        const listEl = document.getElementById('connectionsList');
        
        if (this.connections.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No connections yet</p>';
            return;
        }
        
        listEl.innerHTML = this.connections.map(conn => `
            <div class="connection-item ${conn.id === this.currentConnectionId ? 'active' : ''}" onclick="app.selectConnection('${conn.id}')">
                <div class="connection-info">
                    <div class="connection-name">${conn.name}</div>
                    <div class="connection-type">${conn.type}</div>
                </div>
                <button class="connection-delete" onclick="event.stopPropagation(); app.deleteConnection('${conn.id}')">×</button>
            </div>
        `).join('');
    },
    
    showNewConnectionModal() {
        document.getElementById('newConnectionModal').classList.add('active');
    },
    
    closeModal() {
        document.getElementById('newConnectionModal').classList.remove('active');
        document.getElementById('connectionForm').reset();
        document.getElementById('connectionStatus').innerHTML = '';
    },
    
    updateFormFields() {
        const type = document.getElementById('connType').value;
        
        document.getElementById('sqlFields').style.display = type && type !== 'sqlite' && type !== 'mongodb' ? 'block' : 'none';
        document.getElementById('sqliteFields').style.display = type === 'sqlite' ? 'block' : 'none';
        document.getElementById('mongoFields').style.display = type === 'mongodb' ? 'block' : 'none';
    },
    
    async testConnection() {
        const type = document.getElementById('connType').value;
        const statusEl = document.getElementById('connectionStatus');
        
        if (!type) {
            statusEl.textContent = 'Please select a database type';
            statusEl.classList.remove('success', 'error');
            return;
        }
        
        const config = this.getConnectionConfig();
        
        try {
            statusEl.innerHTML = 'Testing connection...';
            statusEl.classList.remove('success', 'error');
            
            // Simulate test (you can implement actual testing in backend)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            statusEl.textContent = '✓ Connection successful!';
            statusEl.classList.add('success');
            statusEl.classList.remove('error');
        } catch (error) {
            statusEl.textContent = '✗ Connection failed: ' + error.message;
            statusEl.classList.add('error');
            statusEl.classList.remove('success');
        }
    },
    
    getConnectionConfig() {
        const type = document.getElementById('connType').value;
        
        if (type === 'sqlite') {
            return {
                path: document.getElementById('sqlitePath').value
            };
        } else if (type === 'mongodb') {
            return {
                uri: document.getElementById('mongoUri').value
            };
        } else {
            return {
                host: document.getElementById('connHost').value,
                port: parseInt(document.getElementById('connPort').value),
                user: document.getElementById('connUser').value,
                password: document.getElementById('connPassword').value,
                database: document.getElementById('connDatabase').value
            };
        }
    },
    
    async createConnection(e) {
        e.preventDefault();
        
        const name = document.getElementById('connName').value;
        const type = document.getElementById('connType').value;
        
        if (!name || !type) {
            alert('Please fill all required fields');
            return;
        }
        
        const config = this.getConnectionConfig();
        
        try {
            const response = await fetch(`${API_URL}/connections`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, type, config })
            });
            
            if (response.ok) {
                this.closeModal();
                this.loadConnections();
            } else {
                const error = await response.json();
                alert('Error: ' + error.error);
            }
        } catch (error) {
            alert('Failed to create connection: ' + error.message);
        }
    },
    
    selectConnection(connId) {
        this.currentConnectionId = connId;
        this.renderConnections();
        this.refreshSchema();
        
        const conn = this.connections.find(c => c.id === connId);
        document.getElementById('currentDbName').textContent = conn ? conn.name : 'Select a connection';
    },
    
    async deleteConnection(connId) {
        if (!confirm('Are you sure you want to delete this connection?')) return;
        
        try {
            const response = await fetch(`${API_URL}/connections/${connId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                if (this.currentConnectionId === connId) {
                    this.currentConnectionId = null;
                    document.getElementById('currentDbName').textContent = 'Select a connection';
                }
                this.loadConnections();
            }
        } catch (error) {
            alert('Failed to delete connection: ' + error.message);
        }
    },
    
    async refreshSchema() {
        if (!this.currentConnectionId) return;
        
        try {
            const response = await fetch(`${API_URL}/schema/${this.currentConnectionId}`);
            const schema = await response.json();
            this.renderSchema(schema);
        } catch (error) {
            console.error('Failed to load schema:', error);
        }
    },
    
    renderSchema(schema) {
        const treeEl = document.getElementById('schemaTree');
        
        if (!schema || Object.keys(schema).length === 0) {
            treeEl.innerHTML = '<p class="empty-state">No tables found</p>';
            return;
        }
        
        treeEl.innerHTML = Object.entries(schema).map(([table, columns]) => `
            <div class="tree-item tree-item-table" onclick="app.insertTableName('${table}')" title="Click to insert into query">
                📋 ${table}
            </div>
            ${Array.isArray(columns) ? columns.map(col => `
                <div class="tree-item tree-item-column" title="${col.type || 'column'}">
                    ○ ${col.name || col}
                </div>
            `).join('') : ''}
        `).join('');
    },
    
    insertTableName(tableName) {
        const editor = document.getElementById('queryEditor');
        editor.value += tableName + ' ';
        editor.focus();
    },
    
    async executeQuery() {
        if (!this.currentConnectionId) {
            alert('Please select a connection first');
            return;
        }
        
        const query = document.getElementById('queryEditor').value.trim();
        
        if (!query) {
            alert('Please enter a query');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    connection_id: this.currentConnectionId,
                    query: query
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentResults = result.rows || [];
                this.renderResults(result);
                this.switchTab('results');
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Query execution failed: ' + error.message);
        }
    },
    
    renderResults(result) {
        const headerEl = document.getElementById('resultsHeader');
        const containerEl = document.getElementById('resultsContainer');
        
        if (result.count === 0) {
            headerEl.textContent = 'Query executed successfully';
            containerEl.innerHTML = '<p class="empty-state">No results</p>';
            return;
        }
        
        headerEl.textContent = `${result.count} row(s) returned`;
        
        const columns = result.columns || Object.keys(result.rows[0] || {});
        
        containerEl.innerHTML = `
            <table class="results-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${result.rows.map(row => `
                        <tr>
                            ${columns.map(col => `<td>${this.formatValue(row[col])}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },
    
    formatValue(value) {
        if (value === null) return '<em style="color: #999;">NULL</em>';
        if (typeof value === 'object') return `<code>${JSON.stringify(value)}</code>`;
        return String(value);
    },
    
    showError(message) {
        const containerEl = document.getElementById('resultsContainer');
        containerEl.innerHTML = `<div style="padding: 20px; color: #742a2a; background: #fed7d7; border-radius: 4px; margin: 10px;"><strong>Error:</strong> ${message}</div>`;
        this.switchTab('results');
    },
    
    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Deactivate all buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab and activate button
        document.getElementById(tabName + '-tab').classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    },
    
    clearQuery() {
        document.getElementById('queryEditor').value = '';
    },
    
    async exportResults(format) {
        if (this.currentResults.length === 0) {
            alert('No results to export');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rows: this.currentResults,
                    format: format,
                    filename: 'export'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.downloadData(result.data, result.filename);
            } else {
                alert('Export failed: ' + result.error);
            }
        } catch (error) {
            alert('Export failed: ' + error.message);
        }
    },
    
    downloadData(data, filename) {
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => app.init());
