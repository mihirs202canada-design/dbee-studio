# Dbee Studio

A modern, lightweight database management tool for developers. Connect to multiple databases, write queries, explore schemas, and visualize data—all from an intuitive interface.

## Features

- 🔗 **Multi-Database Support**: PostgreSQL, MySQL, MongoDB, SQLite
- 📝 **Query Editor**: Write and execute SQL queries with syntax highlighting
- 🗂️ **Schema Explorer**: Browse tables, columns, and relationships
- 📊 **Data Visualization**: View results in table or JSON format
- 💾 **Data Export**: Export query results to CSV, JSON, or SQL
- 🔐 **Secure Connections**: Encrypted connection strings
- ⚡ **Fast & Lightweight**: Minimal dependencies, quick startup

## Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database Drivers**: psycopg2, mysql-connector-python, pymongo, sqlite3

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend

```bash
cd frontend
# Serve the frontend (using Python's built-in server or your preferred method)
python -m http.server 8000
```

The frontend will be available at `http://localhost:8000`

## Usage

1. Open the application in your browser
2. Click "New Connection" and enter your database credentials
3. Select a connection from the sidebar
4. Use the Query Editor to write and execute queries
5. Browse your schema using the Explorer panel
6. Export results as needed

## API Endpoints

- `POST /api/connections` - Create a new connection
- `GET /api/connections` - List all connections
- `DELETE /api/connections/<id>` - Delete a connection
- `POST /api/query` - Execute a query
- `GET /api/schema/<connection_id>` - Get schema information
- `POST /api/export` - Export query results

## Docker Setup

Quick start with all databases:

```bash
docker-compose up -d
```

This starts:
- Backend on `localhost:5000`
- Frontend on `localhost:8000`
- PostgreSQL on `localhost:5432`
- MySQL on `localhost:3306`
- MongoDB on `localhost:27017`

### Database Credentials (Docker)

**PostgreSQL:**
- Host: localhost
- Port: 5432
- User: dbuser
- Password: dbpass
- Database: testdb

**MySQL:**
- Host: localhost
- Port: 3306
- User: root
- Password: rootpass
- Database: testdb

**MongoDB:**
- URI: mongodb://localhost:27017

**SQLite:**
- Path: `./data/test.db`

## Project Structure

```
dbee-studio/
├── backend/
│   ├── app.py                 # Flask application
│   ├── database_manager.py    # Database operations
│   ├── connection_manager.py  # Connection handling
│   ├── database_driver.py     # Database driver abstraction
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── index.html            # Main HTML
│   ├── styles.css            # Styling
│   └── app.js                # Frontend logic
├── docker-compose.yml        # Docker configuration
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Features in Detail

### Query Editor
- Syntax highlighting
- Execute queries with keyboard shortcut
- Clear query button
- Support for multiple query types (SELECT, INSERT, UPDATE, DELETE)

### Schema Explorer
- Browse all tables in connected database
- View column names and types
- Click to insert table names into queries

### Results Viewer
- Table format for easy viewing
- Pagination support (ready for implementation)
- NULL value highlighting
- JSON object/array formatting

### Export Options
- CSV format
- JSON format
- Ready for SQL export

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Frontend Development

Edit `frontend/app.js` and `frontend/styles.css` directly. Refresh your browser to see changes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Roadmap

- [ ] Advanced query history
- [ ] Saved queries
- [ ] Query performance analysis
- [ ] Database comparison tools
- [ ] Backup and restore functionality
- [ ] User authentication
- [ ] Real-time collaboration
- [ ] Query scheduling
- [ ] Data migration tools

## Support

For issues and questions, please open an issue on GitHub.
