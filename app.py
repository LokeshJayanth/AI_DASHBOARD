from flask import Flask, render_template, redirect, url_for, session
from config import Config
from routes.upload_routes import upload_bp
from routes.dataset_routes import dataset_bp
from routes.prompt_routes import prompt_bp
from routes.workflow_routes import workflow_bp
from routes.test_routes import test_bp
from routes.storage_routes import storage_bp
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.dashboard_view_routes import dashboard_view_bp
from services.db_service import init_db
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Session configuration for user authentication
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(dashboard_view_bp)  # No prefix, uses /dashboards from blueprint
app.register_blueprint(upload_bp, url_prefix='/upload')
app.register_blueprint(dataset_bp, url_prefix='/dataset')
app.register_blueprint(prompt_bp, url_prefix='/prompt')
app.register_blueprint(workflow_bp, url_prefix='/workflow')
app.register_blueprint(test_bp, url_prefix='/test')
app.register_blueprint(storage_bp, url_prefix='/storage')

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise show landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.user_dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/datasets')
def datasets_redirect():
    """Redirect /datasets to dashboard datasets page"""
    return redirect(url_for('dashboard.datasets_page'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
