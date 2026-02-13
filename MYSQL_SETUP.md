# MySQL Setup Guide for AI Dashboard

## Quick Setup Steps

### 1. **Set Your MySQL Password**

Edit `config.py` line 14 and replace `'your_mysql_password_here'` with your actual MySQL root password:

```python
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'YOUR_ACTUAL_PASSWORD'
```

**OR** create a `.env` file in the project root:

```env
MYSQL_PASSWORD=your_actual_password
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_DB=ai_dashboard_db
```

### 2. **Create the Database**

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE ai_dashboard_db;
USE ai_dashboard_db;
SOURCE database/db.sql;
```

**OR** use command line:

```bash
mysql -u root -p < database/db.sql
```

### 3. **Restart the Flask App**

Press `Ctrl+C` to stop the current server, then run:

```bash
python app.py
```

### 4. **Access the Dashboard**

Open your browser to:
- http://localhost:5000

## Testing Without MySQL (Optional)

If you want to test the UI without MySQL first, you can:

1. Comment out the database initialization in `app.py`
2. Test file upload UI
3. Set up MySQL later

## Troubleshooting

**Error: Access Denied**
- Check your MySQL password in `config.py`
- Verify MySQL server is running

**Error: Database doesn't exist**
- Run the `database/db.sql` script to create tables

**Error: Can't connect to MySQL server**
- Ensure MySQL service is running: `net start MySQL80` (or your MySQL service name)
